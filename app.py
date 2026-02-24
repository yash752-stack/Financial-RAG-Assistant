"""
app.py
======
Streamlit web interface for the Financial RAG Assistant.
Run with: streamlit run app.py
"""

import os
import sys
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Financial RAG Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Syne:wght@400;500;600;700&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

:root {
    --velvet: #6B2D6B;
    --velvet-l: #8B3A8B;
    --velvet-glow: #B06BB0;
    --accent: #C084C8;
    --black: #050507;
    --card: #0C0B0F;
    --mid: #120F17;
    --panel: #0F0D14;
    --text: #EDE8F5;
    --text-dim: #7A7088;
    --text-ghost: #3A3448;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body { background: var(--black) !important; }

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 100% 60% at 0% 0%, rgba(107,45,107,0.18) 0%, transparent 55%),
        radial-gradient(ellipse 70% 50% at 100% 100%, rgba(107,45,107,0.12) 0%, transparent 55%),
        var(--black) !important;
    color: var(--text) !important;
}

[data-testid="stSidebar"] {
    background: var(--panel) !important;
    border-right: 1px solid rgba(107,45,107,0.3) !important;
    box-shadow: 4px 0 40px rgba(107,45,107,0.08) !important;
}

#MainMenu, footer, header, .stDeployButton { visibility: hidden; display: none; }

* { font-family: 'Syne', sans-serif !important; }

/* ── HERO ── */
.hero {
    position: relative;
    padding: 4rem 0 3rem;
    margin-bottom: 2.5rem;
    overflow: hidden;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(107,45,107,0.6) 30%, rgba(192,132,200,0.8) 50%, rgba(107,45,107,0.6) 70%, transparent 100%);
}
.hero::before {
    content: '';
    position: absolute;
    top: -40px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(107,45,107,0.2) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-kicker {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    color: var(--velvet-glow);
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.hero-kicker::before {
    content: '';
    display: inline-block;
    width: 24px; height: 1px;
    background: var(--velvet-glow);
    opacity: 0.6;
}
.hero-title {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 4.5rem;
    font-weight: 300;
    line-height: 1.0;
    color: var(--text);
    letter-spacing: -0.02em;
    margin-bottom: 0.4rem;
}
.hero-title em {
    font-family: 'Cormorant Garamond', serif !important;
    font-style: italic;
    font-weight: 300;
    background: linear-gradient(135deg, var(--velvet-glow) 0%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-desc {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.88rem;
    font-weight: 400;
    color: var(--text-dim);
    letter-spacing: 0.03em;
    margin-top: 1rem;
    max-width: 500px;
}

/* ── STAT STRIP ── */
.stats-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: rgba(107,45,107,0.2);
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 2.5rem;
    border: 1px solid rgba(107,45,107,0.2);
}
.stat-cell {
    background: var(--card);
    padding: 1.2rem 1.4rem;
    position: relative;
    transition: background 0.3s;
}
.stat-cell:hover { background: var(--mid); }
.stat-cell::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--velvet), var(--accent));
    opacity: 0;
    transition: opacity 0.3s;
}
.stat-cell:hover::before { opacity: 1; }
.stat-lbl {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.55rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--text-ghost);
    margin-bottom: 0.5rem;
}
.stat-val {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.9rem;
    font-weight: 300;
    color: var(--text);
    line-height: 1;
}
.stat-val.v { color: var(--accent); }
.stat-val-mono {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.72rem;
    color: var(--accent);
    line-height: 1.4;
}

/* ── EMPTY STATE ── */
.empty {
    text-align: center;
    padding: 6rem 2rem;
}
.empty-orb {
    width: 120px; height: 120px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(107,45,107,0.3) 0%, transparent 70%);
    border: 1px solid rgba(107,45,107,0.3);
    margin: 0 auto 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5rem;
    color: var(--velvet-glow);
}
.empty-title {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 2rem;
    font-weight: 300;
    font-style: italic;
    color: var(--text-ghost);
    margin-bottom: 0.75rem;
}
.empty-sub {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.8rem;
    color: var(--text-ghost);
    max-width: 360px;
    margin: 0 auto;
    line-height: 1.8;
    opacity: 0.6;
}
.empty-hint {
    margin-top: 2rem;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    color: var(--velvet-glow);
    opacity: 0.5;
    text-transform: uppercase;
}

