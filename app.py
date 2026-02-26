"""
app.py — Financial RAG Assistant
Royal Velvet & Black Theme
Run: streamlit run app.py
"""

import os
from datetime import date, timedelta
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Financial RAG Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── HIDE STREAMLIT CHROME ─────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], .stDeployButton { display:none !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROYAL VELVET & BLACK DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Syne:wght@400;500;600;700&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

:root {
  --void:       #030305;
  --black:      #07060C;
  --card:       #0D0B12;
  --card-2:     #120E1A;
  --panel:      #0F0C16;
  --border:     rgba(139,58,139,0.22);
  --border-l:   rgba(176,107,176,0.45);
  --velvet:     #6B2D6B;
  --velvet-l:   #8B3A8B;
  --velvet-gl:  #B06BB0;
  --accent:     #C084C8;
  --lilac:      #D4A8D8;
  --text:       #EDE8F5;
  --text-dim:   #9A8AAA;
  --text-ghost: #4A3858;
  --green:      #4ADE80;
  --green-d:    #166534;
  --red:        #F87171;
  --red-d:      #991B1B;
  --gold:       #F0C040;
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: 'Syne', sans-serif !important;
  color: var(--text) !important;
}

/* ── BACKGROUND ────────────────────────────────────── */
.stApp, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(ellipse 110% 55% at 0% 0%,   rgba(107,45,107,0.20) 0%, transparent 55%),
    radial-gradient(ellipse  80% 50% at 100% 100%, rgba(107,45,107,0.14) 0%, transparent 55%),
    radial-gradient(ellipse  60% 40% at 50% 50%,  rgba(107,45,107,0.04) 0%, transparent 70%),
    var(--black) !important;
}
[data-testid="stMain"], [data-testid="block-container"] {
  background: transparent !important;
  padding-top: 0 !important;
  max-width: 1120px !important;
}

/* ── SIDEBAR ───────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--panel) !important;
  border-right: 1px solid var(--border-l) !important;
  box-shadow: 4px 0 40px rgba(107,45,107,0.08) !important;
}
[data-testid="stSidebar"] > div { padding: 1.4rem 1.2rem !important; }

/* ── TYPOGRAPHY ────────────────────────────────────── */
h1, h2, h3, h4 {
  font-family: 'Cormorant Garamond', serif !important;
  color: var(--text) !important;
  letter-spacing: -0.01em !important;
}
code, pre, .mono { font-family: 'Space Mono', monospace !important; }

/* ── METRICS ───────────────────────────────────────── */
[data-testid="stMetric"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  padding: 0.9rem 1rem !important;
}
[data-testid="stMetricLabel"] p {
  font-family: 'Space Mono', monospace !important;
  font-size: 0.58rem !important;
  color: var(--text-ghost) !important;
  text-transform: uppercase !important;
  letter-spacing: 0.18em !important;
}
[data-testid="stMetricValue"] {
  font-family: 'Cormorant Garamond', serif !important;
  font-size: 1.7rem !important;
  font-weight: 300 !important;
  color: var(--accent) !important;
}

/* ── BUTTONS ───────────────────────────────────────── */
.stButton > button {
  background: transparent !important;
  border: 1px solid var(--border) !important;
  border-radius: 6px !important;
  color: var(--text-dim) !important;
  font-family: 'Syne', sans-serif !important;
  font-size: 0.8rem !important;
  transition: all 0.22s ease !important;
  text-align: left !important;
}
.stButton > button:hover {
  background: rgba(107,45,107,0.14) !important;
  border-color: var(--velvet-gl) !important;
  color: var(--accent) !important;
  box-shadow: 0 0 18px rgba(107,45,107,0.22) !important;
  transform: translateY(-1px) !important;
}

/* ── INPUTS ────────────────────────────────────────── */
.stTextInput input, .stTextArea textarea,
[data-testid="stTextInput"] input {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
  font-family: 'Syne', sans-serif !important;
  font-size: 0.88rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--velvet-l) !important;
  box-shadow: 0 0 0 2px rgba(107,45,107,0.25) !important;
}
.stTextInput input::placeholder { color: var(--text-ghost) !important; }

