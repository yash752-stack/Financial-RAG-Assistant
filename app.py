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

/* ── Currency panel ── */
.fx-panel {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.1rem 1.4rem 0.9rem;
  margin-bottom: 1.4rem;
}
.fx-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.1rem; font-weight: 300;
  color: var(--text); margin-bottom: 0.9rem;
  display: flex; align-items: center; gap: 0.5rem;
}
.fx-title::before {
  content: '';
  display: inline-block; width: 3px; height: 1.1rem;
  background: linear-gradient(180deg, var(--velvet), var(--accent));
  border-radius: 2px;
}
.fx-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 0.7rem;
}
.fx-card {
  background: var(--card-2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 0.75rem 1rem;
  position: relative;
  overflow: hidden;
  transition: border-color 0.2s, background 0.2s;
}
.fx-card:hover { border-color: var(--border-l); background: rgba(107,45,107,0.08); }
.fx-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--velvet), var(--accent));
  opacity: 0; transition: opacity 0.2s;
}
.fx-card:hover::before { opacity: 1; }
.fx-pair {
  font-family: 'Space Mono', monospace;
  font-size: 0.58rem; letter-spacing: 0.18em;
  text-transform: uppercase; color: var(--text-ghost);
  margin-bottom: 0.3rem;
}
.fx-flag { font-size: 1rem; margin-bottom: 0.2rem; }
.fx-rate {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.55rem; font-weight: 300;
  color: var(--text); line-height: 1; margin-bottom: 0.2rem;
}
.fx-chg {
  font-family: 'Space Mono', monospace;
  font-size: 0.6rem;
}
.fx-chg.up   { color: #4ade80; }
.fx-chg.down { color: #f87171; }
.fx-chg.flat { color: var(--text-ghost); }
.fx-name {
  font-size: 0.68rem; color: var(--text-ghost);
  margin-top: 0.1rem;
}
.fx-updated {
  font-family: 'Space Mono', monospace;
  font-size: 0.52rem; letter-spacing: 0.1em;
  color: var(--text-ghost); margin-top: 0.6rem;
  text-align: right;
}
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
        "What is USD/INR today?",
        "Compare INR vs JPY vs Yuan",
        "How is NVDA performing?",
        "What was total revenue?",
        "Main risk factors?",
        "EPS change YoY?",
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

period_map   = {"1D": "1d",  "5D": "5d",  "1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y"}
interval_map = {"1D": "5m",  "5D": "30m", "1M": "1d",  "3M": "1d",  "6M": "1d",  "1Y": "1wk"}

import requests, pandas as pd

@st.cache_data(ttl=300)
def fetch_yahoo(symbol: str, period: str, interval: str):
    """
    Fetch OHLCV data from Yahoo Finance v8 JSON API — no yfinance needed.
    Returns a pandas Series of Close prices indexed by datetime, or None on failure.
    """
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?range={period}&interval={interval}&includePrePost=false"
    )
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data  = r.json()
        res   = data["chart"]["result"][0]
        ts    = res["timestamp"]
        close = res["indicators"]["quote"][0]["close"]
        idx   = pd.to_datetime(ts, unit="s", utc=True).tz_convert("US/Eastern")
        s     = pd.Series(close, index=idx, name=symbol).dropna()
        return s
    except Exception:
        return None

@st.cache_data(ttl=60)
def fetch_quote(symbol: str):
    """Fetch latest price + day change % from Yahoo Finance."""
    url     = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=2d&interval=1d"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r    = requests.get(url, headers=headers, timeout=8)
        r.raise_for_status()
        data = r.json()
        res  = data["chart"]["result"][0]
        q    = res["indicators"]["quote"][0]["close"]
        q    = [x for x in q if x is not None]
        if len(q) >= 2:
            pct = (q[-1] - q[-2]) / q[-2] * 100
        else:
            pct = 0.0
        return {"price": q[-1], "pct": pct} if q else None
    except Exception:
        return None

@st.cache_data(ttl=60)
def fetch_fx():
    """
    Fetch real-time FX rates for major currency pairs vs USD
    using Yahoo Finance JSON API — no extra packages required.
    Returns dict: { 'USDINR': {'rate':..,'pct':..,'prev':..}, ... }
    """
    pairs = {
        "USDINR=X":  {"label": "USD / INR",  "flag": "🇮🇳", "name": "Indian Rupee",      "base": "USD", "quote": "INR"},
        "USDJPY=X":  {"label": "USD / JPY",  "flag": "🇯🇵", "name": "Japanese Yen",      "base": "USD", "quote": "JPY"},
        "USDCNY=X":  {"label": "USD / CNY",  "flag": "🇨🇳", "name": "Chinese Yuan",      "base": "USD", "quote": "CNY"},
        "EURUSD=X":  {"label": "EUR / USD",  "flag": "🇪🇺", "name": "Euro",              "base": "EUR", "quote": "USD"},
        "GBPUSD=X":  {"label": "GBP / USD",  "flag": "🇬🇧", "name": "British Pound",     "base": "GBP", "quote": "USD"},
        "USDCHF=X":  {"label": "USD / CHF",  "flag": "🇨🇭", "name": "Swiss Franc",       "base": "USD", "quote": "CHF"},
    }
    results = {}
    headers = {"User-Agent": "Mozilla/5.0"}
    for symbol, meta in pairs.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=2d&interval=1d"
            r   = requests.get(url, headers=headers, timeout=8)
            r.raise_for_status()
            data  = r.json()
            res   = data["chart"]["result"][0]
            close = res["indicators"]["quote"][0]["close"]
            close = [x for x in close if x is not None]
            if not close:
                continue
            rate = close[-1]
            prev = close[-2] if len(close) >= 2 else rate
            pct  = (rate - prev) / prev * 100 if prev else 0.0
            results[symbol] = {**meta, "rate": rate, "prev": prev, "pct": pct}
        except Exception:
            continue
    return results

if symbols:
    period   = period_map[rng]
    interval = interval_map[rng]

    # ── Ticker chips (live quotes) ────────────────────────────────
    chip_html = '<div class="ticker-row">'
    any_chip  = False
    for sym in symbols:
        info = fetch_quote(sym)
        if info:
            any_chip = True
            arrow = "▲" if info["pct"] >= 0 else "▼"
            cls   = "up" if info["pct"] >= 0 else "down"
            chip_html += f"""
            <div class="ticker-chip">
              <div class="ticker-sym">{sym}</div>
              <div class="ticker-prc">${info['price']:,.2f}</div>
              <div class="ticker-chg {cls}">{arrow} {abs(info['pct']):.2f}%</div>
            </div>"""
    chip_html += '</div>'
    if any_chip:
        st.markdown(chip_html, unsafe_allow_html=True)

    # ── Historical chart ──────────────────────────────────────────
    chart = pd.DataFrame()
    for sym in symbols:
        s = fetch_yahoo(sym, period, interval)
        if s is not None and not s.empty:
            chart[sym] = s

    if not chart.empty:
        chart   = chart.dropna(how="all").ffill()
        # Normalise to % return for comparability
        normed  = (chart / chart.iloc[0] - 1) * 100
        st.line_chart(normed, height=230, use_container_width=True)
        st.caption(f"% return from period start · {rng} · {len(chart)} data points · Yahoo Finance")
    else:
        st.warning("Could not load chart data. Yahoo Finance may be rate-limiting — try again in a moment.")
else:
    st.info("Select at least one symbol above to show the chart.")

st.markdown("</div>", unsafe_allow_html=True)  # close stock-panel

# ══════════════════════════════════════════════════════════════════════════════
# CURRENCY PANEL — historical chart + live cards vs USD
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="fx-panel">', unsafe_allow_html=True)

fx_col1, fx_col2 = st.columns([4, 1])
with fx_col1:
    st.markdown('<div class="fx-title">Major Currencies vs USD</div>', unsafe_allow_html=True)
with fx_col2:
    fx_rng = st.selectbox("fx_range", ["1M","3M","6M","1Y"], index=0, label_visibility="collapsed", key="fx_rng")

fx_period_map   = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y"}
fx_interval_map = {"1M": "1d",  "3M": "1d",  "6M": "1d",  "1Y": "1wk"}

# Currency pairs config
FX_PAIRS = {
    "USDINR=X": {"label": "USD/INR", "flag": "🇮🇳", "name": "Indian Rupee",   "invert": False},
    "USDJPY=X": {"label": "USD/JPY", "flag": "🇯🇵", "name": "Japanese Yen",   "invert": False},
    "USDCNY=X": {"label": "USD/CNY", "flag": "🇨🇳", "name": "Chinese Yuan",   "invert": False},
    "EURUSD=X": {"label": "EUR/USD", "flag": "🇪🇺", "name": "Euro",           "invert": True},
    "GBPUSD=X": {"label": "GBP/USD", "flag": "🇬🇧", "name": "British Pound",  "invert": True},
    "USDCHF=X": {"label": "USD/CHF", "flag": "🇨🇭", "name": "Swiss Franc",    "invert": False},
}

# Build historical chart — all pairs normalised to "USD strength" (how many units of that currency per $1)
fx_chart = pd.DataFrame()
for sym, meta in FX_PAIRS.items():
    s = fetch_yahoo(sym, fx_period_map[fx_rng], fx_interval_map[fx_rng])
    if s is not None and not s.empty:
        # For EUR/USD and GBP/USD, invert so chart reads as "USD per EUR/GBP" i.e. USD cost
        if meta["invert"]:
            s = 1.0 / s
        # Normalise to % change vs period start for comparability
        s = (s / s.iloc[0] - 1) * 100
        fx_chart[meta["label"]] = s

if not fx_chart.empty:
    fx_chart = fx_chart.dropna(how="all").ffill()
    st.line_chart(fx_chart, height=220, use_container_width=True)
    st.caption(
        f"% change from {fx_rng} start · INR/JPY/CNY/CHF: USD weakening = line rises · "
        f"EUR/GBP: inverted to show USD cost · Yahoo Finance"
    )
else:
    st.warning("Currency chart unavailable — Yahoo Finance may be rate-limiting. Try again in a moment.")

# Live rate cards row
import datetime as _dt
fx_data = fetch_fx()
if fx_data:
    now_ist = _dt.datetime.utcnow() + _dt.timedelta(hours=5, minutes=30)
    cards_html = '<div class="fx-grid" style="margin-top:0.9rem;">'
    for sym, info in fx_data.items():
        rate  = info["rate"]
        pct   = info["pct"]
        arrow = "▲" if pct > 0.005 else ("▼" if pct < -0.005 else "●")
        cls   = "up" if pct > 0.005 else ("down" if pct < -0.005 else "flat")
        rate_str = f"{rate:,.2f}" if rate >= 10 else (f"{rate:.4f}" if rate >= 1 else f"{rate:.5f}")
        cards_html += f"""
        <div class="fx-card">
          <div class="fx-flag">{info['flag']}</div>
          <div class="fx-pair">{info['label']}</div>
          <div class="fx-rate">{rate_str}</div>
          <div class="fx-chg {cls}">{arrow} {abs(pct):.3f}%</div>
          <div class="fx-name">{info['name']}</div>
        </div>"""
    cards_html += f'</div><div class="fx-updated">Live · {now_ist.strftime("%H:%M")} IST · 60s cache</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # close fx-panel

# ══════════════════════════════════════════════════════════════════════════════
# CHAT SECTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="font-family:'Cormorant Garamond',serif;font-size:1.35rem;font-weight:300;
            color:#EDE8F5;margin:0.5rem 0 0.8rem;">
  Ask Anything — Markets, Currencies &amp; Documents
</div>
""", unsafe_allow_html=True)

# Empty state
if not st.session_state.messages:
    st.markdown("""
    <div class="empty">
      <div class="empty-orb">◈</div>
      <div class="empty-title">Ready without uploads</div>
      <div class="empty-sub">
        Ask about <strong>live stock prices</strong>, <strong>currency rates</strong>,
        macro trends, or comparisons — no documents needed.<br><br>
        Use <strong>＋</strong> to upload financial reports for deeper document analysis.
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
    question = st.chat_input("Ask about stocks, currencies, or your documents…")

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
        with st.spinner("Thinking…"):
            try:
                from openai import OpenAI
                oai = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

                # ── 1. Live market context (always injected) ──────────────
                live_stocks_lines = []
                for sym in symbols:
                    info = fetch_quote(sym)
                    if info:
                        arrow = "▲" if info["pct"] >= 0 else "▼"
                        live_stocks_lines.append(
                            f"  {sym}: ${info['price']:,.2f}  ({arrow}{abs(info['pct']):.2f}% today)"
                        )
                live_stocks_str = "\n".join(live_stocks_lines) if live_stocks_lines else "  (no stocks selected)"

                live_fx_lines = []
                fx_now = fetch_fx()
                if fx_now:
                    for sym, info in fx_now.items():
                        arrow = "▲" if info["pct"] > 0 else ("▼" if info["pct"] < 0 else "●")
                        rate_str = f"{info['rate']:,.2f}" if info["rate"] >= 10 else f"{info['rate']:.4f}"
                        live_fx_lines.append(
                            f"  {info['label']}: {rate_str}  ({arrow}{abs(info['pct']):.3f}% today)"
                        )
                live_fx_str = "\n".join(live_fx_lines) if live_fx_lines else "  (unavailable)"

                import datetime as _dt
                utc_now = _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

                live_market_context = f"""
=== LIVE MARKET DATA (as of {utc_now}) ===

STOCKS:
{live_stocks_str}

CURRENCIES (vs USD):
{live_fx_str}
""".strip()

                # ── 2. Document RAG context (only if docs ingested) ───────
                doc_context  = ""
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
                    doc_context = "\n---\n".join(f"[{m['filename']}]\n{c}" for c, m in zip(cks, mts))
                    sources_data = [
                        {"filename": m["filename"], "score": round(1 - d / 2, 3), "preview": c[:220]}
                        for c, m, d in zip(cks, mts, dts)
                    ]

                # ── 3. Build final user message ───────────────────────────
                if doc_context:
                    user_msg = (
                        f"{live_market_context}\n\n"
                        f"=== DOCUMENT CONTEXT ===\n{doc_context}\n\n"
                        f"Question: {q}"
                    )
                else:
                    user_msg = f"{live_market_context}\n\nQuestion: {q}"

                # ── 4. System prompt ──────────────────────────────────────
                system_prompt = """You are an expert financial analyst and markets assistant with real-time data access.

You have been given:
1. LIVE MARKET DATA — current stock prices and currency exchange rates (refreshed every 60s).
2. DOCUMENT CONTEXT — if the user has uploaded financial documents, relevant excerpts are included.

Behaviour rules:
- For questions about stocks, currencies, markets, FX rates, or macroeconomics: answer using the live market data provided. You do NOT need documents for this — the live data is sufficient.
- For questions about uploaded documents (earnings, 10-Ks, annual reports): use the document context and cite specific numbers and dates.
- If both live data and document context are relevant, combine them intelligently.
- If asked to compare currencies or stocks, use the live rates/prices provided.
- Always be concise, precise, and cite the data you're referencing.
- If information is genuinely missing from both sources, say so clearly — never hallucinate numbers."""

                # ── 5. Call LLM ───────────────────────────────────────────
                # Build messages with chat history for multi-turn context
                history_msgs = []
                for m in st.session_state.messages[:-1]:  # exclude current user msg
                    history_msgs.append({"role": m["role"], "content": m["content"]})

                resp = oai.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *history_msgs,
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=0.15,
                    max_tokens=1500,
                )
                answer = resp.choices[0].message.content
                tokens = resp.usage.total_tokens

                st.markdown(answer)

                if sources_data:
                    with st.expander(f"↳ {len(sources_data)} document source(s)"):
                        for src in sources_data:
                            st.markdown(f"""
                            <div class="src-card">
                              <div class="src-name">📄 {src['filename']}</div>
                              <div class="src-score">relevance: {src['score']}</div>
                              <div class="src-preview">{src['preview']}…</div>
                            </div>""", unsafe_allow_html=True)

                st.caption(f"llama-3.3-70b-versatile · {tokens} tokens · live data injected")
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
