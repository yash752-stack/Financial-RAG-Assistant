from __future__ import annotations

import os
from typing import Any

import pandas as pd
import streamlit as st

from .analytics import format_metric_value, render_metrics_dashboard, render_trend_chart
from .config import APP_TAGLINE, APP_TITLE, GROQ_MODEL, configure_environment, configure_page, ensure_session_defaults
from .document_parser import ingest_documents
from .llm import groq_call
from .market_data import (
    calculate_diversification,
    calculate_portfolio_beta,
    calculate_sharpe_ratio,
    calculate_var,
    fetch_multi_quotes,
    portfolio_summary,
)
from .retriever import compute_retrieval_stats, expand_query, log_retrieval, retrieval_cache_get, retrieval_cache_put

configure_environment()
configure_page()
ensure_session_defaults()


SAMPLE_PORTFOLIO: dict[str, dict[str, float]] = {
    "AAPL": {"shares": 18, "avg_cost": 182.0},
    "MSFT": {"shares": 10, "avg_cost": 401.0},
    "NVDA": {"shares": 8, "avg_cost": 876.0},
    "RELIANCE.NS": {"shares": 14, "avg_cost": 2840.0},
}

MARKET_TICKERS: list[str] = ["AAPL", "MSFT", "NVDA", "TSLA", "BTC-USD", "GC=F"]


def _safe_secret(name: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(name, os.getenv(name, default)))
    except Exception:
        return os.getenv(name, default)


