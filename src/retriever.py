from __future__ import annotations

import math
import re
import statistics as stats
from typing import Any

_RETRIEVAL_CACHE: dict[str, dict[str, Any]] = {}
_RETRIEVAL_LOG: list[dict[str, Any]] = []


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def cache_key(query: str) -> str:
    return re.sub(r"\s+", " ", query.strip().lower())


def retrieval_cache_get(query: str) -> dict[str, Any] | None:
    return _RETRIEVAL_CACHE.get(cache_key(query))


def retrieval_cache_put(query: str, result: dict[str, Any]) -> None:
    _RETRIEVAL_CACHE[cache_key(query)] = result


def log_retrieval(
    query: str,
    retrieved: list[dict[str, Any]],
    *,
    keyword_hits: int = 0,
    response_time_ms: float | None = None,
) -> None:
    avg_ce = (
        sum(chunk.get("ce_score", 0.0) for chunk in retrieved) / len(retrieved)
        if retrieved
        else 0.0
    )
    top_ce = max((chunk.get("ce_score", -99.0) for chunk in retrieved), default=-99.0)
    _RETRIEVAL_LOG.append(
        {
            "query": query,
            "n_chunks": len(retrieved),
            "sections": list({chunk.get("section", "?") for chunk in retrieved}),
            "avg_ce": round(avg_ce, 4),
            "top_ce": round(top_ce, 4),
            "keyword_hits": keyword_hits,
            "response_ms": response_time_ms,
        }
    )


def compute_retrieval_stats() -> dict[str, float]:
    if not _RETRIEVAL_LOG:
        return {"recall_at_k": 0.0, "avg_ce": 0.0, "mrr_proxy": 0.0}
    recall_hits = sum(1 for row in _RETRIEVAL_LOG if row["keyword_hits"] > 0)
    avg_ce = stats.fmean(row["avg_ce"] for row in _RETRIEVAL_LOG)
    mrr_proxy = stats.fmean(1.0 / max(row["n_chunks"], 1) for row in _RETRIEVAL_LOG)
    return {
        "recall_at_k": round(recall_hits / len(_RETRIEVAL_LOG), 3),
        "avg_ce": round(avg_ce, 3),
        "mrr_proxy": round(mrr_proxy, 3),
    }


def expand_query(query: str) -> str:
    synonyms = {
        "revenue": ["sales", "top line", "net revenue"],
        "profit": ["net income", "earnings", "bottom line"],
        "margin": ["profitability", "gross margin", "operating margin"],
        "guidance": ["outlook", "forecast", "projection"],
        "risk": ["uncertainty", "exposure", "headwind"],
        "cash flow": ["fcf", "operating cash flow", "free cash flow"],
    }
    expanded = [query.strip()]
    query_l = query.lower()
    for term, variants in synonyms.items():
        if term in query_l:
            expanded.extend(variants)
    return " ".join(dict.fromkeys(token for token in expanded if token))


def guess_section(text: str) -> str:
    section_patterns = [
        (r"risk factor|litigation|regulatory|contingent", "Risk Factors"),
        (r"guidance|outlook|forecast|next quarter", "Outlook & Guidance"),
        (r"balance sheet|shareholders.{0,8}equity|book value", "Balance Sheet"),
        (r"cash flow|free cash flow|operating activities", "Cash Flow"),
        (r"revenue|ebitda|gross profit|net income", "Income Statement"),
        (r"macro|industry|market condition|sector trend", "Market & Industry"),
    ]
    sample = text[:900].lower()
    for pattern, label in section_patterns:
        if re.search(pattern, sample, re.IGNORECASE):
            return label
    return "General"


class CrossEncoderReranker:
    """Small reranker wrapper with a pure-Python fallback."""

    _neural_model = None
    _load_attempted = False

    @classmethod
    def _load_model(cls):
        if cls._load_attempted:
            return cls._neural_model
        cls._load_attempted = True
        try:
            from sentence_transformers import CrossEncoder

            cls._neural_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-2-v2")
        except Exception:
            cls._neural_model = None
        return cls._neural_model

    @classmethod
    def score_python(cls, query: str, chunks: list[str]) -> list[float]:
        query_terms = set(tokenize(query))
        if not query_terms:
            return [0.0] * len(chunks)
        scores: list[float] = []
        for chunk in chunks:
            chunk_terms = set(tokenize(chunk))
            overlap = query_terms & chunk_terms
            union = query_terms | chunk_terms
            density = len(overlap) / max(len(tokenize(chunk)), 1)
            jaccard = len(overlap) / max(len(union), 1)
            scores.append(round(jaccard + density, 6))
        return scores

    @classmethod
    def rerank(cls, query: str, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not candidates:
            return []
        chunks = [candidate["chunk"] for candidate in candidates]
        model = cls._load_model()
        if model is not None:
            try:
                pairs = [(query, chunk) for chunk in chunks]
                scores = model.predict(pairs)
            except Exception:
                scores = cls.score_python(query, chunks)
        else:
            scores = cls.score_python(query, chunks)
        enriched = []
        for candidate, score in zip(candidates, scores):
            row = dict(candidate)
            row["ce_score"] = float(score)
            enriched.append(row)
        return sorted(enriched, key=lambda row: row.get("ce_score", 0.0), reverse=True)


class HybridRetriever:
    """BM25 + TF-IDF fusion with optional reranking."""

    def __init__(self, chunks: list[str], embeddings: Any):
        self.chunks = chunks
        self.embeddings = embeddings
        self._bm25 = None
        try:
            from rank_bm25 import BM25Okapi

            self._bm25 = BM25Okapi([tokenize(chunk) for chunk in chunks])
        except Exception:
            self._bm25 = None

    def _cosine(self, a, b) -> float:
        dot = float(a @ b.T) if hasattr(a, "__matmul__") else sum(x * y for x, y in zip(a, b))
        if hasattr(dot, "A1"):
            dot = float(dot.A1[0])
        if hasattr(a, "multiply"):
            na = math.sqrt(float(a.multiply(a).sum()))
            nb = math.sqrt(float(b.multiply(b).sum()))
        else:
            na = math.sqrt(sum(x * x for x in a))
            nb = math.sqrt(sum(x * x for x in b))
        return dot / (na * nb) if na and nb else 0.0

    def retrieve(self, query: str, query_embedding, *, n: int = 8, rerank: bool = True) -> list[dict[str, Any]]:
        if not self.chunks:
            return []
        dense_scores = []
        for idx, chunk_embedding in enumerate(self.embeddings):
            try:
                score = self._cosine(query_embedding, chunk_embedding)
            except Exception:
                score = 0.0
            dense_scores.append((idx, float(score)))
        dense_rank = sorted(dense_scores, key=lambda item: item[1], reverse=True)

        bm25_rank: list[tuple[int, float]] = []
        if self._bm25 is not None:
            scores = self._bm25.get_scores(tokenize(query))
            bm25_rank = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)

        fusion: dict[int, float] = {}
        for rank, (idx, _) in enumerate(dense_rank[:30], start=1):
            fusion[idx] = fusion.get(idx, 0.0) + 1.0 / (60 + rank)
        for rank, (idx, _) in enumerate(bm25_rank[:30], start=1):
            fusion[idx] = fusion.get(idx, 0.0) + 1.0 / (60 + rank)

        candidates = [
            {"idx": idx, "chunk": self.chunks[idx], "score": score}
            for idx, score in sorted(fusion.items(), key=lambda item: item[1], reverse=True)[:30]
        ]
        if rerank:
            candidates = CrossEncoderReranker.rerank(query, candidates)
        return candidates[:n]
