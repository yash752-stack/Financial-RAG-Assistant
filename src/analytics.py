"""
analytics.py — Financial Intelligence Engine
============================================
Features:
  1. Automated metric extraction (Revenue, EPS, Net Income, Ratios etc.)
  2. Financial taxonomy tagging (Income Statement / Cash Flow / Balance Sheet / Ratios)
  3. Hybrid BM25 + Dense retrieval with cross-encoder re-ranking
  4. Pre-built financial QA templates
  5. Visual analytics dashboard builder
  6. Benchmarking / eval harness (FinanceBench-style)

This module is intentionally Streamlit-friendly and mostly lightweight.
Optional reranking paths can use sentence-transformers when installed,
but the rest of the analytics stack works without it.
"""

from __future__ import annotations
import re, json, math
from typing import Any, Optional
import pandas as pd
import streamlit as st


# ══════════════════════════════════════════════════════════════════════════════
# 1 ─ FINANCIAL TAXONOMY
# ══════════════════════════════════════════════════════════════════════════════

TAXONOMY: dict[str, list[str]] = {
    "Income Statement": [
        "revenue", "net revenue", "total revenue", "net sales", "gross profit",
        "gross margin", "operating income", "ebit", "ebitda", "net income",
        "net profit", "earnings", "eps", "earnings per share", "diluted eps",
        "operating expense", "cost of revenue", "cost of goods sold", "cogs",
        "research and development", "r&d", "selling general administrative",
        "sg&a", "tax", "income tax", "interest expense",
    ],
    "Balance Sheet": [
        "total assets", "total liabilities", "shareholders equity", "stockholders equity",
        "book value", "cash and equivalents", "short-term investments",
        "accounts receivable", "inventory", "goodwill", "intangible assets",
        "long-term debt", "current liabilities", "current assets",
        "retained earnings", "common stock", "treasury stock",
    ],
    "Cash Flow": [
        "operating cash flow", "cash from operations", "free cash flow", "fcf",
        "capital expenditure", "capex", "investing activities",
        "financing activities", "dividends paid", "share repurchase",
        "buyback", "depreciation", "amortization",
    ],
    "Ratios & Valuation": [
        "p/e ratio", "price to earnings", "p/b ratio", "price to book",
        "roe", "return on equity", "roa", "return on assets",
        "debt to equity", "d/e ratio", "current ratio", "quick ratio",
        "gross margin", "net margin", "operating margin", "ebitda margin",
        "interest coverage", "dividend yield", "payout ratio",
        "price to sales", "ev/ebitda", "enterprise value",
    ],
    "Growth & Guidance": [
        "year over year", "yoy", "quarter over quarter", "qoq",
        "guidance", "outlook", "forecast", "projection",
        "growth rate", "cagr", "compound annual",
    ],
    "Risk Factors": [
        "risk", "uncertainty", "competition", "regulatory", "litigation",
        "geopolitical", "macroeconomic", "supply chain", "inflation",
        "interest rate risk", "credit risk", "liquidity risk", "cyber",
    ],
}


def tag_chunk(text: str) -> list[str]:
    """Return list of taxonomy categories present in a text chunk."""
    tl = text.lower()
    return [cat for cat, kws in TAXONOMY.items() if any(kw in tl for kw in kws)]


# ══════════════════════════════════════════════════════════════════════════════
# 2 ─ METRIC EXTRACTOR  (regex + heuristic, no LLM call needed)
# ══════════════════════════════════════════════════════════════════════════════