/* ── CHAT INPUT ────────────────────────────────────── */
[data-testid="stChatInput"] {
  background: var(--card-2) !important;
  border: 1px solid var(--border-l) !important;
  border-radius: 14px !important;
  box-shadow: 0 0 30px rgba(107,45,107,0.12) !important;
}
[data-testid="stChatInput"] textarea {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: var(--text) !important;
  font-family: 'Syne', sans-serif !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--text-ghost) !important; }
[data-testid="stChatInput"]:focus-within {
  border-color: rgba(139,58,139,0.7) !important;
  box-shadow: 0 0 30px rgba(107,45,107,0.22) !important;
}

/* ── CHAT MESSAGES ─────────────────────────────────── */
[data-testid="stChatMessage"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  padding: 0.8rem 1rem !important;
  margin-bottom: 0.5rem !important;
}

/* ── FILE UPLOADER ─────────────────────────────────── */
[data-testid="stFileUploader"] {
  background: rgba(107,45,107,0.05) !important;
  border: 1.5px dashed rgba(139,58,139,0.4) !important;
  border-radius: 10px !important;
}

/* ── EXPANDER ──────────────────────────────────────── */
[data-testid="stExpander"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
}
[data-testid="stExpander"] summary {
  background: transparent !important;
  font-family: 'Space Mono', monospace !important;
  font-size: 0.65rem !important;
  letter-spacing: 0.06em !important;
  color: var(--text-ghost) !important;
  border: none !important;
}

/* ── ALERTS ────────────────────────────────────────── */
[data-testid="stAlert"] {
  background: rgba(107,45,107,0.1) !important;
  border: 1px solid var(--border-l) !important;
  border-radius: 8px !important;
  color: var(--lilac) !important;
}
div[data-testid="stSuccess"] {
  background: rgba(74,222,128,0.07) !important;
  border-color: rgba(74,222,128,0.25) !important;
  color: #86efac !important;
}
div[data-testid="stError"] {
  background: rgba(248,113,113,0.07) !important;
  border-color: rgba(248,113,113,0.25) !important;
  color: #fca5a5 !important;
}

/* ── PROGRESS ──────────────────────────────────────── */
.stProgress > div > div {
  background: linear-gradient(90deg, var(--velvet), var(--accent)) !important;
}

/* ── MULTISELECT ───────────────────────────────────── */
[data-testid="stMultiSelect"] > div {
  background: var(--card) !important;
  border-color: var(--border) !important;
  border-radius: 8px !important;
}
.stMultiSelect span[data-baseweb="tag"] {
  background: rgba(107,45,107,0.3) !important;
  border: 1px solid var(--velvet-gl) !important;
  color: var(--lilac) !important;
  border-radius: 999px !important;
  font-size: 0.72rem !important;
}

/* ── SELECTBOX ─────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
  background: var(--card) !important;
  border-color: var(--border) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
}

/* ── LINE CHART ────────────────────────────────────── */
[data-testid="stArrowVegaLiteChart"] { border-radius: 8px; overflow: hidden; }

hr { border-color: var(--border) !important; margin: 1rem 0 !important; }
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-thumb { background: rgba(107,45,107,0.35); border-radius: 2px; }

/* ════════════════════════════════════════════════════
   CUSTOM COMPONENTS
   ════════════════════════════════════════════════════ */