/* ── CHAT MESSAGES ── */
.msg-u {
    display: flex;
    justify-content: flex-end;
    padding: 0.75rem 0;
}
.bubble-u {
    max-width: 60%;
    background: linear-gradient(135deg, #1A0F1A 0%, #160C1A 100%);
    border: 1px solid rgba(107,45,107,0.4);
    border-radius: 20px 20px 4px 20px;
    padding: 1rem 1.4rem;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.92rem;
    color: var(--text);
    line-height: 1.65;
    box-shadow: 0 4px 24px rgba(107,45,107,0.15), inset 0 1px 0 rgba(192,132,200,0.1);
}
.msg-a {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    padding: 0.75rem 0;
}
.avatar {
    flex-shrink: 0;
    width: 36px; height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--velvet) 0%, var(--velvet-l) 100%);
    border: 1px solid rgba(192,132,200,0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.6rem;
    color: var(--accent);
    box-shadow: 0 0 20px rgba(107,45,107,0.4);
    margin-top: 2px;
}
.bubble-a-wrap { max-width: 78%; }
.bubble-a {
    background: var(--card);
    border: 1px solid rgba(107,45,107,0.15);
    border-radius: 4px 20px 20px 20px;
    padding: 1.2rem 1.5rem;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.92rem;
    color: #C8C0D8;
    line-height: 1.8;
    box-shadow: 0 4px 32px rgba(0,0,0,0.4);
}
.bubble-meta {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.55rem;
    letter-spacing: 0.12em;
    color: var(--text-ghost);
    text-transform: uppercase;
    margin-top: 0.5rem;
    padding-left: 0.25rem;
}

/* ── SOURCE CARDS ── */
.src-card {
    background: var(--card);
    border: 1px solid rgba(107,45,107,0.15);
    border-left: 2px solid var(--velvet);
    border-radius: 0 6px 6px 0;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.5rem;
    transition: border-left-color 0.2s, background 0.2s;
}
.src-card:hover { border-left-color: var(--accent); background: var(--mid); }
.src-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.3rem; }
.src-fname { font-family: 'Space Mono', monospace !important; font-size: 0.68rem; color: var(--accent); }
.src-badge {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.58rem;
    color: var(--text-ghost);
    background: rgba(107,45,107,0.15);
    border: 1px solid rgba(107,45,107,0.2);
    padding: 0.1rem 0.4rem;
    border-radius: 3px;
}
.src-text { font-family: 'Syne', sans-serif !important; font-size: 0.76rem; color: var(--text-ghost); line-height: 1.55; }