# Patterns: (label, unit_hint, regex)
_METRIC_PATTERNS: list[tuple[str, str, str]] = [
    # Revenue / Income
    ("Revenue",          "USD",  r"(?:total\s+)?(?:net\s+)?revenue[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
    ("Net Income",       "USD",  r"net\s+income[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
    ("Gross Profit",     "USD",  r"gross\s+profit[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
    ("Operating Income", "USD",  r"operating\s+income[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
    ("EBITDA",           "USD",  r"ebitda[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
    ("Free Cash Flow",   "USD",  r"free\s+cash\s+flow[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
    ("CapEx",            "USD",  r"capital\s+expenditures?[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
    # Per-share
    ("EPS (Basic)",      "USD",  r"basic\s+(?:earnings|eps)[^\n]{0,60}?\$\s*([\d,\.]+)"),
    ("EPS (Diluted)",    "USD",  r"diluted\s+(?:earnings|eps)[^\n]{0,60}?\$\s*([\d,\.]+)"),
    # Margins (%)
    ("Gross Margin",     "%",    r"gross\s+margin[^\n]{0,60}?([\d\.]+)\s*%"),
    ("Net Margin",       "%",    r"net\s+(?:profit\s+)?margin[^\n]{0,60}?([\d\.]+)\s*%"),
    ("Operating Margin", "%",    r"operating\s+margin[^\n]{0,60}?([\d\.]+)\s*%"),
    # Ratios
    ("ROE",              "%",    r"return\s+on\s+equity[^\n]{0,60}?([\d\.]+)\s*%"),
    ("ROA",              "%",    r"return\s+on\s+assets[^\n]{0,60}?([\d\.]+)\s*%"),
    ("Debt/Equity",      "x",    r"debt[- ]to[- ]equity[^\n]{0,60}?([\d\.]+)"),
    ("Current Ratio",    "x",    r"current\s+ratio[^\n]{0,60}?([\d\.]+)"),
    # Share count
    ("Shares Outstanding", "M",  r"shares?\s+outstanding[^\n]{0,60}?([\d,\.]+)\s*(million|billion|M|B)?"),
]

_SCALE = {
    "billion": 1e9, "b": 1e9,
    "million": 1e6, "m": 1e6,
    None: 1.0, "": 1.0,
}


def extract_metrics(full_text: str) -> list[dict]:
    """
    Run regex patterns over document text, return structured metric list.
    Each item: {label, value (float), unit, raw, category}
    """
    tl = full_text.lower()
    results: list[dict] = []
    seen: set[str] = set()

    for label, unit, pattern in _METRIC_PATTERNS:
        for m in re.finditer(pattern, tl, re.IGNORECASE):
            raw_num = m.group(1).replace(",", "")
            scale_key = (m.group(2) or "").lower() if m.lastindex and m.lastindex >= 2 else ""
            scale = _SCALE.get(scale_key, 1.0)
            try:
                val = float(raw_num) * scale
            except ValueError:
                continue
            if label in seen:
                continue
            seen.add(label)
            # tag category
            cat = next(
                (c for c, kws in TAXONOMY.items()
                 if any(kw in label.lower() for kw in kws)),
                "Other"
            )
            results.append({
                "label":    label,
                "value":    val,
                "unit":     unit,
                "raw":      m.group(0).strip()[:120],
                "category": _metric_category(label),
            })

    return results


def _metric_category(label: str) -> str:
    ll = label.lower()
    if any(k in ll for k in ["eps", "diluted", "basic"]):
        return "Per Share"
    if any(k in ll for k in ["margin", "roe", "roa", "ratio", "debt"]):
        return "Ratios"
    if any(k in ll for k in ["cash flow", "capex"]):
        return "Cash Flow"
    if any(k in ll for k in ["revenue", "income", "profit", "ebitda"]):
        return "Income Statement"
    return "Other"


def format_metric_value(val: float, unit: str) -> str:
    """Human-readable value formatter."""
    if unit == "USD":
        if val >= 1e9:
            return f"${val/1e9:.2f}B"
        elif val >= 1e6:
            return f"${val/1e6:.1f}M"
        elif val >= 1e3:
            return f"${val/1e3:.1f}K"
        return f"${val:.2f}"
    elif unit == "%":
        return f"{val:.1f}%"
    elif unit == "x":
        return f"{val:.2f}x"
    elif unit == "M":
        if val >= 1e9:
            return f"{val/1e9:.2f}B"
        return f"{val:.1f}M"
    return f"{val:,.2f}"


# ══════════════════════════════════════════════════════════════════════════════
# 3 ─ HYBRID RETRIEVER  (BM25 + Dense + optional cross-encoder re-ranking)
# ══════════════════════════════════════════════════════════════════════════════

def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class HybridRetriever:
    """
    Combines BM25 keyword scores with dense embedding cosine similarity.
    Falls back to dense-only if rank_bm25 is not installed.
    Optionally re-ranks top-k with a cross-encoder for precision.
    """

    def __init__(self, chunks: list[str], embeddings: list[list[float]]):
        self.chunks     = chunks
        self.embeddings = embeddings
        self._bm25      = None
        self._ce_model  = None
        self._build_bm25()

    def _build_bm25(self):
        try:
            from rank_bm25 import BM25Okapi
            tokenized = [_tokenize(c) for c in self.chunks]
            self._bm25 = BM25Okapi(tokenized)
        except ImportError:
            self._bm25 = None  # graceful degradation

    def _cosine(self, a: list[float], b: list[float]) -> float:
        dot  = sum(x * y for x, y in zip(a, b))
        na   = math.sqrt(sum(x*x for x in a))
        nb   = math.sqrt(sum(x*x for x in b))
        return dot / (na * nb + 1e-9)

    def retrieve(
        self,
        query: str,
        query_emb: list[float],
        n: int = 8,
        bm25_weight: float = 0.35,
        rerank: bool = True,
        rerank_top: int = 16,
    ) -> list[dict]:
        """
        Returns top-n chunks sorted by hybrid score.
        Each item: {idx, chunk, score, bm25, dense}
        """
        N = len(self.chunks)

        # ── Dense scores ──────────────────────────────────────────
        dense = [self._cosine(query_emb, e) for e in self.embeddings]

        # ── BM25 scores (normalised 0–1) ──────────────────────────
        if self._bm25:
            bm25_raw = self._bm25.get_scores(_tokenize(query))
            bm25_max = max(bm25_raw) or 1.0
            bm25_norm = [s / bm25_max for s in bm25_raw]
        else:
            bm25_norm = [0.0] * N

        # ── Hybrid combination ────────────────────────────────────
        alpha = bm25_weight
        hybrid = [
            (1 - alpha) * d + alpha * b
            for d, b in zip(dense, bm25_norm)
        ]

        # Sort and take top candidates for re-ranking
        ranked = sorted(range(N), key=lambda i: hybrid[i], reverse=True)
        candidates = ranked[:max(rerank_top, n)]

        # ── Cross-encoder re-ranking (optional) ──────────────────
        if rerank:
            pairs = [(query, self.chunks[i]) for i in candidates]
            ce_scores = self._cross_encode(pairs)
            if ce_scores:
                candidates = sorted(
                    candidates,
                    key=lambda i: ce_scores[candidates.index(i)],
                    reverse=True,
                )

        top = candidates[:n]
        return [
            {
                "idx":    i,
                "chunk":  self.chunks[i],
                "score":  hybrid[i],
                "bm25":   bm25_norm[i],
                "dense":  dense[i],
            }
            for i in top
        ]

    def _cross_encode(self, pairs: list[tuple[str, str]]) -> list[float]:
        """Cross-encoder re-ranking using a lightweight model."""
        try:
            from sentence_transformers import CrossEncoder
            if self._ce_model is None:
                # Small, fast cross-encoder — 22MB
                self._ce_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-2-v2")
            scores = self._ce_model.predict(pairs).tolist()
            return scores
        except Exception:
            return []


# ══════════════════════════════════════════════════════════════════════════════
# 4 ─ PRE-BUILT FINANCIAL QA TEMPLATES
# ══════════════════════════════════════════════════════════════════════════════

TEMPLATES: dict[str, dict] = {
    # ── Income Statement ──────────────────────────────────────────────────────
    "Revenue Summary": {
        "icon":     "💰",
        "category": "Income Statement",
        "prompt":   (
            "Extract and summarise the revenue figures from the document. "
            "Include: total revenue, revenue breakdown by segment/product if available, "
            "YoY growth rate, and any guidance. Present as a structured table."
        ),
    },
    "Profitability Deep-Dive": {
        "icon":     "📊",
        "category": "Income Statement",
        "prompt":   (
            "Analyse profitability in detail: gross profit & margin, operating income & margin, "
            "EBITDA, net income & net margin. Compare to prior year. Highlight any one-time items."
        ),
    },
    "EPS Analysis": {
        "icon":     "📈",
        "category": "Per Share",
        "prompt":   (
            "What is the basic and diluted EPS? How has it changed YoY and QoQ? "
            "What drove the change — revenue growth, cost reduction, share buybacks, or tax?"
        ),
    },
    # ── Balance Sheet ──────────────────────────────────────────────────────────
    "Balance Sheet Snapshot": {
        "icon":     "🏦",
        "category": "Balance Sheet",
        "prompt":   (
            "Summarise the balance sheet: total assets, liabilities, shareholders equity, "
            "cash position, debt levels. Calculate debt-to-equity and book value per share if possible."
        ),
    },
    "Liquidity Assessment": {
        "icon":     "💧",
        "category": "Balance Sheet",
        "prompt":   (
            "Assess the company's liquidity: current ratio, quick ratio, cash and equivalents, "
            "short-term debt obligations. Is the company at risk of a liquidity crunch?"
        ),
    },
    # ── Cash Flow ──────────────────────────────────────────────────────────────
    "Free Cash Flow Analysis": {
        "icon":     "🌊",
        "category": "Cash Flow",
        "prompt":   (
            "Break down the cash flow statement: operating cash flow, CapEx, free cash flow. "
            "Compare FCF to net income. What is the FCF conversion rate? How is cash being deployed?"
        ),
    },
    "Capital Allocation": {
        "icon":     "🎯",
        "category": "Cash Flow",
        "prompt":   (
            "How is the company allocating its capital? Dividends, buybacks, M&A, R&D spend, "
            "debt repayment. What % of FCF is returned to shareholders?"
        ),
    },
    # ── Ratios ─────────────────────────────────────────────────────────────────
    "Key Ratios & Benchmarks": {
        "icon":     "⚖️",
        "category": "Ratios",
        "prompt":   (
            "Calculate or extract these ratios: ROE, ROA, Gross Margin, Net Margin, "
            "Operating Margin, Debt/Equity, Current Ratio, Interest Coverage. "
            "Flag any that look concerning vs. industry norms."
        ),
    },
    # ── Risk ───────────────────────────────────────────────────────────────────
    "Risk Factor Summary": {
        "icon":     "⚠️",
        "category": "Risk Factors",
        "prompt":   (
            "List the top 5 material risk factors mentioned. For each: name, description, "
            "potential financial impact, and any mitigation strategies disclosed."
        ),
    },
    # ── Growth ─────────────────────────────────────────────────────────────────
    "Growth & Guidance": {
        "icon":     "🚀",
        "category": "Growth",
        "prompt":   (
            "What is the company's growth trajectory? Extract 3-year revenue CAGR if possible, "
            "management guidance for next quarter/year, key growth drivers and headwinds."
        ),
    },
    "Competitive Position": {
        "icon":     "🏆",
        "category": "Strategy",
        "prompt":   (
            "Summarise the competitive moat, market share, key differentiators, and strategic "
            "priorities mentioned. What risks could erode this position?"
        ),
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# 5 ─ ANALYTICS DASHBOARD BUILDER
# ══════════════════════════════════════════════════════════════════════════════

VELVET = {
    "bg":        "#07060C",
    "card":      "#0D0B12",
    "card2":     "#120E1A",
    "border":    "rgba(139,58,139,0.25)",
    "accent":    "#C084C8",
    "green":     "#4ade80",
    "red":       "#f87171",
    "gold":      "#F0C040",
    "text":      "#EDE8F5",
    "dim":       "#9A8AAA",
    "ghost":     "#4A3858",
}

CATEGORY_COLORS: dict[str, str] = {
    "Income Statement": "#C084C8",
    "Balance Sheet":    "#60a5fa",
    "Cash Flow":        "#4ade80",
    "Ratios":           "#F0C040",
    "Per Share":        "#fb923c",
    "Growth":           "#34d399",
    "Risk Factors":     "#f87171",
    "Other":            "#9A8AAA",
}


def render_metric_card(label: str, value: str, delta: Optional[str] = None,
                       category: str = "Other") -> str:
    color    = CATEGORY_COLORS.get(category, VELVET["dim"])
    delta_html = ""
    if delta:
        is_pos = delta.startswith("+") or (not delta.startswith("-"))
        dc     = VELVET["green"] if is_pos else VELVET["red"]
        delta_html = (
            f'<div style="font-family:Space Mono,monospace;font-size:0.58rem;'
            f'color:{dc};margin-top:0.15rem;">{delta}</div>'
        )
    return f"""
<div style="background:{VELVET['card2']};border:1px solid {VELVET['border']};
            border-top:2px solid {color};border-radius:10px;
            padding:0.8rem 1rem;position:relative;transition:all 0.2s;">
  <div style="font-family:Space Mono,monospace;font-size:0.52rem;letter-spacing:0.15em;
              text-transform:uppercase;color:{VELVET['ghost']};margin-bottom:0.35rem;">
    {label}
  </div>
  <div style="font-family:'Cormorant Garamond',serif;font-size:1.6rem;font-weight:300;
              color:{VELVET['text']};line-height:1;">
    {value}
  </div>
  {delta_html}
  <div style="font-family:Space Mono,monospace;font-size:0.46rem;color:{color};
              margin-top:0.3rem;text-transform:uppercase;letter-spacing:0.1em;">
    {category}
  </div>
</div>"""


def render_metrics_dashboard(metrics: list[dict]) -> None:
    """Render extracted metrics as a dashboard in the current Streamlit context."""
    if not metrics:
        st.info("No financial metrics extracted from the documents. Upload a PDF with financial tables.")
        return

    # Group by category
    by_cat: dict[str, list[dict]] = {}
    for m in metrics:
        by_cat.setdefault(m["category"], []).append(m)

    category_order = ["Income Statement", "Per Share", "Cash Flow", "Ratios", "Balance Sheet", "Other"]

    for cat in category_order:
        items = by_cat.get(cat, [])
        if not items:
            continue

        color = CATEGORY_COLORS.get(cat, VELVET["dim"])
        st.markdown(
            f'<div style="font-family:Space Mono,monospace;font-size:0.56rem;'
            f'letter-spacing:0.2em;text-transform:uppercase;color:{color};'
            f'margin:1rem 0 0.5rem;padding-bottom:0.3rem;'
            f'border-bottom:1px solid rgba(139,58,139,0.2);">{cat}</div>',
            unsafe_allow_html=True,
        )

        cols = st.columns(min(len(items), 4))
        for i, m in enumerate(items):
            with cols[i % 4]:
                val_str = format_metric_value(m["value"], m["unit"])
                st.markdown(
                    render_metric_card(m["label"], val_str, category=cat),
                    unsafe_allow_html=True,
                )


def render_trend_chart(metrics: list[dict], title: str = "Extracted Metrics") -> None:
    """Bar chart of all USD metrics for quick visual comparison."""
    usd_metrics = [m for m in metrics if m["unit"] == "USD" and m["value"] > 0]
    pct_metrics = [m for m in metrics if m["unit"] == "%"]
    ratio_metrics = [m for m in metrics if m["unit"] == "x"]

    if usd_metrics:
        df = pd.DataFrame(usd_metrics).set_index("label")["value"]
        df_display = df / 1e9  # convert to billions for display
        st.markdown(
            '<div style="font-family:Space Mono,monospace;font-size:0.54rem;'
            'letter-spacing:0.15em;text-transform:uppercase;color:#C084C8;'
            'margin:0.8rem 0 0.3rem;">USD Metrics (Billions $)</div>',
            unsafe_allow_html=True,
        )
        st.bar_chart(df_display, height=180, use_container_width=True)

    if pct_metrics:
        df_pct = pd.DataFrame(pct_metrics).set_index("label")["value"]
        st.markdown(
            '<div style="font-family:Space Mono,monospace;font-size:0.54rem;'
            'letter-spacing:0.15em;text-transform:uppercase;color:#F0C040;'
            'margin:0.8rem 0 0.3rem;">% Metrics (Margins & Returns)</div>',
            unsafe_allow_html=True,
        )
        st.bar_chart(df_pct, height=150, use_container_width=True)

    if ratio_metrics:
        df_ratio = pd.DataFrame(ratio_metrics).set_index("label")["value"]
        st.markdown(
            '<div style="font-family:Space Mono,monospace;font-size:0.54rem;'
            'letter-spacing:0.15em;text-transform:uppercase;color:#4ade80;'
            'margin:0.8rem 0 0.3rem;">Ratio Metrics (×)</div>',
            unsafe_allow_html=True,
        )
        st.bar_chart(df_ratio, height=150, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# 6 ─ BENCHMARK / EVAL HARNESS
# ══════════════════════════════════════════════════════════════════════════════

# A small FinanceBench-inspired test set for QA accuracy evaluation
EVAL_QUESTIONS: list[dict] = [
    {
        "id":       "fb_001",
        "question": "What was total revenue?",
        "expected_keywords": ["revenue", "billion", "million", "$"],
        "category": "Income Statement",
    },
    {
        "id":       "fb_002",
        "question": "What was diluted EPS?",
        "expected_keywords": ["eps", "diluted", "$", "per share"],
        "category": "Per Share",
    },
    {
        "id":       "fb_003",
        "question": "What was the gross margin?",
        "expected_keywords": ["gross margin", "%", "percent"],
        "category": "Ratios",
    },
    {
        "id":       "fb_004",
        "question": "What was free cash flow?",
        "expected_keywords": ["free cash flow", "operating", "capex", "capital expenditure"],
        "category": "Cash Flow",
    },
    {
        "id":       "fb_005",
        "question": "What are the main risk factors?",
        "expected_keywords": ["risk", "competition", "regulatory", "uncertainty"],
        "category": "Risk Factors",
    },
    {
        "id":       "fb_006",
        "question": "What is the company's revenue guidance?",
        "expected_keywords": ["guidance", "outlook", "forecast", "expect", "anticipate"],
        "category": "Growth",
    },
    {
        "id":       "fb_007",
        "question": "What is the debt-to-equity ratio?",
        "expected_keywords": ["debt", "equity", "ratio", "leverage"],
        "category": "Ratios",
    },
    {
        "id":       "fb_008",
        "question": "How much did the company spend on R&D?",
        "expected_keywords": ["research", "development", "r&d", "billion", "million"],
        "category": "Income Statement",
    },
]


def score_answer(answer: str, expected_keywords: list[str]) -> dict:
    """
    Simple keyword-coverage recall metric.
    Returns: {recall, hits, total, score_pct}
    """
    al = answer.lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in al)
    recall = hits / len(expected_keywords) if expected_keywords else 0.0
    return {
        "recall":    recall,
        "hits":      hits,
        "total":     len(expected_keywords),
        "score_pct": round(recall * 100, 1),
    }


def render_eval_dashboard(results: list[dict]) -> None:
    """Render benchmark results as a mini dashboard."""
    if not results:
        return

    avg_score = sum(r["score"]["score_pct"] for r in results) / len(results)
    color = VELVET["green"] if avg_score >= 70 else (VELVET["gold"] if avg_score >= 40 else VELVET["red"])

    st.markdown(
        f'<div style="background:{VELVET["card2"]};border:1px solid {VELVET["border"]};'
        f'border-radius:10px;padding:1rem 1.2rem;margin-bottom:1rem;">'
        f'<div style="font-family:Space Mono,monospace;font-size:0.54rem;'
        f'letter-spacing:0.15em;text-transform:uppercase;color:{VELVET["ghost"]};">Overall Recall Score</div>'
        f'<div style="font-family:Cormorant Garamond,serif;font-size:2.2rem;'
        f'font-weight:300;color:{color};">{avg_score:.1f}%</div>'
        f'<div style="font-family:Space Mono,monospace;font-size:0.5rem;color:{VELVET["ghost"]};">'
        f'{len(results)} questions evaluated</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    rows = []
    for r in results:
        sc = r["score"]
        rows.append({
            "Question":  r["question"][:60] + ("…" if len(r["question"]) > 60 else ""),
            "Category":  r.get("category", "—"),
            "Score":     f"{sc['score_pct']}%",
            "Hits":      f"{sc['hits']}/{sc['total']}",
        })
    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 7 ─ STREAMLIT ANALYTICS TAB  (call this from app.py)
# ══════════════════════════════════════════════════════════════════════════════

def render_analytics_tab(
    vectorstore: Optional[dict],
    groq_api_key: str,
    doc_full_text: str = "",
) -> None:
    """
    Full analytics UI. Pass the vectorstore dict from session state,
    the Groq API key, and the concatenated full text of ingested docs.
    """
    if not vectorstore and not doc_full_text:
        st.markdown("""
        <div style="text-align:center;padding:3rem 2rem;">
          <div style="font-size:2.5rem;margin-bottom:1rem;opacity:0.4;">📊</div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.5rem;
                      font-weight:300;font-style:italic;color:#4A3858;">
            Upload documents to unlock analytics
          </div>
          <div style="font-family:Syne,sans-serif;font-size:0.8rem;color:#4A3858;
                      margin-top:0.6rem;max-width:380px;margin-left:auto;margin-right:auto;">
            Auto-extract revenue, EPS, margins, ratios · Trend charts ·
            Pre-built templates · Benchmark evaluation
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Tab strip ─────────────────────────────────────────────────
    sub_tab_names = [
        "📊 Metrics Dashboard",
        "📋 Templates",
        "🔍 Hybrid Search",
        "🧪 Eval Benchmark",
    ]
    sub_tabs = st.tabs(sub_tab_names)

    # ── TAB 1: Metrics Dashboard ───────────────────────────────────
    with sub_tabs[0]:
        st.markdown(
            '<div style="font-family:Space Mono,monospace;font-size:0.54rem;'
            'letter-spacing:0.18em;text-transform:uppercase;color:#C084C8;margin-bottom:0.8rem;">'
            'Auto-Extracted Financial Metrics</div>',
            unsafe_allow_html=True,
        )
        if doc_full_text:
            with st.spinner("Extracting metrics…"):
                metrics = extract_metrics(doc_full_text)

            if metrics:
                render_metrics_dashboard(metrics)
                st.markdown("<hr style='border-color:rgba(139,58,139,0.15);margin:1rem 0;'>", unsafe_allow_html=True)
                render_trend_chart(metrics)

                with st.expander("📄 Raw extraction table"):
                    rows = [
                        {
                            "Metric":   m["label"],
                            "Value":    format_metric_value(m["value"], m["unit"]),
                            "Unit":     m["unit"],
                            "Category": m["category"],
                            "Raw Text": m["raw"],
                        }
                        for m in metrics
                    ]
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.info(
                    "No metrics matched regex patterns. This can happen with scanned PDFs "
                    "or non-standard formatting. Try the Templates tab for LLM extraction."
                )
        else:
            st.info("Full document text not available. Re-ingest documents.")

    # ── TAB 2: Templates ───────────────────────────────────────────
    with sub_tabs[1]:
        cats = sorted({v["category"] for v in TEMPLATES.values()})
        chosen_cat = st.selectbox(
            "Filter by category",
            ["All"] + cats,
            label_visibility="collapsed",
        )

        visible = {
            k: v for k, v in TEMPLATES.items()
            if chosen_cat == "All" or v["category"] == chosen_cat
        }

        n_cols = 3
        items  = list(visible.items())
        for row_start in range(0, len(items), n_cols):
            cols = st.columns(n_cols)
            for col_i, (tname, tmeta) in enumerate(items[row_start:row_start + n_cols]):
                with cols[col_i]:
                    color = CATEGORY_COLORS.get(tmeta["category"], VELVET["dim"])
                    st.markdown(
                        f'<div style="background:{VELVET["card2"]};border:1px solid rgba(139,58,139,0.22);'
                        f'border-top:2px solid {color};border-radius:10px;padding:0.8rem 0.9rem 0.6rem;">'
                        f'<div style="font-size:1.2rem;">{tmeta["icon"]}</div>'
                        f'<div style="font-family:Syne,sans-serif;font-size:0.82rem;font-weight:600;'
                        f'color:{VELVET["text"]};margin:0.3rem 0 0.2rem;">{tname}</div>'
                        f'<div style="font-family:Space Mono,monospace;font-size:0.52rem;'
                        f'color:{color};text-transform:uppercase;letter-spacing:0.1em;">{tmeta["category"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button(
                        "Run Analysis →",
                        key=f"tpl_{tname[:20]}",
                        use_container_width=True,
                    ):
                        st.session_state["_prefill"] = tmeta["prompt"]
                        st.success(f"✓ '{tname}' sent to chat ↓")

        st.markdown(
            '<div style="font-family:Space Mono,monospace;font-size:0.5rem;color:#4A3858;'
            'margin-top:1rem;">Templates inject the prompt into the chat — scroll down to see the answer.</div>',
            unsafe_allow_html=True,
        )

    # ── TAB 3: Hybrid Search ───────────────────────────────────────
    with sub_tabs[2]:
        st.markdown(
            '<div style="font-family:Space Mono,monospace;font-size:0.54rem;'
            'letter-spacing:0.18em;text-transform:uppercase;color:#C084C8;margin-bottom:0.8rem;">'
            'Hybrid BM25 + Dense Retrieval with Cross-Encoder Re-ranking</div>',
            unsafe_allow_html=True,
        )

        hs_q = st.text_input(
            "Search query",
            placeholder="e.g. free cash flow capital expenditure 2023",
            label_visibility="collapsed",
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            bm25_w  = st.slider("BM25 weight", 0.0, 1.0, 0.35, 0.05,
                                help="0 = dense only, 1 = keyword only")
        with c2:
            top_n   = st.slider("Results", 3, 10, 5)
        with c3:
            use_ce  = st.checkbox("Cross-encoder re-rank", value=True,
                                  help="Slower but more precise — uses ms-marco-MiniLM")

        # Taxonomy filter
        tax_filter = st.multiselect(
            "Filter by taxonomy",
            list(TAXONOMY.keys()),
            default=[],
            label_visibility="collapsed",
        )

        if hs_q and vectorstore:
            with st.spinner("Retrieving…"):
                try:
                    vs      = vectorstore
                    model   = vs["model"]
                    col     = vs["collection"]

                    # Get all chunks + embeddings from ChromaDB
                    all_res = col.get(include=["documents", "embeddings", "metadatas"])
                    chunks  = all_res["documents"]
                    embeds  = all_res["embeddings"]
                    metas   = all_res["metadatas"]

                    # Apply taxonomy filter
                    if tax_filter:
                        filtered_idx = [
                            i for i, c in enumerate(chunks)
                            if any(tcat in tag_chunk(c) for tcat in tax_filter)
                        ]
                        chunks  = [chunks[i]  for i in filtered_idx]
                        embeds  = [embeds[i]  for i in filtered_idx]
                        metas   = [metas[i]   for i in filtered_idx]

                    if not chunks:
                        st.warning("No chunks match the selected taxonomy filters.")
                    else:
                        q_emb = model.encode([hs_q], normalize_embeddings=True).tolist()[0]
                        hr    = HybridRetriever(chunks, embeds)
                        hits  = hr.retrieve(hs_q, q_emb, n=top_n,
                                            bm25_weight=bm25_w, rerank=use_ce)

                        for rank, h in enumerate(hits, 1):
                            meta = metas[h["idx"]] if h["idx"] < len(metas) else {}
                            tags = tag_chunk(h["chunk"])
                            tag_html = " ".join(
                                f'<span style="background:rgba(139,58,139,0.15);'
                                f'border:1px solid rgba(139,58,139,0.3);'
                                f'font-family:Space Mono,monospace;font-size:0.5rem;'
                                f'padding:0.1rem 0.35rem;border-radius:3px;'
                                f'color:{CATEGORY_COLORS.get(t, VELVET["dim"])};">'
                                f'{t}</span>'
                                for t in tags
                            )
                            fname = meta.get("filename", "—")
                            st.markdown(
                                f'<div style="background:{VELVET["card"]};'
                                f'border:1px solid rgba(139,58,139,0.22);'
                                f'border-left:3px solid #C084C8;border-radius:0 8px 8px 0;'
                                f'padding:0.7rem 0.9rem;margin-bottom:0.5rem;">'
                                f'<div style="display:flex;justify-content:space-between;'
                                f'align-items:center;margin-bottom:0.35rem;">'
                                f'<div style="font-family:Space Mono,monospace;font-size:0.58rem;'
                                f'color:#C084C8;">#{rank} · 📄 {fname}</div>'
                                f'<div style="font-family:Space Mono,monospace;font-size:0.52rem;'
                                f'color:#4A3858;">hybrid:{h["score"]:.3f} '
                                f'dense:{h["dense"]:.3f} bm25:{h["bm25"]:.3f}</div>'
                                f'</div>'
                                f'<div style="font-size:0.8rem;color:#9A8AAA;line-height:1.55;">'
                                f'{h["chunk"][:320]}…</div>'
                                f'<div style="margin-top:0.4rem;display:flex;gap:0.3rem;flex-wrap:wrap;">'
                                f'{tag_html}</div>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
                except Exception as e:
                    st.error(f"Search error: {e}")
        elif hs_q and not vectorstore:
            st.info("Upload and ingest documents first.")

    # ── TAB 4: Eval Benchmark ──────────────────────────────────────
    with sub_tabs[3]:
        st.markdown(
            '<div style="font-family:Space Mono,monospace;font-size:0.54rem;'
            'letter-spacing:0.18em;text-transform:uppercase;color:#C084C8;margin-bottom:0.8rem;">'
            'FinanceBench-Style QA Accuracy Evaluation</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-family:Syne,sans-serif;font-size:0.8rem;color:#4A3858;'
            'margin-bottom:1rem;line-height:1.7;">'
            'Runs 8 standard financial QA prompts against your documents and measures '
            'keyword-recall accuracy. Useful for benchmarking retrieval quality.</div>',
            unsafe_allow_html=True,
        )

        if st.button("▶  Run Benchmark", use_container_width=False):
            if not vectorstore or not groq_api_key:
                st.error("Need both documents and API key.")
            else:
                eval_results = []
                prog = st.progress(0, text="Evaluating…")
                for i, eq in enumerate(EVAL_QUESTIONS):
                    try:
                        from openai import OpenAI
                        oai   = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
                        vs    = vectorstore
                        q_emb = vs["model"].encode([eq["question"]], normalize_embeddings=True).tolist()
                        res   = vs["collection"].query(
                            query_embeddings=q_emb, n_results=4,
                            include=["documents", "metadatas", "distances"],
                        )
                        ctx  = "\n---\n".join(res["documents"][0])
                        resp = oai.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {"role": "system", "content": "Answer the financial question using only the provided context. Be concise."},
                                {"role": "user",   "content": f"Context:\n{ctx}\n\nQuestion: {eq['question']}"},
                            ],
                            temperature=0.05, max_tokens=400,
                        )
                        answer = resp.choices[0].message.content
                        sc     = score_answer(answer, eq["expected_keywords"])
                        eval_results.append({
                            "question": eq["question"],
                            "category": eq["category"],
                            "answer":   answer,
                            "score":    sc,
                        })
                    except Exception as exc:
                        eval_results.append({
                            "question": eq["question"],
                            "category": eq["category"],
                            "answer":   f"Error: {exc}",
                            "score":    {"recall": 0, "hits": 0, "total": 0, "score_pct": 0},
                        })
                    prog.progress((i + 1) / len(EVAL_QUESTIONS), text=f"Q{i+1}/{len(EVAL_QUESTIONS)}: {eq['question'][:40]}…")

                prog.empty()
                render_eval_dashboard(eval_results)

                with st.expander("📋 Full answers"):
                    for r in eval_results:
                        st.markdown(
                            f'<div style="background:{VELVET["card2"]};'
                            f'border:1px solid rgba(139,58,139,0.2);border-radius:8px;'
                            f'padding:0.7rem 0.9rem;margin-bottom:0.5rem;">'
                            f'<div style="font-family:Space Mono,monospace;font-size:0.58rem;'
                            f'color:#C084C8;margin-bottom:0.3rem;">{r["question"]}</div>'
                            f'<div style="font-size:0.8rem;color:#9A8AAA;">{r["answer"][:500]}</div>'
                            f'<div style="font-family:Space Mono,monospace;font-size:0.52rem;'
                            f'color:#4A3858;margin-top:0.3rem;">score: {r["score"]["score_pct"]}% '
                            f'· {r["score"]["hits"]}/{r["score"]["total"]} keywords hit</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