/* Hero header */
.rag-header {
  position: relative;
  padding: 2rem 2.2rem;
  background: linear-gradient(135deg, rgba(107,45,107,0.22) 0%, rgba(13,11,18,0.98) 55%, rgba(107,45,107,0.12) 100%);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 18px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.4);
  margin-bottom: 1.4rem;
  overflow: hidden;
}
.rag-header::before {
  content: '';
  position: absolute;
  top: -80px; right: -80px;
  width: 280px; height: 280px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(107,45,107,0.25) 0%, transparent 70%);
  pointer-events: none;
}
.rag-header::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(107,45,107,0.6) 30%, rgba(192,132,200,0.8) 50%, rgba(107,45,107,0.6) 70%, transparent 100%);
}
.rag-kicker {
  font-family: 'Space Mono', monospace;
  font-size: 0.6rem;
  letter-spacing: 0.3em;
  color: var(--velvet-gl);
  text-transform: uppercase;
  margin-bottom: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.rag-kicker::before {
  content: '';
  display: inline-block;
  width: 20px; height: 1px;
  background: var(--velvet-gl);
  opacity: 0.6;
}
.rag-header h1 {
  font-family: 'Cormorant Garamond', serif !important;
  font-size: 3.2rem !important;
  font-weight: 300 !important;
  line-height: 1.0 !important;
  color: var(--text) !important;
  margin: 0 0 0.2rem !important;
  letter-spacing: -0.02em !important;
}
.rag-header h1 em {
  font-style: italic;
  background: linear-gradient(135deg, var(--velvet-gl) 0%, var(--accent) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.rag-header p {
  font-family: 'Syne', sans-serif;
  font-size: 0.86rem;
  color: var(--text-dim);
  margin: 0.6rem 0 0 !important;
  max-width: 480px;
}
.badge-row { display: flex; gap: 0.4rem; margin-top: 0.9rem; flex-wrap: wrap; }
.badge {
  font-family: 'Space Mono', monospace;
  font-size: 0.62rem;
  letter-spacing: 0.08em;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  border: 1px solid var(--border);
  color: var(--text-ghost);
  background: rgba(255,255,255,0.04);
}
.badge.v { border-color: rgba(139,58,139,0.5); color: var(--accent); background: rgba(107,45,107,0.12); }
.badge.g { border-color: rgba(74,222,128,0.3);  color: #86efac;      background: rgba(74,222,128,0.07); }

/* Stat strip */
.stat-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: rgba(107,45,107,0.22);
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(107,45,107,0.22);
  margin-bottom: 1.4rem;
}
.stat-cell {
  background: var(--card);
  padding: 1rem 1.2rem;
  position: relative;
  transition: background 0.25s;
}
.stat-cell:hover { background: var(--card-2); }
.stat-cell::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--velvet), var(--accent));
  opacity: 0;
  transition: opacity 0.25s;
}
.stat-cell:hover::before { opacity: 1; }
.stat-lbl {
  font-family: 'Space Mono', monospace;
  font-size: 0.52rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--text-ghost);
  margin-bottom: 0.4rem;
}
.stat-val {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.7rem;
  font-weight: 300;
  color: var(--text);
  line-height: 1;
}
.stat-val.active { color: var(--accent); }
.stat-val-mono {
  font-family: 'Space Mono', monospace;
  font-size: 0.68rem;
  color: var(--accent);
  line-height: 1.4;
}

/* Stock panel */
.stock-panel {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.2rem 1.4rem 0.5rem;
  margin-bottom: 1.4rem;
}
.stock-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.1rem;
  font-weight: 300;
  color: var(--text);
  margin-bottom: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.stock-title::before {
  content: '';
  display: inline-block;
  width: 3px; height: 1.1rem;
  background: linear-gradient(180deg, var(--velvet), var(--accent));
  border-radius: 2px;
}