/* ── SIDEBAR ── */
.sb-logo {
    padding: 2rem 0 1.5rem;
    border-bottom: 1px solid rgba(107,45,107,0.2);
    margin-bottom: 0.5rem;
}
.sb-logo-title {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.4rem;
    font-weight: 300;
    color: var(--text);
}
.sb-logo-title em {
    font-family: 'Cormorant Garamond', serif !important;
    font-style: italic;
    color: var(--accent);
}
.sb-logo-sub {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.52rem;
    letter-spacing: 0.25em;
    color: var(--text-ghost);
    text-transform: uppercase;
    margin-top: 0.4rem;
}
.sb-section {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.55rem;
    letter-spacing: 0.28em;
    color: var(--velvet-glow);
    text-transform: uppercase;
    padding: 1.5rem 0 0.5rem;
    border-bottom: 1px solid rgba(107,45,107,0.15);
    margin-bottom: 0.75rem;
}
.key-active {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    background: rgba(74,222,128,0.06);
    border: 1px solid rgba(74,222,128,0.15);
    color: #6ee7b7;
    padding: 0.45rem 0.8rem;
    border-radius: 4px;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.6rem;
    letter-spacing: 0.12em;
    width: 100%;
}
.key-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: #4ade80;
    box-shadow: 0 0 6px #4ade80;
    animation: blink 2s infinite;
}
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
.doc-pill {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(107,45,107,0.08);
    border: 1px solid rgba(107,45,107,0.2);
    padding: 0.38rem 0.7rem;
    border-radius: 4px;
    margin-bottom: 0.35rem;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.6rem;
    color: var(--text-dim);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.doc-pill-dot { width: 4px; height: 4px; border-radius: 50%; background: var(--velvet-glow); flex-shrink: 0; }

/* ── BUTTONS ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid rgba(107,45,107,0.25) !important;
    color: var(--text-dim) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.78rem !important;
    border-radius: 4px !important;
    transition: all 0.25s ease !important;
    text-align: left !important;
    padding: 0.5rem 0.9rem !important;
}
.stButton > button:hover {
    background: rgba(107,45,107,0.12) !important;
    border-color: rgba(107,45,107,0.6) !important;
    color: var(--accent) !important;
    box-shadow: 0 0 16px rgba(107,45,107,0.2) !important;
}

/* ── INPUTS ── */
.stTextInput input {
    background: var(--card) !important;
    border: 1px solid rgba(107,45,107,0.3) !important;
    border-radius: 4px !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.85rem !important;
}
.stTextInput input::placeholder { color: var(--text-ghost) !important; }

[data-testid="stFileUploader"] {
    background: rgba(107,45,107,0.04) !important;
    border: 1px dashed rgba(107,45,107,0.3) !important;
    border-radius: 6px !important;
}

[data-testid="stChatInput"] > div {
    background: var(--card) !important;
    border: 1px solid rgba(107,45,107,0.3) !important;
    border-radius: 12px !important;
    box-shadow: 0 0 30px rgba(107,45,107,0.1) !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: rgba(107,45,107,0.6) !important;
    box-shadow: 0 0 30px rgba(107,45,107,0.2) !important;
}
[data-testid="stChatInput"] textarea { background: transparent !important; color: var(--text) !important; font-family: 'Syne', sans-serif !important; font-size: 0.9rem !important; }
[data-testid="stChatInput"] textarea::placeholder { color: var(--text-ghost) !important; }

[data-testid="stExpander"] summary, .streamlit-expanderHeader {
    background: var(--card) !important;
    border: 1px solid rgba(107,45,107,0.15) !important;
    border-radius: 4px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.08em !important;
    color: var(--text-ghost) !important;
}

.stProgress > div > div { background: linear-gradient(90deg, var(--velvet), var(--accent)) !important; }

[data-testid="stMetric"] { background: var(--card) !important; border: 1px solid rgba(107,45,107,0.15) !important; padding: 0.75rem 1rem !important; border-radius: 4px !important; }
[data-testid="stMetricLabel"] p { font-family: 'Space Mono', monospace !important; font-size: 0.55rem !important; letter-spacing: 0.2em !important; color: var(--text-ghost) !important; text-transform: uppercase !important; }
[data-testid="stMetricValue"] { font-family: 'Cormorant Garamond', serif !important; color: var(--accent) !important; font-size: 1.6rem !important; font-weight: 300 !important; }

.stSuccess { background: rgba(74,222,128,0.06) !important; border: 1px solid rgba(74,222,128,0.15) !important; color: #6ee7b7 !important; border-radius: 4px !important; }
.stError   { background: rgba(248,113,113,0.06) !important; border: 1px solid rgba(248,113,113,0.15) !important; color: #fca5a5 !important; border-radius: 4px !important; }
.stInfo    { background: rgba(107,45,107,0.08) !important; border: 1px solid rgba(107,45,107,0.2) !important; color: var(--accent) !important; border-radius: 4px !important; }

hr { border: none !important; height: 1px !important; background: rgba(107,45,107,0.15) !important; margin: 1rem 0 !important; }

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(107,45,107,0.3); border-radius: 2px; }

.vb-footer { text-align: center; padding: 2.5rem 0 1rem; margin-top: 4rem; position: relative; }
.vb-footer::before { content: ''; position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 200px; height: 1px; background: linear-gradient(90deg, transparent, rgba(107,45,107,0.5), transparent); }
.vb-footer-text { font-family: 'Space Mono', monospace !important; font-size: 0.58rem; letter-spacing: 0.22em; color: var(--text-ghost); text-transform: uppercase; }

[data-testid="stChatMessage"] { background: transparent !important; border: none !important; box-shadow: none !important; }
</style>
""", unsafe_allow_html=True)


# ── SESSION STATE ─────────────────────────────────────────────────────────────
for k, v in [("messages", []), ("docs_ingested", False), ("store_stats", {})]:
    if k not in st.session_state:
        st.session_state[k] = v


@st.cache_resource
def get_pipeline():
    from chromadb import EphemeralClient
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    return {"client": EphemeralClient(settings=Settings(anonymized_telemetry=False)),
            "model": SentenceTransformer("all-MiniLM-L6-v2")}


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
        <div class="sb-logo-title">RAG <em>Assistant</em></div>
        <div class="sb-logo-sub">Financial Intelligence · v2</div>
    </div>
    """, unsafe_allow_html=True)

    # ── API KEY ──
    st.markdown('<div class="sb-section">Configuration</div>', unsafe_allow_html=True)

    default_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
    if default_key:
        GROQ_API_KEY = default_key
        st.markdown("""
        <div class="key-active">
            <div class="key-dot"></div>
            API Key Active
        </div>
        """, unsafe_allow_html=True)
    else:
        GROQ_API_KEY = st.text_input(
            "", type="password",
            placeholder="gsk_...",
            label_visibility="collapsed"
        )
        st.markdown("<small style='font-family:Space Mono,monospace;font-size:0.58rem;color:#3A3448;'>console.groq.com → free key</small>", unsafe_allow_html=True)
        if GROQ_API_KEY:
            st.markdown("""
            <div class="key-active">
                <div class="key-dot"></div>
                API Key Active
            </div>
            """, unsafe_allow_html=True)

    # ── DOCUMENTS ──
    st.markdown('<div class="sb-section">Documents</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "", type=["pdf", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files and st.button("↑  Ingest Documents", use_container_width=True):
        if not GROQ_API_KEY:
            st.error("Please enter your Groq API key first.")
        else:
            with st.spinner("Embedding documents..."):
                try:
                    from chromadb import EphemeralClient
                    from chromadb.config import Settings
                    from sentence_transformers import SentenceTransformer
                    from pypdf import PdfReader
                    from langchain_text_splitters import RecursiveCharacterTextSplitter

                    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

                    @st.cache_resource
                    def load_embed_model():
                        return SentenceTransformer("all-MiniLM-L6-v2")

                    embed_model = load_embed_model()
                    chroma = EphemeralClient(settings=Settings(anonymized_telemetry=False))
                    try: chroma.delete_collection("financials")
                    except: pass
                    col = chroma.create_collection("financials", metadata={"hnsw:space": "cosine"})

                    all_chunks, all_ids, all_meta, file_names = [], [], [], []
                    prog = st.progress(0)
                    for i, f in enumerate(uploaded_files):
                        if f.name.endswith(".pdf"):
                            reader = PdfReader(f)
                            text = " ".join(p.extract_text() or "" for p in reader.pages)
                        else:
                            text = f.read().decode("utf-8")
                        chunks = splitter.split_text(text)
                        file_names.append(f.name)
                        for j, chunk in enumerate(chunks):
                            all_chunks.append(chunk)
                            all_ids.append(f"{f.name}_chunk_{j}")
                            all_meta.append({"filename": f.name, "chunk": j})
                        prog.progress((i + 1) / len(uploaded_files))

                    if all_chunks:
                        embeddings = embed_model.encode(all_chunks, normalize_embeddings=True).tolist()
                        col.add(documents=all_chunks, embeddings=embeddings, ids=all_ids, metadatas=all_meta)

                    st.session_state.vectorstore = {"collection": col, "model": embed_model}
                    st.session_state.docs_ingested = True
                    st.session_state.store_stats = {
                        "total_chunks": len(all_chunks),
                        "unique_documents": len(file_names),
                        "sources": file_names
                    }
                    st.success(f"✓ {len(all_chunks)} chunks from {len(uploaded_files)} files")
                except Exception as e:
                    st.error(str(e))

    # ── KNOWLEDGE BASE ──
    if st.session_state.store_stats:
        stats = st.session_state.store_stats
        st.markdown('<div class="sb-section">Knowledge Base</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Chunks", stats.get("total_chunks", 0))
        c2.metric("Docs", stats.get("unique_documents", 0))
        for src in stats.get("sources", []):
            short = src[:24] + "…" if len(src) > 24 else src
            st.markdown(f'<div class="doc-pill"><div class="doc-pill-dot"></div>{short}</div>', unsafe_allow_html=True)

    # ── QUICK ASK ──
    st.markdown('<div class="sb-section">Quick Ask</div>', unsafe_allow_html=True)
    for q in ["What was the total revenue?", "Main risk factors?", "EPS change YoY?", "Debt situation?", "Key business highlights"]:
        if st.button(q, use_container_width=True, key=f"sq_{q[:12]}"):
            st.session_state.prefill_question = q

    st.markdown('<div class="sb-section">Actions</div>', unsafe_allow_html=True)
    if st.button("✕  Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ══════════════════════════════════════════════════════════════
# HERO — no tech pills
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-kicker">Financial Intelligence Platform</div>
    <h1 class="hero-title">Interrogate Your<br><em>Financial Documents</em></h1>
    <p class="hero-desc">
        Semantic search and AI-powered analysis across Annual Reports,
        10-Ks &amp; Earnings Transcripts. Ask in plain language.
    </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# STAT STRIP — show Llama model name
# ══════════════════════════════════════════════════════════════
chunks = st.session_state.store_stats.get("total_chunks", 0)
docs   = st.session_state.store_stats.get("unique_documents", 0)
msgs   = len(st.session_state.messages) // 2

st.markdown(f"""
<div class="stats-strip">
    <div class="stat-cell">
        <div class="stat-lbl">Model</div>
        <div class="stat-val-mono">Llama 3.3 · 70B</div>
    </div>
    <div class="stat-cell">
        <div class="stat-lbl">Chunks Indexed</div>
        <div class="stat-val {'v' if chunks else ''}">{chunks if chunks else '—'}</div>
    </div>
    <div class="stat-cell">
        <div class="stat-lbl">Documents</div>
        <div class="stat-val {'v' if docs else ''}">{docs if docs else '—'}</div>
    </div>
    <div class="stat-cell">
        <div class="stat-lbl">Exchanges</div>
        <div class="stat-val {'v' if msgs else ''}">{msgs if msgs else '—'}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# CHAT HISTORY
# ══════════════════════════════════════════════════════════════
if not st.session_state.messages:
    st.markdown("""
    <div class="empty">
        <div class="empty-orb">◈</div>
        <div class="empty-title">Awaiting your inquiry</div>
        <div class="empty-sub">
            Upload financial documents from the sidebar, then ask anything —
            revenue figures, risk assessments, year-over-year performance, or competitive landscape.
        </div>
        <div class="empty-hint">← Begin by uploading documents</div>
    </div>
    """, unsafe_allow_html=True)

for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="msg-u">
            <div class="bubble-u">{message["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-a">
            <div class="avatar">AI</div>
            <div class="bubble-a-wrap">
                <div class="bubble-a">{message["content"]}</div>
                <div class="bubble-meta">◈ Llama 3.3 · 70B via Groq</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if message.get("sources"):
            with st.expander(f"▸ {len(message['sources'])} source documents"):
                for src in message["sources"]:
                    st.markdown(f"""
                    <div class="src-card">
                        <div class="src-top">
                            <div class="src-fname">📄 {src['filename']}</div>
                            <div class="src-badge">score {src['score']:.3f}</div>
                        </div>
                        <div class="src-text">{src['preview']}</div>
                    </div>
                    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# CHAT INPUT
# ══════════════════════════════════════════════════════════════
prefill  = st.session_state.pop("prefill_question", "")
question = st.chat_input("Ask about your financial documents...")

if question or prefill:
    q = question or prefill

    if not GROQ_API_KEY:
        st.error("Please enter your Groq API key in the sidebar.")
        st.stop()

    st.markdown(f"""
    <div class="msg-u">
        <div class="bubble-u">{q}</div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": q})

    with st.spinner(""):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

            context = "No documents ingested yet. Please upload financial documents first."
            sources_data = []

            if st.session_state.get("vectorstore"):
                vs = st.session_state.vectorstore
                q_emb = vs["model"].encode([q], normalize_embeddings=True).tolist()
                results = vs["collection"].query(query_embeddings=q_emb, n_results=5,
                                                  include=["documents", "metadatas", "distances"])
                chunks_  = results["documents"][0]
                metas    = results["metadatas"][0]
                dists    = results["distances"][0]
                context  = "\n---\n".join(f"[{m['filename']}]\n{c}" for c, m in zip(chunks_, metas))
                sources_data = [
                    {"filename": m["filename"], "score": round(1 - d / 2, 3), "preview": c[:200]}
                    for c, m, d in zip(chunks_, metas, dists)
                ]

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": (
                        "You are an expert financial analyst assistant. "
                        "Answer questions based only on the provided context. "
                        "Always cite specific numbers and dates. "
                        "If information is missing, say so clearly."
                    )},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {q}"}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            answer = response.choices[0].message.content
            tokens = response.usage.total_tokens

            st.markdown(f"""
            <div class="msg-a">
                <div class="avatar">AI</div>
                <div class="bubble-a-wrap">
                    <div class="bubble-a">{answer}</div>
                    <div class="bubble-meta">◈ Llama 3.3 · 70B via Groq &nbsp;·&nbsp; {tokens} tokens</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if sources_data:
                with st.expander(f"▸ {len(sources_data)} source documents"):
                    for src in sources_data:
                        st.markdown(f"""
                        <div class="src-card">
                            <div class="src-top">
                                <div class="src-fname">📄 {src['filename']}</div>
                                <div class="src-badge">score {src['score']:.3f}</div>
                            </div>
                            <div class="src-text">{src['preview']}...</div>
                        </div>
                        """, unsafe_allow_html=True)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources_data
            })

        except Exception as e:
            st.error(f"Error: {e}")

# ══════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="vb-footer">
    <div class="vb-footer-text">
        Built by Yash Chaudhary &nbsp;·&nbsp; Financial RAG Assistant &nbsp;·&nbsp; Llama 3.3 × Groq × ChromaDB
    </div>
</div>
""", unsafe_allow_html=True)
