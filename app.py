"""
app.py
======
Streamlit web interface for the Financial RAG Assistant.
Run with: streamlit run app.py
"""

import os
import sys
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
load_dotenv()

st.set_page_config(
    page_title="Financial RAG Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=JetBrains+Mono:wght@300;400;500&family=Instrument+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #080b0f !important;
    color: #e8e0d0 !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(212,175,55,0.04) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(212,175,55,0.03) 0%, transparent 60%),
        #080b0f !important;
}

[data-testid="stSidebar"] {
    background: #070a0d !important;
    border-right: 1px solid rgba(212,175,55,0.15) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

h1, h2, h3 { font-family: 'DM Serif Display', serif !important; }
p, li, span, label, div { font-family: 'Instrument Sans', sans-serif !important; }
code, pre { font-family: 'JetBrains Mono', monospace !important; }

.hero {
    position: relative;
    padding: 3rem 2rem 2.5rem;
    margin-bottom: 2rem;
    overflow: hidden;
    border-bottom: 1px solid rgba(212,175,55,0.2);
}
.hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        linear-gradient(135deg, rgba(212,175,55,0.06) 0%, transparent 50%),
        repeating-linear-gradient(90deg, transparent, transparent 80px, rgba(212,175,55,0.02) 80px, rgba(212,175,55,0.02) 81px),
        repeating-linear-gradient(0deg, transparent, transparent 80px, rgba(212,175,55,0.02) 80px, rgba(212,175,55,0.02) 81px);
    pointer-events: none;
}
.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem;
    font-weight: 400;
    letter-spacing: 0.25em;
    color: #d4af37;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
    opacity: 0.8;
}
.hero-title {
    font-family: 'DM Serif Display', serif !important;
    font-size: 3rem;
    font-weight: 400;
    color: #f0e8d8;
    margin: 0 0 0.5rem;
    line-height: 1.1;
}
.hero-title span {
    font-family: 'DM Serif Display', serif !important;
    font-style: italic;
    color: #d4af37;
}
.hero-sub {
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.95rem;
    color: #6a6058;
    font-weight: 300;
    margin: 0 0 1rem;
}
.hero-tag {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.62rem;
    letter-spacing: 0.15em;
    color: #d4af37;
    border: 1px solid rgba(212,175,55,0.3);
    padding: 0.2rem 0.6rem;
    border-radius: 2px;
    margin-right: 0.4rem;
}