def _init_demo_state() -> None:
    defaults = {
        "hosted_answers": [],
        "hosted_market_loaded": False,
        "hosted_portfolio_loaded": False,
        "hosted_api_key": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
          background:
            radial-gradient(circle at top left, rgba(67, 56, 202, 0.16), transparent 28%),
            radial-gradient(circle at bottom right, rgba(8, 145, 178, 0.16), transparent 30%),
            linear-gradient(180deg, #08111f 0%, #0b1220 100%);
        }
        [data-testid="stSidebar"] {
          background: linear-gradient(180deg, rgba(9, 15, 30, 0.98), rgba(7, 11, 22, 0.98));
          border-right: 1px solid rgba(148, 163, 184, 0.15);
        }
        .hero-card, .surface-card {
          background: rgba(10, 16, 28, 0.78);
          border: 1px solid rgba(148, 163, 184, 0.14);
          border-radius: 20px;
          box-shadow: 0 18px 60px rgba(2, 6, 23, 0.35);
        }
        .hero-card {
          padding: 1.6rem 1.6rem 1.3rem;
          margin-bottom: 1rem;
        }
        .hero-kicker {
          font-size: 0.76rem;
          letter-spacing: 0.16em;
          text-transform: uppercase;
          color: #67e8f9;
          margin-bottom: 0.5rem;
        }
        .hero-title {
          font-size: 2.4rem;
          font-weight: 700;
          line-height: 1.05;
          color: #f8fafc;
          margin: 0;
        }
        .hero-copy {
          color: #cbd5e1;
          max-width: 52rem;
          margin-top: 0.75rem;
          margin-bottom: 1rem;
          line-height: 1.65;
        }
        .pill-row {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }
        .pill {
          padding: 0.35rem 0.7rem;
          border-radius: 999px;
          border: 1px solid rgba(103, 232, 249, 0.2);
          background: rgba(8, 145, 178, 0.08);
          color: #a5f3fc;
          font-size: 0.78rem;
        }
        .tiny-note {
          color: #94a3b8;
          font-size: 0.82rem;
          line-height: 1.55;
        }
        .source-card {
          border: 1px solid rgba(148, 163, 184, 0.14);
          border-radius: 14px;
          padding: 0.85rem 0.95rem;
          background: rgba(15, 23, 42, 0.55);
          margin-bottom: 0.7rem;
        }
        .source-title {
          color: #f8fafc;
          font-weight: 600;
          margin-bottom: 0.25rem;
        }
        .source-meta {
          color: #67e8f9;
          font-size: 0.78rem;
          margin-bottom: 0.35rem;
        }
        .source-preview {
          color: #cbd5e1;
          font-size: 0.92rem;
          line-height: 1.55;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _configure_sidebar() -> str:
    with st.sidebar:
        st.markdown("## Financial RAG Assistant")
        st.caption("Hosted demo build")
        st.markdown(
            "[Open live demo](https://financial-rag-assistant.streamlit.app/)\n\n"
            "[View GitHub repo](https://github.com/yash752-stack/Financial-RAG-Assistant)"
        )
        st.markdown("---")
        st.markdown("### API")
        api_key = _safe_secret("GROQ_API_KEY") or st.session_state.get("hosted_api_key", "")
        if api_key:
            st.success("Groq key detected")
        else:
            api_key = st.text_input(
                "Groq API key",
                value="",
                type="password",
                placeholder="gsk_...",
                help="Optional for the hosted demo. Without a key, the app still shows retrieval-backed excerpts.",
            )
        st.session_state["hosted_api_key"] = api_key

        st.markdown("---")
        st.markdown("### Live demo scope")
        st.markdown(
            "- Upload reports and build a hybrid retrieval index\n"
            "- Ask grounded financial questions with citations\n"
            "- Review extracted metrics and trends\n"
            "- Load market and portfolio snapshots on demand"
        )
        if st.button("Clear demo session", use_container_width=True):
            for key in [
                "vectorstore",
                "uploaded_docs",
                "chunk_count",
                "file_names",
                "doc_full_text",
                "auto_metrics",
                "auto_generated",
                "messages",
                "hosted_answers",
                "hosted_market_loaded",
                "hosted_portfolio_loaded",
            ]:
                if key in st.session_state:
                    if key in {"uploaded_docs", "chunk_count"}:
                        st.session_state[key] = 0
                    elif key in {"file_names", "auto_metrics", "messages", "hosted_answers"}:
                        st.session_state[key] = []
                    elif key in {"auto_generated", "hosted_market_loaded", "hosted_portfolio_loaded"}:
                        st.session_state[key] = False
                    elif key == "vectorstore":
                        st.session_state[key] = None
                    else:
                        st.session_state[key] = ""
            st.rerun()
    return api_key


def _render_header() -> None:
    st.markdown(
        f"""
        <div class="hero-card">
          <div class="hero-kicker">AI-native financial intelligence</div>
          <h1 class="hero-title">{APP_TITLE}</h1>
          <div class="hero-copy">{APP_TAGLINE}</div>
          <div class="pill-row">
            <span class="pill">Streamlit hosted demo</span>
            <span class="pill">Groq {GROQ_MODEL}</span>
            <span class="pill">TF-IDF + BM25 + RRF</span>
            <span class="pill">Cited document answers</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(4)
    metric_cols[0].metric("Uploaded docs", st.session_state.get("uploaded_docs", 0))
    metric_cols[1].metric("Indexed chunks", st.session_state.get("chunk_count", 0))
    metric_cols[2].metric("Retrieval mode", "Hybrid" if st.session_state.get("vectorstore") else "Ready")
    metric_cols[3].metric("Demo status", "Live")


def _render_overview() -> None:
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("### What this demo proves")
        st.markdown(
            "- Document-grounded Q&A for 10-Ks, annual reports, CSVs, and spreadsheets\n"
            "- Hybrid retrieval using TF-IDF, BM25, and Reciprocal Rank Fusion\n"
            "- Groq-backed answer generation with source context\n"
            "- Financial metric extraction and quick analyst dashboards"
        )
        st.markdown("### Live demo flow")
        st.markdown(
            "1. Upload one or more financial documents.\n"
            "2. Ingest them into the hybrid index.\n"
            "3. Ask a question and inspect cited evidence.\n"
            "4. Open analytics or load the market and portfolio snapshots."
        )
    with right:
        st.markdown("### Hosted architecture")
        st.code(
            "Upload -> Parser + Chunking -> TF-IDF/BM25 -> RRF -> Groq -> Cited answer",
            language="text",
        )
        st.markdown(
            '<div class="surface-card" style="padding:1rem 1rem 0.85rem;">'
            '<div class="tiny-note">'
            "This hosted build is intentionally lighter than the original studio UI so the public Streamlit deployment renders quickly and reliably."
            "</div></div>",
            unsafe_allow_html=True,
        )


def _retrieve_sources(query: str, n_results: int = 5) -> tuple[str, list[dict[str, Any]]]:
    vectorstore = st.session_state.get("vectorstore")
    if not vectorstore:
        return "", []

    cached = retrieval_cache_get(query)
    if cached:
        return cached["context"], cached["sources"]

    chunks: list[str] = vectorstore.get("chunks", [])
    meta: list[dict[str, Any]] = vectorstore.get("meta", [])
    vectorizer = vectorstore.get("vectorizer")
    matrix = vectorstore.get("tfidf_matrix")
    if not chunks or vectorizer is None or matrix is None:
        return "", []

    from sklearn.metrics.pairwise import cosine_similarity

    expanded = expand_query(query)
    query_vec = vectorizer.transform([expanded])
    dense_scores = cosine_similarity(query_vec, matrix).flatten().tolist()

    try:
        from rank_bm25 import BM25Okapi

        def _tokenize(text: str) -> list[str]:
            return [token for token in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split() if token]

        bm25 = BM25Okapi([_tokenize(chunk) for chunk in chunks])
        raw_scores = bm25.get_scores(_tokenize(expanded))
        top_bm25 = max(raw_scores) if len(raw_scores) else 1.0
        bm25_scores = [score / top_bm25 if top_bm25 else 0.0 for score in raw_scores]
    except Exception:
        bm25_scores = [0.0] * len(chunks)

    dense_rank = sorted(range(len(chunks)), key=lambda idx: dense_scores[idx], reverse=True)
    bm25_rank = sorted(range(len(chunks)), key=lambda idx: bm25_scores[idx], reverse=True)

    fusion: dict[int, float] = {}
    for rank, idx in enumerate(dense_rank[:30], start=1):
        fusion[idx] = fusion.get(idx, 0.0) + 1.0 / (60 + rank)
    for rank, idx in enumerate(bm25_rank[:30], start=1):
        fusion[idx] = fusion.get(idx, 0.0) + 1.0 / (60 + rank)

    candidates: list[dict[str, Any]] = []
    hinted_section = _normalize_section_hint(query)
    for idx in sorted(fusion, key=fusion.get, reverse=True)[:20]:
        row = meta[idx]
        section = row.get("10k_item") or row.get("section") or "General"
        score = fusion[idx]
        if hinted_section and hinted_section.lower() in section.lower():
            score += 0.015
        candidates.append(
            {
                "doc_title": row.get("doc_title") or row.get("filename", "Document"),
                "filename": row.get("filename", "Document"),
                "section": section,
                "page": row.get("page", "?"),
                "preview": chunks[idx][:380],
                "score": round(score, 4),
            }
        )

    sources = sorted(candidates, key=lambda item: item["score"], reverse=True)[:n_results]
    context = "\n\n".join(
        f"[{source['doc_title']} | {source['section']} | page {source['page']}]\n{source['preview']}"
        for source in sources
    )
    retrieval_cache_put(query, {"context": context, "sources": sources})
    log_retrieval(query, sources, keyword_hits=len(sources))
    return context, sources


def _normalize_section_hint(query: str) -> str:
    q = query.lower()
    mapping = {
        "risk": "Risk",
        "cash flow": "Cash Flow",
        "balance sheet": "Balance Sheet",
        "revenue": "Income Statement",
        "eps": "Per Share",
        "margin": "Ratios",
        "guidance": "Outlook",
    }
    for token, label in mapping.items():
        if token in q:
            return label
    return ""


def _fallback_answer(query: str, sources: list[dict[str, Any]]) -> str:
    if not sources:
        return "No grounded evidence found yet. Upload a document and run ingestion first."
    lines = [
        "No Groq API key is configured, so this demo is showing the highest-confidence document excerpts instead of a generated answer.",
        "",
        f"Question: {query}",
        "",
        "Best matching evidence:",
    ]
    for index, source in enumerate(sources[:3], start=1):
        lines.append(
            f"{index}. {source['doc_title']} ({source['section']}, page {source['page']}): {source['preview']}"
        )
    return "\n".join(lines)


def _answer_question(query: str, api_key: str) -> dict[str, Any]:
    context, sources = _retrieve_sources(query)
    if not sources:
        return {
            "question": query,
            "answer": "No document context is available yet. Upload and ingest at least one file first.",
            "sources": [],
        }

    if not api_key:
        answer = _fallback_answer(query, sources)
    else:
        prompt = (
            "You are a financial analyst. Answer only from the provided document context. "
            "Quote specific figures when available and end with a brief conclusion.\n\n"
            f"Question:\n{query}\n\n"
            f"Context:\n{context}"
        )
        answer = groq_call(
            api_key,
            [{"role": "user", "content": prompt}],
            system=(
                "You are a precise financial analyst. "
                "Use only the supplied context. "
                "If the answer is not in the context, say so clearly."
            ),
            max_tokens=700,
            site_key="hosted_demo_answer",
        )
    return {"question": query, "answer": answer, "sources": sources}


def _render_document_tab(api_key: str) -> None:
    st.markdown("### Document-grounded Q&A")
    uploader = st.file_uploader(
        "Upload financial documents",
        type=["pdf", "txt", "xlsx", "xls", "csv", "docx"],
        accept_multiple_files=True,
        help="Upload 10-Ks, annual reports, transcripts, spreadsheets, or notes.",
    )
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Ingest uploaded files", use_container_width=True, disabled=not uploader):
            count = ingest_documents(uploader or [])
            st.success(f"Indexed {count} chunks across {len(uploader or [])} file(s).")
    with c2:
        if st.session_state.get("vectorstore"):
            st.info("Hybrid index ready for questions.")
        else:
            st.caption("Ingest at least one document to enable retrieval.")

    query = st.text_input(
        "Ask a financial question about the uploaded documents",
        placeholder="What was total revenue and how did it change year over year?",
    )
    if st.button("Generate grounded answer", type="primary", use_container_width=True):
        if not query.strip():
            st.warning("Enter a question first.")
        else:
            with st.spinner("Retrieving context and building answer..."):
                result = _answer_question(query, api_key)
            answers = st.session_state.get("hosted_answers", [])
            answers.insert(0, result)
            st.session_state["hosted_answers"] = answers[:6]

    answers = st.session_state.get("hosted_answers", [])
    if answers:
        st.markdown("### Recent answers")
        for item in answers:
            with st.container(border=True):
                st.markdown(f"**Question:** {item['question']}")
                st.markdown(item["answer"])
                if item["sources"]:
                    with st.expander("View citations"):
                        for source in item["sources"]:
                            st.markdown(
                                f"""
                                <div class="source-card">
                                  <div class="source-title">{source['doc_title']}</div>
                                  <div class="source-meta">{source['section']} · page {source['page']} · score {source['score']}</div>
                                  <div class="source-preview">{source['preview']}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
    else:
        st.caption("Your answers and citations will appear here.")


def _render_analytics_tab() -> None:
    st.markdown("### Metrics and extraction analytics")
    if not st.session_state.get("auto_generated") or not st.session_state.get("auto_metrics"):
        st.info("Upload and ingest a document to populate the analytics view.")
        return

    metrics = st.session_state.get("auto_metrics", [])
    render_metrics_dashboard(metrics)
    render_trend_chart(metrics, title="Extracted metric profile")

    with st.expander("View extracted metrics table"):
        df = pd.DataFrame(metrics)
        if "value" in df.columns and "unit" in df.columns:
            df["formatted_value"] = df.apply(lambda row: format_metric_value(row["value"], row["unit"]), axis=1)
        st.dataframe(df, use_container_width=True)

    stats = compute_retrieval_stats()
    stat_cols = st.columns(3)
    stat_cols[0].metric("Recall proxy", stats["recall_at_k"])
    stat_cols[1].metric("Avg rerank score", stats["avg_ce"])
    stat_cols[2].metric("MRR proxy", stats["mrr_proxy"])


def _render_market_tab() -> None:
    st.markdown("### Live market snapshot")
    st.caption("This loads on demand so the hosted demo stays fast on first render.")

    if st.button("Load live market snapshot", use_container_width=True):
        st.session_state["hosted_market_loaded"] = True

    if not st.session_state.get("hosted_market_loaded"):
        return

    with st.spinner("Fetching live quotes..."):
        quotes = fetch_multi_quotes(MARKET_TICKERS)

    if not quotes:
        st.warning("Live quotes are temporarily unavailable.")
        return

    rows = []
    for symbol in MARKET_TICKERS:
        quote = quotes.get(symbol)
        if not quote:
            continue
        rows.append(
            {
                "symbol": symbol,
                "name": quote.get("name", symbol),
                "price": quote.get("price"),
                "pct_change": quote.get("pct"),
                "currency": quote.get("currency", "USD"),
            }
        )
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    gainers = df.sort_values("pct_change", ascending=False).head(3)
    losers = df.sort_values("pct_change", ascending=True).head(3)
    left, right = st.columns(2)
    with left:
        st.markdown("#### Top movers")
        st.dataframe(gainers, use_container_width=True, hide_index=True)
    with right:
        st.markdown("#### Weakest movers")
        st.dataframe(losers, use_container_width=True, hide_index=True)


def _render_portfolio_tab() -> None:
    st.markdown("### Portfolio demo")
    st.caption("Uses a preloaded sample portfolio to demonstrate the portfolio analytics layer.")

    if st.button("Load sample portfolio analytics", use_container_width=True):
        st.session_state["hosted_portfolio_loaded"] = True

    if not st.session_state.get("hosted_portfolio_loaded"):
        return

    with st.spinner("Calculating sample portfolio analytics..."):
        summary = portfolio_summary(SAMPLE_PORTFOLIO)
        beta = calculate_portfolio_beta(summary)
        var_95 = calculate_var(summary)
        sharpe = calculate_sharpe_ratio(summary)
        diversification = calculate_diversification(summary)

    metric_cols = st.columns(4)
    metric_cols[0].metric("Portfolio value", f"${summary['total_value']:,.0f}")
    metric_cols[1].metric("P&L", f"${summary['total_pnl']:,.0f}", f"{summary['total_pnl_pct']:.2f}%")
    metric_cols[2].metric("Portfolio beta", beta)
    metric_cols[3].metric("Diversification", f"{diversification}/100")

    risk_cols = st.columns(2)
    risk_cols[0].metric("Daily VaR (95%)", f"${var_95:,.0f}")
    risk_cols[1].metric("Sharpe proxy", sharpe)

    holdings = pd.DataFrame(summary.get("holdings", []))
    if not holdings.empty:
        holdings = holdings[
            ["sym", "shares", "avg_cost", "price", "weight", "pnl", "pnl_pct", "currency"]
        ]
        st.dataframe(holdings, use_container_width=True, hide_index=True)


def main() -> None:
    _init_demo_state()
    _inject_styles()
    api_key = _configure_sidebar()
    _render_header()

    overview_tab, docs_tab, analytics_tab, markets_tab, portfolio_tab = st.tabs(
        ["Overview", "Document Q&A", "Analytics", "Markets", "Portfolio"]
    )

    with overview_tab:
        _render_overview()
    with docs_tab:
        _render_document_tab(api_key)
    with analytics_tab:
        _render_analytics_tab()
    with markets_tab:
        _render_market_tab()
    with portfolio_tab:
        _render_portfolio_tab()


if __name__ == "__main__":
    main()