/* Upload drawer (inline, above chat input) */
.upload-drawer {
  background: linear-gradient(135deg, rgba(107,45,107,0.18) 0%, rgba(13,11,18,0.95) 100%);
  border: 1px solid rgba(139,58,139,0.45);
  border-radius: 12px;
  padding: 1rem 1.1rem 0.7rem;
  margin-bottom: 0.6rem;
  animation: slideDown 0.2s ease;
}
.upload-drawer-title {
  font-family: 'Space Mono', monospace;
  font-size: 0.62rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--velvet-gl);
  margin-bottom: 0.6rem;
}
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-6px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Source cards */
.src-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-left: 3px solid var(--velvet-gl);
  border-radius: 0 8px 8px 0;
  padding: 0.7rem 0.9rem;
  margin: 0.4rem 0;
  font-size: 0.82rem;
  transition: border-left-color 0.2s;
}
.src-card:hover { border-left-color: var(--accent); background: var(--card-2); }
.src-name { font-family: 'Space Mono', monospace; font-size: 0.7rem; color: var(--accent); margin-bottom: 0.15rem; }
.src-score { font-family: 'Space Mono', monospace; font-size: 0.62rem; color: var(--text-ghost); }
.src-preview { color: var(--text-dim); line-height: 1.55; margin-top: 0.2rem; }

/* Sidebar section labels */
.sb-lbl {
  font-family: 'Space Mono', monospace;
  font-size: 0.54rem;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--velvet-gl);
  padding: 1.2rem 0 0.45rem;
  border-top: 1px solid var(--border);
  margin-top: 0.5rem;
}

/* API key active badge */
.key-ok {
  display: flex; align-items: center; gap: 0.5rem;
  background: rgba(74,222,128,0.07);
  border: 1px solid rgba(74,222,128,0.2);
  color: #86efac;
  padding: 0.38rem 0.7rem;
  border-radius: 6px;
  font-family: 'Space Mono', monospace;
  font-size: 0.6rem;
  letter-spacing: 0.1em;
}
.key-dot {
  width: 5px; height: 5px;
  border-radius: 50%;
  background: #4ade80;
  box-shadow: 0 0 6px #4ade80;
  animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

/* Doc pill */
.doc-pill {
  display: flex; align-items: center; gap: 0.4rem;
  background: rgba(107,45,107,0.1);
  border: 1px solid var(--border);
  padding: 0.32rem 0.65rem;
  border-radius: 4px;
  margin-bottom: 0.3rem;
  font-family: 'Space Mono', monospace;
  font-size: 0.58rem;
  color: var(--text-dim);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.doc-dot { width:4px; height:4px; border-radius:50%; background:var(--velvet-gl); flex-shrink:0; }

/* Empty state */
.empty {
  text-align: center;
  padding: 4rem 2rem;
}
.empty-orb {
  width: 100px; height: 100px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(107,45,107,0.28) 0%, transparent 70%);
  border: 1px solid var(--border);
  margin: 0 auto 1.5rem;
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem; color: var(--velvet-gl);
}
.empty-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.7rem;
  font-weight: 300;
  font-style: italic;
  color: var(--text-ghost);
  margin-bottom: 0.5rem;
}
.empty-sub {
  font-size: 0.8rem;
  color: var(--text-ghost);
  max-width: 300px;
  margin: 0 auto;
  line-height: 1.8;
  opacity: 0.7;
}

/* Footer */
.vfooter {
  text-align: center;
  padding: 1.8rem 0 0.5rem;
  position: relative;
  margin-top: 2.5rem;
}
.vfooter::before {
  content: '';
  position: absolute;
  top: 0; left: 50%; transform: translateX(-50%);
  width: 180px; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(107,45,107,0.5), transparent);
}
.vfooter-text {
  font-family: 'Space Mono', monospace;
  font-size: 0.56rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--text-ghost);
}