.stat-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: rgba(212,175,55,0.08);
    border: 1px solid rgba(212,175,55,0.08);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 2rem;
}
.stat-card {
    background: #0d1117;
    padding: 1.2rem 1.5rem;
}
.stat-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.58rem;
    letter-spacing: 0.2em;
    color: #3a3530;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.stat-value {
    font-family: 'DM Serif Display', serif !important;
    font-size: 1.6rem;
    color: #e8e0d0;
    line-height: 1;
}
.stat-value.gold { color: #d4af37; }
.stat-mono {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem;
    color: #d4af37;
    line-height: 1;
}

.msg-user {
    display: flex;
    justify-content: flex-end;
    margin: 1.5rem 0;
}
.msg-user-bubble {
    max-width: 65%;
    background: linear-gradient(135deg, #15120a, #1e1a0f);
    border: 1px solid rgba(212,175,55,0.2);
    border-radius: 16px 16px 4px 16px;
    padding: 1rem 1.25rem;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.95rem;
    color: #e8e0d0;
    line-height: 1.6;
}
.msg-assistant {
    display: flex;
    justify-content: flex-start;
    margin: 1.5rem 0;
    gap: 0.75rem;
    align-items: flex-start;
}
.msg-avatar {
    width: 30px;
    height: 30px;
    background: linear-gradient(135deg, #d4af37, #a8891f);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.65rem;
    flex-shrink: 0;
    margin-top: 4px;
    font-family: 'JetBrains Mono', monospace !important;
    color: #080b0f;
    font-weight: 600;
    letter-spacing: 0;
}
.msg-assistant-bubble {
    max-width: 80%;
    background: #0d1117;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 4px 16px 16px 16px;
    padding: 1.2rem 1.5rem;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.95rem;
    color: #c0b8a8;
    line-height: 1.75;
}
.msg-meta {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.58rem;
    color: #2a2520;
    letter-spacing: 0.12em;
    margin-top: 0.5rem;
    text-transform: uppercase;
}

.source-item {
    background: #0a0e12;
    border: 1px solid rgba(212,175,55,0.08);
    border-left: 2px solid #d4af37;
    padding: 0.8rem 1rem;
    border-radius: 0 4px 4px 0;
    margin-bottom: 0.5rem;
}
.source-filename {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem;
    color: #d4af37;
    margin-bottom: 0.25rem;
}
.source-score {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.62rem;
    color: #3a3530;
    float: right;
    background: rgba(212,175,55,0.06);
    padding: 0.1rem 0.35rem;
    border-radius: 2px;
}
.source-preview {
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.78rem;
    color: #5a5248;
    line-height: 1.5;
    margin-top: 0.25rem;
    clear: both;
}

.empty-state {
    text-align: center;
    padding: 5rem 2rem;
    border: 1px dashed rgba(212,175,55,0.1);
    border-radius: 6px;
    margin: 1rem 0;
}
.empty-icon {
    font-size: 2.5rem;
    margin-bottom: 1.25rem;
    opacity: 0.25;
    color: #d4af37;
}
.empty-title {
    font-family: 'DM Serif Display', serif !important;
    font-size: 1.4rem;
    color: #3a3530;
    margin-bottom: 0.5rem;
}
.empty-sub {
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.82rem;
    color: #2a2520;
    max-width: 380px;
    margin: 0 auto;
    line-height: 1.7;
}

.sidebar-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.58rem;
    letter-spacing: 0.25em;
    color: #d4af37;
    text-transform: uppercase;
    margin: 1.5rem 0 0.6rem;
    padding-bottom: 0.35rem;
    border-bottom: 1px solid rgba(212,175,55,0.12);
}
.api-badge {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    background: rgba(34,197,94,0.07);
    border: 1px solid rgba(34,197,94,0.18);
    color: #4ade80;
    padding: 0.4rem 0.8rem;
    border-radius: 3px;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    width: 100%;
}
.doc-chip {
    display: block;
    background: rgba(212,175,55,0.04);
    border: 1px solid rgba(212,175,55,0.1);
    padding: 0.35rem 0.7rem;
    border-radius: 3px;
    margin-bottom: 0.35rem;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem;
    color: #7a7060;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.stButton button {
    background: transparent !important;
    border: 1px solid rgba(212,175,55,0.15) !important;
    color: #7a7060 !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.78rem !important;
    border-radius: 3px !important;
    transition: all 0.2s !important;
    text-align: left !important;
}
.stButton button:hover {
    background: rgba(212,175,55,0.06) !important;
    border-color: rgba(212,175,55,0.35) !important;
    color: #d4af37 !important;
}

[data-testid="stFileUploader"] {
    background: rgba(212,175,55,0.02) !important;
}

.stTextInput input {
    background: #0d1117 !important;
    border: 1px solid rgba(212,175,55,0.15) !important;
    border-radius: 3px !important;
    color: #e8e0d0 !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.85rem !important;
}

[data-testid="stChatInput"] > div {
    background: #0d1117 !important;
    border: 1px solid rgba(212,175,55,0.2) !important;
    border-radius: 6px !important;
}

.streamlit-expanderHeader {
    background: #0d1117 !important;
    border: 1px solid rgba(212,175,55,0.08) !important;
    border-radius: 3px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.08em !important;
    color: #4a4440 !important;
}

hr { border-color: rgba(212,175,55,0.08) !important; }

[data-testid="stMetric"] {
    background: #0d1117 !important;
    border: 1px solid rgba(255,255,255,0.03) !important;
    padding: 0.7rem 1rem !important;
    border-radius: 3px !important;
}
[data-testid="stMetricLabel"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.15em !important;
    color: #3a3530 !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    font-family: 'DM Serif Display', serif !important;
    color: #d4af37 !important;
}

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(212,175,55,0.15); border-radius: 2px; }

.footer {
    text-align: center;
    padding: 2rem 0 0.5rem;
    margin-top: 3rem;
    border-top: 1px solid rgba(212,175,55,0.06);
}
.footer-text {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    color: #1e1c18;
    text-transform: uppercase;
}

[data-testid="stChatMessage"] { background: transparent !important; border: none !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "docs_ingested" not in st.session_state:
    st.session_state.docs_ingested = False
if "store_stats" not in st.session_state:
    st.session_state.store_stats = {}


@st.cache_resource
def get_pipeline():
    from rag_pipeline import FinancialRAGPipeline
    from vector_store import FinancialVectorStore
    store = FinancialVectorStore(
        persist_directory="./data/chroma_db",
        embedding_model="all-MiniLM-L6-v2"
    )
    pipeline = FinancialRAGPipeline(
        vector_store=store,
        model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
        top_k=int(os.getenv("TOP_K_RESULTS", 5)),
        temperature=0.1
    )
    return pipeline


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.5rem 0 0.5rem;">
        <div style="font-family:'DM Serif Display',serif;font-size:1.25rem;color:#e8e0d0;">
            RAG <span style="color:#d4af37;font-style:italic;">Assistant</span>
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;
                    letter-spacing:0.22em;color:#2a2520;text-transform:uppercase;margin-top:0.2rem;">
            Financial Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">API Key</div>', unsafe_allow_html=True)
    api_key = st.text_input("", type="password",
                            value=os.getenv("OPENAI_API_KEY", ""),
                            placeholder="sk-...",
                            label_visibility="collapsed")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        st.markdown('<div class="api-badge">● KEY ACTIVE</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Documents</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("", type=["pdf", "txt"],
                                      accept_multiple_files=True,
                                      label_visibility="collapsed")

    if uploaded_files:
        if st.button("↑  Ingest Documents", use_container_width=True):
            os.makedirs("data/docs", exist_ok=True)
            prog = st.progress(0)
            for i, uf in enumerate(uploaded_files):
                with open(f"data/docs/{uf.name}", "wb") as f:
                    f.write(uf.getbuffer())
                prog.progress((i + 1) / len(uploaded_files))
            with st.spinner("Embedding..."):
                try:
                    pipeline = get_pipeline()
                    count = pipeline.ingest_documents("data/docs")
                    st.session_state.docs_ingested = True
                    st.session_state.store_stats = pipeline.vector_store.get_store_stats()
                    st.success(f"✓ {count} chunks indexed")
                except Exception as e:
                    st.error(str(e))

    if st.session_state.store_stats:
        stats = st.session_state.store_stats
        st.markdown('<div class="sidebar-label">Knowledge Base</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Chunks", stats.get("total_chunks", 0))
        c2.metric("Docs", stats.get("unique_documents", 0))
        for src in stats.get("sources", []):
            short = src[:26] + "…" if len(src) > 26 else src
            st.markdown(f'<div class="doc-chip">📄 {short}</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Quick Ask</div>', unsafe_allow_html=True)
    samples = [
        "What was the total revenue?",
        "Main risk factors?",
        "EPS change YoY?",
        "Company debt situation?",
        "Key business highlights",
    ]
    for q in samples:
        if st.button(q, use_container_width=True, key=f"s_{q[:15]}"):
            st.session_state.prefill_question = q

    st.markdown('<div class="sidebar-label">Actions</div>', unsafe_allow_html=True)
    if st.button("✕  Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">▸ Financial Intelligence Platform</div>
    <h1 class="hero-title">Interrogate Your<br><span>Financial Documents</span></h1>
    <p class="hero-sub">Semantic search across Annual Reports, 10-Ks &amp; Earnings Transcripts</p>
    <div>
        <span class="hero-tag">LangChain</span>
        <span class="hero-tag">ChromaDB</span>
        <span class="hero-tag">OpenAI</span>
        <span class="hero-tag">Vector Search</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── STAT BAR ──────────────────────────────────────────────────────────────────
chunks = st.session_state.store_stats.get("total_chunks", 0)
docs   = st.session_state.store_stats.get("unique_documents", 0)
msgs   = len(st.session_state.messages) // 2
mdl    = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

st.markdown(f"""
<div class="stat-row">
    <div class="stat-card">
        <div class="stat-label">Model</div>
        <div class="stat-mono">{mdl}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Chunks Indexed</div>
        <div class="stat-value {'gold' if chunks else ''}">{chunks or '—'}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Documents</div>
        <div class="stat-value {'gold' if docs else ''}">{docs or '—'}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Exchanges</div>
        <div class="stat-value {'gold' if msgs else ''}">{msgs or '—'}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── CHAT HISTORY ──────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">◈</div>
        <div class="empty-title">Ready to analyse</div>
        <div class="empty-sub">
            Upload financial documents in the sidebar, then ask anything —
            revenue figures, risk factors, YoY changes, or competitive landscape.
        </div>
    </div>
    """, unsafe_allow_html=True)

for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="msg-user">
            <div class="msg-user-bubble">{message["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-assistant">
            <div class="msg-avatar">AI</div>
            <div>
                <div class="msg-assistant-bubble">{message["content"]}</div>
                <div class="msg-meta">◈ Financial RAG Assistant</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if message.get("sources"):
            with st.expander(f"▸ {len(message['sources'])} sources"):
                for src in message["sources"]:
                    st.markdown(f"""
                    <div class="source-item">
                        <span class="source-score">score {src['score']:.3f}</span>
                        <div class="source-filename">📄 {src['filename']}</div>
                        <div class="source-preview">{src['preview']}</div>
                    </div>
                    """, unsafe_allow_html=True)

# ── CHAT INPUT ────────────────────────────────────────────────────────────────
prefill  = st.session_state.pop("prefill_question", "")
question = st.chat_input("Ask about your financial documents...")

if question or prefill:
    q = question or prefill

    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
        st.stop()

    st.markdown(f"""
    <div class="msg-user">
        <div class="msg-user-bubble">{q}</div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": q})

    with st.spinner(""):
        try:
            pipeline  = get_pipeline()
            response  = pipeline.query(question=q, verbose=False)
            answer    = response.answer
            sources_data = []

            st.markdown(f"""
            <div class="msg-assistant">
                <div class="msg-avatar">AI</div>
                <div>
                    <div class="msg-assistant-bubble">{answer}</div>
                    <div class="msg-meta">◈ {response.model_used} &nbsp;·&nbsp; {response.tokens_used} tokens</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if response.sources:
                with st.expander(f"▸ {len(response.sources)} source documents"):
                    for src in response.sources:
                        fname   = src.metadata.get("filename", "Unknown")
                        score   = src.similarity_score
                        preview = src.content[:200].replace("\n", " ") + "..."
                        sources_data.append({"filename": fname, "score": score, "preview": preview})
                        st.markdown(f"""
                        <div class="source-item">
                            <span class="source-score">score {score:.3f}</span>
                            <div class="source-filename">📄 {fname}</div>
                            <div class="source-preview">{preview}</div>
                        </div>
                        """, unsafe_allow_html=True)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources_data
            })

        except ValueError as e:
            st.error(f"Configuration Error: {e}")
        except Exception as e:
            st.error(f"Error: {e}")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <div class="footer-text">
        Built by Yash Chaudhary &nbsp;·&nbsp; Financial RAG Assistant &nbsp;·&nbsp; LangChain × ChromaDB × OpenAI
    </div>
</div>
""", unsafe_allow_html=True)
