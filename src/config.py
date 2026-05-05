from __future__ import annotations

from collections.abc import Mapping

import streamlit as st
from dotenv import load_dotenv

APP_TITLE = "Financial RAG Assistant"
APP_TAGLINE = (
    "AI-native financial intelligence platform for document-grounded Q&A, "
    "market analytics, and portfolio risk insights."
)
GROQ_MODEL = "llama-3.3-70b-versatile"

DEFAULT_SESSION_STATE: tuple[tuple[str, object], ...] = (
    ("messages", []),
    ("vectorstore", None),
    ("uploaded_docs", 0),
    ("chunk_count", 0),
    ("file_names", []),
    ("show_upload", False),
    ("show_chat", False),
    ("show_portfolio", False),
    ("doc_full_text", ""),
    ("auto_metrics", []),
    ("auto_generated", False),
    ("search_query", ""),
    ("search_results", []),
    ("portfolio", {}),
    ("portfolio_notes", {}),
    ("analyst_mode", False),
    ("_chart_ai_text", ""),
    ("_chart_ai_done", False),
    ("_chart_ai_tf", "1D"),
    ("_fx_ai_text", ""),
    ("_fx_ai_done", False),
    ("_fx_ai_tf", "1D"),
    ("_comm_ai_text", ""),
    ("_comm_ai_done", False),
    ("_comm_ai_tf", "1D"),
    ("_crypto_ai_text", ""),
    ("_crypto_ai_done", False),
    ("_crypto_ai_tf", "1D"),
    ("_pf_selected_holding", ""),
    ("_pf_holding_ai", {}),
    ("price_alerts", {}),
    ("alert_log", []),
    ("app_theme", "Royal Velvet"),
    ("_groq_last_err", {}),
    ("_ce_enabled", False),
)


def configure_environment() -> None:
    load_dotenv()


def configure_page() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def ensure_session_defaults(extra_defaults: Mapping[str, object] | None = None) -> None:
    for key, value in DEFAULT_SESSION_STATE:
        if key not in st.session_state:
            st.session_state[key] = value
    if extra_defaults:
        for key, value in extra_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