/* Ticker bar */
.ticker-row {
  display: flex; gap: 0.6rem; flex-wrap: wrap;
  margin-bottom: 0.8rem;
}
.ticker-chip {
  display: flex; flex-direction: column; align-items: center;
  background: var(--card-2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.45rem 0.7rem;
  min-width: 80px;
  font-family: 'Space Mono', monospace;
}
.ticker-sym  { font-size: 0.62rem; color: var(--accent); font-weight: 700; }
.ticker-prc  { font-size: 0.72rem; color: var(--text); margin-top: 0.1rem; }
.ticker-chg.up   { font-size: 0.6rem; color: #4ade80; }
.ticker-chg.down { font-size: 0.6rem; color: #f87171; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for k, v in [
    ("messages", []),
    ("vectorstore", None),
    ("uploaded_docs", 0),
    ("chunk_count", 0),
    ("file_names", []),
    ("show_upload", False),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# INGEST FUNCTION
# ══════════════════════════════════════════════════════════════════════════════
def ingest_documents(files):
    from chromadb import EphemeralClient
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    from pypdf import PdfReader
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    @st.cache_resource
    def load_model():
        return SentenceTransformer("all-MiniLM-L6-v2")

    model = load_model()
    client = EphemeralClient(settings=Settings(anonymized_telemetry=False))
    try:
        client.delete_collection("financials")
    except Exception:
        pass
    col = client.create_collection("financials", metadata={"hnsw:space": "cosine"})

    all_chunks, all_ids, all_meta, fnames = [], [], [], []
    prog = st.progress(0, text="Reading files…")

    for i, f in enumerate(files):
        if f.name.lower().endswith(".pdf"):
            reader = PdfReader(f)
            text = " ".join(pg.extract_text() or "" for pg in reader.pages)
        else:
            text = f.read().decode("utf-8")
        chunks = splitter.split_text(text)
        fnames.append(f.name)
        for j, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(f"{f.name}_chunk_{j}")
            all_meta.append({"filename": f.name, "chunk": j})
        prog.progress((i + 1) / len(files), text=f"Processed {f.name}")

    prog.empty()

    if all_chunks:
        with st.spinner(f"Embedding {len(all_chunks)} chunks…"):
            embs = model.encode(all_chunks, normalize_embeddings=True).tolist()
            col.add(documents=all_chunks, embeddings=embs, ids=all_ids, metadatas=all_meta)

    st.session_state.vectorstore  = {"collection": col, "model": model}
    st.session_state.uploaded_docs = len(files)
    st.session_state.chunk_count  = len(all_chunks)
    st.session_state.file_names   = fnames
    return len(all_chunks)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:0 0 1rem;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.4rem;font-weight:300;
                  color:#EDE8F5;line-height:1.1;">
        RAG <em style="color:#C084C8;font-style:italic;">Assistant</em>
      </div>
      <div style="font-family:'Space Mono',monospace;font-size:0.52rem;letter-spacing:0.22em;
                  color:#4A3858;text-transform:uppercase;margin-top:0.35rem;">
        Financial Intelligence · v3
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── API KEY ──────────────────────────────────────────────────────────────
    st.markdown('<div class="sb-lbl" style="border-top:none;padding-top:0;margin-top:0;">Configuration</div>', unsafe_allow_html=True)
    default_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))

    if default_key:
        GROQ_API_KEY = default_key
        st.markdown('<div class="key-ok"><div class="key-dot"></div>API Key Active</div>', unsafe_allow_html=True)
    else:
        GROQ_API_KEY = st.text_input("", type="password", placeholder="gsk_…", label_visibility="collapsed")
        st.markdown("<span style='font-family:Space Mono,monospace;font-size:0.56rem;color:#4A3858;'>console.groq.com → free key</span>", unsafe_allow_html=True)
        if GROQ_API_KEY:
            os.environ["GROQ_API_KEY"] = GROQ_API_KEY
            st.markdown('<div class="key-ok"><div class="key-dot"></div>API Key Active</div>', unsafe_allow_html=True)

    # ── KNOWLEDGE BASE STATS ─────────────────────────────────────────────────
    if st.session_state.file_names:
        st.markdown('<div class="sb-lbl">Knowledge Base</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Chunks", st.session_state.chunk_count)
        c2.metric("Docs", st.session_state.uploaded_docs)
        for fn in st.session_state.file_names:
            short = fn[:22] + "…" if len(fn) > 22 else fn
            st.markdown(f'<div class="doc-pill"><div class="doc-dot"></div>{short}</div>', unsafe_allow_html=True)

    # ── QUICK ASK ────────────────────────────────────────────────────────────
    st.markdown('<div class="sb-lbl">Quick Ask</div>', unsafe_allow_html=True)
    for q_item in [
        "What was total revenue?",
        "Main risk factors?",
        "EPS change YoY?",
        "Key business highlights",
        "Debt and liquidity summary",
    ]:
        if st.button(q_item, use_container_width=True, key=f"qa_{q_item[:14]}"):
            st.session_state["_prefill"] = q_item

    st.markdown('<div class="sb-lbl">Actions</div>', unsafe_allow_html=True)
    if st.button("✕  Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN PAGE
# ══════════════════════════════════════════════════════════════════════════════

# ── HERO HEADER ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="rag-header">
  <div class="rag-kicker">Financial Intelligence Platform</div>
  <h1>Interrogate Your<br><em>Financial Documents</em></h1>
  <p>Semantic search and AI-powered analysis across Annual Reports,
     10-Ks &amp; Earnings Transcripts. Ask in plain language.</p>
  <div class="badge-row">
    <span class="badge v">Semantic Retrieval</span>
    <span class="badge v">Source-backed Answers</span>
    <span class="badge v">Llama 3.3 · 70B</span>
    <span class="badge">Groq</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── STAT STRIP ───────────────────────────────────────────────────────────────
chunks = st.session_state.chunk_count
docs   = st.session_state.uploaded_docs
msgs   = len(st.session_state.messages) // 2

st.markdown(f"""
<div class="stat-strip">
  <div class="stat-cell">
    <div class="stat-lbl">Model</div>
    <div class="stat-val-mono">Llama 3.3 · 70B</div>
  </div>
  <div class="stat-cell">
    <div class="stat-lbl">Chunks Indexed</div>
    <div class="stat-val {'active' if chunks else ''}">{chunks if chunks else '—'}</div>
  </div>
  <div class="stat-cell">
    <div class="stat-lbl">Documents</div>
    <div class="stat-val {'active' if docs else ''}">{docs if docs else '—'}</div>
  </div>
  <div class="stat-cell">
    <div class="stat-lbl">Exchanges</div>
    <div class="stat-val {'active' if msgs else ''}">{msgs if msgs else '—'}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# LIVE STOCK CHART
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="stock-panel">', unsafe_allow_html=True)
st.markdown('<div class="stock-title">Live Market Overview</div>', unsafe_allow_html=True)

col_sym, col_rng = st.columns([4, 1])
with col_sym:
    symbols = st.multiselect(
        "symbols",
        options=["AAPL","MSFT","NVDA","GOOGL","AMZN","TSLA","META","TSM","SAP","BABA","SONY","NVO",
                 "RELIANCE.NS","TCS.NS","INFY.NS","WIPRO.NS"],
        default=["AAPL","MSFT","NVDA","TSLA"],
        label_visibility="collapsed",
    )
with col_rng:
    rng = st.selectbox("range", ["1D","5D","1M","3M","6M","1Y"], index=2, label_visibility="collapsed")

days_map = {"1D": 2, "5D": 7, "1M": 32, "3M": 95, "6M": 185, "1Y": 370}
interval_map = {"1D": "1m", "5D": "5m", "1M": "1d", "3M": "1d", "6M": "1d", "1Y": "1d"}

if symbols:
    try:
        import pandas as pd
        import yfinance as yf

        end_dt   = date.today()
        start_dt = end_dt - timedelta(days=days_map[rng])
        interval = interval_map[rng]

        # Download data
        if rng in ("1D", "5D"):
            raw = yf.download(
                tickers=symbols,
                period="5d" if rng == "5D" else "1d",
                interval=interval,
                auto_adjust=True,
                progress=False,
                group_by="ticker",
                threads=True,
            )
        else:
            raw = yf.download(
                tickers=symbols,
                start=start_dt.isoformat(),
                end=end_dt.isoformat(),
                interval=interval,
                auto_adjust=True,
                progress=False,
                group_by="ticker",
                threads=True,
            )

        chart = pd.DataFrame()
        if len(symbols) == 1:
            sym = symbols[0]
            if "Close" in raw.columns:
                chart[sym] = raw["Close"]
            elif hasattr(raw.columns, "levels"):
                chart[sym] = raw.xs("Close", axis=1, level=1) if "Close" in raw.columns.get_level_values(1) else raw.iloc[:, 0]
            else:
                chart[sym] = raw.iloc[:, 0]
        else:
            for sym in symbols:
                key = (sym, "Close")
                if key in raw.columns:
                    chart[sym] = raw[key]

        chart = chart.dropna(how="all")

        # Ticker chips — show latest price + daily change
        if not chart.empty:
            latest_prices = {}
            try:
                tinfo = yf.download(
                    tickers=symbols,
                    period="2d",
                    interval="1d",
                    auto_adjust=True,
                    progress=False,
                    group_by="ticker",
                    threads=True,
                )
                for sym in symbols:
                    try:
                        if len(symbols) == 1:
                            col_close = tinfo["Close"]
                        else:
                            col_close = tinfo[(sym, "Close")]
                        vals = col_close.dropna()
                        if len(vals) >= 2:
                            pct = (float(vals.iloc[-1]) - float(vals.iloc[-2])) / float(vals.iloc[-2]) * 100
                            latest_prices[sym] = {"price": float(vals.iloc[-1]), "pct": pct}
                        elif len(vals) == 1:
                            latest_prices[sym] = {"price": float(vals.iloc[-1]), "pct": 0.0}
                    except Exception:
                        pass
            except Exception:
                pass

            # Render ticker chips
            if latest_prices:
                chip_html = '<div class="ticker-row">'
                for sym, info in latest_prices.items():
                    pct   = info["pct"]
                    price = info["price"]
                    arrow = "▲" if pct >= 0 else "▼"
                    cls   = "up" if pct >= 0 else "down"
                    chip_html += f"""
                    <div class="ticker-chip">
                      <div class="ticker-sym">{sym}</div>
                      <div class="ticker-prc">${price:,.2f}</div>
                      <div class="ticker-chg {cls}">{arrow} {abs(pct):.2f}%</div>
                    </div>"""
                chip_html += '</div>'
                st.markdown(chip_html, unsafe_allow_html=True)

            # Normalised % return chart
            normed = (chart / chart.iloc[0] - 1) * 100
            st.line_chart(normed, height=220, use_container_width=True)
            st.caption(f"% return · {rng} · {len(chart)} data points · Yahoo Finance")
        else:
            st.info("No market data returned. Try a different range or symbols.")

    except Exception as e:
        st.info(f"Stock chart unavailable: {e}")
else:
    st.info("Select at least one symbol above to show the chart.")

st.markdown("</div>", unsafe_allow_html=True)  # close stock-panel

# ══════════════════════════════════════════════════════════════════════════════
# CHAT SECTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="font-family:'Cormorant Garamond',serif;font-size:1.35rem;font-weight:300;
            color:#EDE8F5;margin:0.5rem 0 0.8rem;">
  Ask About Your Documents
</div>
""", unsafe_allow_html=True)

# Empty state
if not st.session_state.messages:
    st.markdown("""
    <div class="empty">
      <div class="empty-orb">◈</div>
      <div class="empty-title">Awaiting your inquiry</div>
      <div class="empty-sub">
        Upload financial documents using the <strong>＋</strong> button below,
        then ask anything about revenue, risks, earnings or strategy.
      </div>
    </div>
    """, unsafe_allow_html=True)

# Chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander(f"↳ {len(msg['sources'])} source(s)"):
                for src in msg["sources"]:
                    st.markdown(f"""
                    <div class="src-card">
                      <div class="src-name">📄 {src['filename']}</div>
                      <div class="src-score">relevance: {src['score']}</div>
                      <div class="src-preview">{src['preview']}…</div>
                    </div>""", unsafe_allow_html=True)

# ── UPLOAD DRAWER (shown above input when ＋ is clicked) ─────────────────────
if st.session_state.show_upload:
    st.markdown('<div class="upload-drawer"><div class="upload-drawer-title">◈ Upload Financial Documents</div>', unsafe_allow_html=True)
    inline_files = st.file_uploader(
        "Upload",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="drawer_upload",
    )
    col_ing, col_cls = st.columns([3, 1])
    with col_ing:
        if inline_files and st.button("⬆  Ingest Documents", use_container_width=True, key="drawer_ingest"):
            if not GROQ_API_KEY:
                st.error("Enter your Groq API key in the sidebar first.")
            else:
                try:
                    n = ingest_documents(inline_files)
                    st.success(f"✓ {n} chunks from {len(inline_files)} file(s) ingested")
                    st.session_state.show_upload = False
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    with col_cls:
        if st.button("✕ Close", use_container_width=True, key="drawer_close"):
            st.session_state.show_upload = False
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── QUESTION BAR with ＋ button ───────────────────────────────────────────────
bar_col1, bar_col2 = st.columns([1, 16], gap="small")

with bar_col1:
    if st.button("＋", key="plus_btn", use_container_width=True, help="Upload documents"):
        st.session_state.show_upload = not st.session_state.show_upload
        st.rerun()

with bar_col2:
    prefill  = st.session_state.pop("_prefill", None)
    question = st.chat_input("Ask about your financial documents…")

q = prefill or question

# ── ANSWER GENERATION ────────────────────────────────────────────────────────
if q:
    if not GROQ_API_KEY:
        st.error("Please enter your Groq API key in the sidebar.")
        st.stop()

    with st.chat_message("user"):
        st.markdown(q)
    st.session_state.messages.append({"role": "user", "content": q})

    with st.chat_message("assistant"):
        with st.spinner("Searching and generating…"):
            try:
                from openai import OpenAI
                oai = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

                context      = "No documents ingested yet. Please upload financial documents first."
                sources_data = []

                if st.session_state.vectorstore:
                    vs    = st.session_state.vectorstore
                    q_emb = vs["model"].encode([q], normalize_embeddings=True).tolist()
                    res   = vs["collection"].query(
                        query_embeddings=q_emb,
                        n_results=5,
                        include=["documents", "metadatas", "distances"],
                    )
                    cks  = res["documents"][0]
                    mts  = res["metadatas"][0]
                    dts  = res["distances"][0]
                    context = "\n---\n".join(f"[{m['filename']}]\n{c}" for c, m in zip(cks, mts))
                    sources_data = [
                        {"filename": m["filename"], "score": round(1 - d / 2, 3), "preview": c[:220]}
                        for c, m, d in zip(cks, mts, dts)
                    ]

                resp = oai.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": (
                            "You are an expert financial analyst. Answer questions based only on the "
                            "provided context. Always cite specific numbers and dates. "
                            "If information is missing, say so clearly."
                        )},
                        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {q}"},
                    ],
                    temperature=0.1,
                    max_tokens=1500,
                )
                answer = resp.choices[0].message.content
                tokens = resp.usage.total_tokens

                st.markdown(answer)

                if sources_data:
                    with st.expander(f"↳ {len(sources_data)} source(s) used"):
                        for src in sources_data:
                            st.markdown(f"""
                            <div class="src-card">
                              <div class="src-name">📄 {src['filename']}</div>
                              <div class="src-score">relevance: {src['score']}</div>
                              <div class="src-preview">{src['preview']}…</div>
                            </div>""", unsafe_allow_html=True)

                st.caption(f"llama-3.3-70b-versatile · {tokens} tokens")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources_data,
                })

            except Exception as e:
                st.error(f"Error: {e}")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vfooter">
  <div class="vfooter-text">
    Built by Yash Chaudhary &nbsp;·&nbsp; Financial RAG Assistant &nbsp;·&nbsp; Llama 3.3 × Groq × ChromaDB
  </div>
</div>
""", unsafe_allow_html=True)
