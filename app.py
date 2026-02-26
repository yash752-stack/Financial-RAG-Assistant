"""
app.py — Financial RAG Assistant
Royal Velvet & Black Theme  |  v4
Run: streamlit run app.py
"""

import os
import datetime as _dt
from datetime import date, timedelta
import requests
import pandas as pd
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
  --red:        #F87171;
  --gold:       #F0C040;
}

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Syne', sans-serif !important; color: var(--text) !important; }

.stApp, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(ellipse 110% 55% at 0% 0%, rgba(107,45,107,0.20) 0%, transparent 55%),
    radial-gradient(ellipse  80% 50% at 100% 100%, rgba(107,45,107,0.14) 0%, transparent 55%),
    var(--black) !important;
}
[data-testid="stMain"], [data-testid="block-container"] {
  background: transparent !important; padding-top: 0 !important; max-width: 1120px !important;
}
[data-testid="stSidebar"] {
  background: var(--panel) !important;
  border-right: 1px solid var(--border-l) !important;
  box-shadow: 4px 0 40px rgba(107,45,107,0.08) !important;
}
[data-testid="stSidebar"] > div { padding: 1.4rem 1.2rem !important; }

h1,h2,h3,h4 { font-family: 'Cormorant Garamond', serif !important; color: var(--text) !important; }
code, pre { font-family: 'Space Mono', monospace !important; }

[data-testid="stMetric"] { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; padding: 0.9rem 1rem !important; }
[data-testid="stMetricLabel"] p { font-family: 'Space Mono', monospace !important; font-size: 0.58rem !important; color: var(--text-ghost) !important; text-transform: uppercase !important; letter-spacing: 0.18em !important; }
[data-testid="stMetricValue"] { font-family: 'Cormorant Garamond', serif !important; font-size: 1.7rem !important; font-weight: 300 !important; color: var(--accent) !important; }

.stButton > button { background: transparent !important; border: 1px solid var(--border) !important; border-radius: 6px !important; color: var(--text-dim) !important; font-family: 'Syne', sans-serif !important; font-size: 0.8rem !important; transition: all 0.22s ease !important; text-align: left !important; }
.stButton > button:hover { background: rgba(107,45,107,0.14) !important; border-color: var(--velvet-gl) !important; color: var(--accent) !important; box-shadow: 0 0 18px rgba(107,45,107,0.22) !important; transform: translateY(-1px) !important; }

.stTextInput input, .stTextArea textarea { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; color: var(--text) !important; font-family: 'Syne', sans-serif !important; font-size: 0.88rem !important; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color: var(--velvet-l) !important; box-shadow: 0 0 0 2px rgba(107,45,107,0.25) !important; }
.stTextInput input::placeholder { color: var(--text-ghost) !important; }

[data-testid="stChatInput"] { background: var(--card-2) !important; border: 1px solid var(--border-l) !important; border-radius: 14px !important; box-shadow: 0 0 30px rgba(107,45,107,0.12) !important; }
[data-testid="stChatInput"] textarea { background: transparent !important; border: none !important; box-shadow: none !important; color: var(--text) !important; font-family: 'Syne', sans-serif !important; }
[data-testid="stChatInput"] textarea::placeholder { color: var(--text-ghost) !important; }
[data-testid="stChatInput"]:focus-within { border-color: rgba(139,58,139,0.7) !important; box-shadow: 0 0 30px rgba(107,45,107,0.22) !important; }

[data-testid="stChatMessage"] { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; padding: 0.8rem 1rem !important; margin-bottom: 0.5rem !important; }
[data-testid="stFileUploader"] { background: rgba(107,45,107,0.05) !important; border: 1.5px dashed rgba(139,58,139,0.4) !important; border-radius: 10px !important; }
[data-testid="stExpander"] { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; }
[data-testid="stExpander"] summary { background: transparent !important; font-family: 'Space Mono', monospace !important; font-size: 0.65rem !important; letter-spacing: 0.06em !important; color: var(--text-ghost) !important; border: none !important; }
[data-testid="stAlert"] { background: rgba(107,45,107,0.1) !important; border: 1px solid var(--border-l) !important; border-radius: 8px !important; color: var(--lilac) !important; }
div[data-testid="stSuccess"] { background: rgba(74,222,128,0.07) !important; border-color: rgba(74,222,128,0.25) !important; color: #86efac !important; }
div[data-testid="stError"] { background: rgba(248,113,113,0.07) !important; border-color: rgba(248,113,113,0.25) !important; color: #fca5a5 !important; }
.stProgress > div > div { background: linear-gradient(90deg, var(--velvet), var(--accent)) !important; }
[data-testid="stMultiSelect"] > div { background: var(--card) !important; border-color: var(--border) !important; border-radius: 8px !important; }
.stMultiSelect span[data-baseweb="tag"] { background: rgba(107,45,107,0.3) !important; border: 1px solid var(--velvet-gl) !important; color: var(--lilac) !important; border-radius: 999px !important; font-size: 0.72rem !important; }
[data-testid="stSelectbox"] > div > div { background: var(--card) !important; border-color: var(--border) !important; border-radius: 8px !important; color: var(--text) !important; }
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-thumb { background: rgba(107,45,107,0.35); border-radius: 2px; }

/* ── HERO ── */
.rag-header { position: relative; padding: 2rem 2.2rem; background: linear-gradient(135deg, rgba(107,45,107,0.22) 0%, rgba(13,11,18,0.98) 55%, rgba(107,45,107,0.12) 100%); border: 1px solid rgba(255,255,255,0.08); border-radius: 18px; box-shadow: 0 8px 40px rgba(0,0,0,0.4); margin-bottom: 1.4rem; overflow: hidden; }
.rag-header::before { content: ''; position: absolute; top: -80px; right: -80px; width: 280px; height: 280px; border-radius: 50%; background: radial-gradient(circle, rgba(107,45,107,0.25) 0%, transparent 70%); pointer-events: none; }
.rag-header::after { content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent 0%, rgba(107,45,107,0.6) 30%, rgba(192,132,200,0.8) 50%, rgba(107,45,107,0.6) 70%, transparent 100%); }
.rag-kicker { font-family: 'Space Mono', monospace; font-size: 0.6rem; letter-spacing: 0.3em; color: var(--velvet-gl); text-transform: uppercase; margin-bottom: 0.9rem; display: flex; align-items: center; gap: 0.6rem; }
.rag-kicker::before { content: ''; display: inline-block; width: 20px; height: 1px; background: var(--velvet-gl); opacity: 0.6; }
.rag-header h1 { font-family: 'Cormorant Garamond', serif !important; font-size: 3.2rem !important; font-weight: 300 !important; line-height: 1.0 !important; color: var(--text) !important; margin: 0 0 0.2rem !important; letter-spacing: -0.02em !important; }
.rag-header h1 em { font-style: italic; background: linear-gradient(135deg, var(--velvet-gl) 0%, var(--accent) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.rag-header p { font-family: 'Syne', sans-serif; font-size: 0.86rem; color: var(--text-dim); margin: 0.6rem 0 0 !important; max-width: 480px; }
.badge-row { display: flex; gap: 0.4rem; margin-top: 0.9rem; flex-wrap: wrap; }
.badge { font-family: 'Space Mono', monospace; font-size: 0.62rem; letter-spacing: 0.08em; padding: 0.2rem 0.55rem; border-radius: 999px; border: 1px solid var(--border); color: var(--text-ghost); background: rgba(255,255,255,0.04); }
.badge.v { border-color: rgba(139,58,139,0.5); color: var(--accent); background: rgba(107,45,107,0.12); }
.badge.g { border-color: rgba(74,222,128,0.3); color: #86efac; background: rgba(74,222,128,0.07); }

/* ── STAT STRIP ── */
.stat-strip { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: rgba(107,45,107,0.22); border-radius: 10px; overflow: hidden; border: 1px solid rgba(107,45,107,0.22); margin-bottom: 1.4rem; }
.stat-cell { background: var(--card); padding: 1rem 1.2rem; position: relative; transition: background 0.25s; }
.stat-cell:hover { background: var(--card-2); }
.stat-cell::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, var(--velvet), var(--accent)); opacity: 0; transition: opacity 0.25s; }
.stat-cell:hover::before { opacity: 1; }
.stat-lbl { font-family: 'Space Mono', monospace; font-size: 0.52rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--text-ghost); margin-bottom: 0.4rem; }
.stat-val { font-family: 'Cormorant Garamond', serif; font-size: 1.7rem; font-weight: 300; color: var(--text); line-height: 1; }
.stat-val.active { color: var(--accent); }
.stat-val-mono { font-family: 'Space Mono', monospace; font-size: 0.68rem; color: var(--accent); line-height: 1.4; }

/* ── MARKET MOOD BAR ── */
.mood-bar-wrap { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1rem 1.4rem; margin-bottom: 1.4rem; }
.mood-title { font-family: 'Space Mono', monospace; font-size: 0.58rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--velvet-gl); margin-bottom: 0.7rem; }
.mood-track { height: 6px; border-radius: 3px; background: linear-gradient(90deg, #f87171 0%, #fb923c 25%, #facc15 50%, #86efac 75%, #4ade80 100%); position: relative; margin-bottom: 0.5rem; }
.mood-needle { position: absolute; top: -5px; width: 16px; height: 16px; border-radius: 50%; border: 2px solid #fff; background: var(--accent); transform: translateX(-50%); box-shadow: 0 0 8px rgba(192,132,200,0.6); transition: left 0.5s ease; }
.mood-labels { display: flex; justify-content: space-between; font-family: 'Space Mono', monospace; font-size: 0.5rem; color: var(--text-ghost); }
.mood-index { font-family: 'Cormorant Garamond', serif; font-size: 2rem; font-weight: 300; color: var(--text); }
.mood-label { font-family: 'Space Mono', monospace; font-size: 0.62rem; letter-spacing: 0.1em; margin-left: 0.5rem; }
.mood-indices { display: flex; gap: 1rem; margin-top: 0.8rem; flex-wrap: wrap; }
.mood-idx-chip { display: flex; flex-direction: column; background: var(--card-2); border: 1px solid var(--border); border-radius: 8px; padding: 0.4rem 0.8rem; font-family: 'Space Mono', monospace; min-width: 90px; }
.mood-idx-name { font-size: 0.52rem; color: var(--text-ghost); letter-spacing: 0.1em; }
.mood-idx-val  { font-size: 0.72rem; color: var(--text); margin-top: 0.1rem; }
.mood-idx-chg.up   { font-size: 0.56rem; color: #4ade80; }
.mood-idx-chg.down { font-size: 0.56rem; color: #f87171; }

/* ── NEWS ── */
.news-panel { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.1rem 1.4rem; margin-bottom: 1.4rem; }
.news-title { font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; font-weight: 300; color: var(--text); margin-bottom: 0.9rem; display: flex; align-items: center; gap: 0.5rem; }
.news-title::before { content: ''; display: inline-block; width: 3px; height: 1.1rem; background: linear-gradient(180deg, var(--velvet), var(--accent)); border-radius: 2px; }
.news-card { border-left: 2px solid var(--velvet-gl); padding: 0.6rem 0.8rem; margin-bottom: 0.5rem; background: var(--card-2); border-radius: 0 8px 8px 0; transition: border-left-color 0.2s; }
.news-card:hover { border-left-color: var(--accent); }
.news-src { font-family: 'Space Mono', monospace; font-size: 0.52rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--velvet-gl); margin-bottom: 0.2rem; }
.news-hl { font-family: 'Syne', sans-serif; font-size: 0.82rem; color: var(--text); line-height: 1.45; }
.news-hl a { color: var(--text) !important; text-decoration: none; }
.news-hl a:hover { color: var(--accent) !important; }
.news-time { font-family: 'Space Mono', monospace; font-size: 0.5rem; color: var(--text-ghost); margin-top: 0.2rem; }

/* ── COMMODITIES ── */
.comm-panel { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.1rem 1.4rem 0.9rem; margin-bottom: 1.4rem; }
.comm-title { font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; font-weight: 300; color: var(--text); margin-bottom: 0.9rem; display: flex; align-items: center; gap: 0.5rem; }
.comm-title::before { content: ''; display: inline-block; width: 3px; height: 1.1rem; background: linear-gradient(180deg, #F0C040, #C084C8); border-radius: 2px; }

/* ── CRYPTO ── */
.crypto-panel { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.1rem 1.4rem 0.9rem; margin-bottom: 1.4rem; }
.crypto-title { font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; font-weight: 300; color: var(--text); margin-bottom: 0.9rem; display: flex; align-items: center; gap: 0.5rem; }
.crypto-title::before { content: ''; display: inline-block; width: 3px; height: 1.1rem; background: linear-gradient(180deg, #fb923c, #C084C8); border-radius: 2px; }

/* ── PRICE CHIP (reusable) ── */
.price-chip { display: flex; flex-direction: column; background: var(--card-2); border: 1px solid var(--border); border-radius: 10px; padding: 0.75rem 1rem; min-width: 120px; font-family: 'Space Mono', monospace; transition: border-color 0.2s; }
.price-chip:hover { border-color: var(--border-l); }
.pc-sym  { font-size: 0.6rem; color: var(--accent); font-weight: 700; letter-spacing: 0.08em; white-space: nowrap; }
.pc-name { font-size: 0.5rem; color: var(--text-ghost); margin-bottom: 0.2rem; }
.pc-val  { font-family: 'Cormorant Garamond', serif; font-size: 1.5rem; font-weight: 300; color: var(--text); line-height: 1; }
.pc-chg.up   { font-size: 0.58rem; color: #4ade80; margin-top: 0.1rem; }
.pc-chg.down { font-size: 0.58rem; color: #f87171; margin-top: 0.1rem; }
.pc-chg.flat { font-size: 0.58rem; color: var(--text-ghost); margin-top: 0.1rem; }
.chips-row { display: flex; gap: 0.6rem; flex-wrap: wrap; }

/* ── FX panel ── */
.fx-panel { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.1rem 1.4rem 0.9rem; margin-bottom: 1.4rem; }
.fx-panel-title { font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; font-weight: 300; color: var(--text); margin-bottom: 0.9rem; display: flex; align-items: center; gap: 0.5rem; }
.fx-panel-title::before { content: ''; display: inline-block; width: 3px; height: 1.1rem; background: linear-gradient(180deg, var(--velvet), var(--accent)); border-radius: 2px; }

/* ── MISC ── */
.sb-lbl { font-family: 'Space Mono', monospace; font-size: 0.54rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--velvet-gl); padding: 1.2rem 0 0.45rem; border-top: 1px solid var(--border); margin-top: 0.5rem; }
.key-ok { display: flex; align-items: center; gap: 0.5rem; background: rgba(74,222,128,0.07); border: 1px solid rgba(74,222,128,0.2); color: #86efac; padding: 0.38rem 0.7rem; border-radius: 6px; font-family: 'Space Mono', monospace; font-size: 0.6rem; letter-spacing: 0.1em; }
.key-dot { width: 5px; height: 5px; border-radius: 50%; background: #4ade80; box-shadow: 0 0 6px #4ade80; animation: blink 2s infinite; }
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.3;} }
.doc-pill { display: flex; align-items: center; gap: 0.4rem; background: rgba(107,45,107,0.1); border: 1px solid var(--border); padding: 0.32rem 0.65rem; border-radius: 4px; margin-bottom: 0.3rem; font-family: 'Space Mono', monospace; font-size: 0.58rem; color: var(--text-dim); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.doc-dot { width:4px; height:4px; border-radius:50%; background:var(--velvet-gl); flex-shrink:0; }
.empty { text-align: center; padding: 4rem 2rem; }
.empty-orb { width: 100px; height: 100px; border-radius: 50%; background: radial-gradient(circle, rgba(107,45,107,0.28) 0%, transparent 70%); border: 1px solid var(--border); margin: 0 auto 1.5rem; display: flex; align-items: center; justify-content: center; font-size: 2rem; color: var(--velvet-gl); }
.empty-title { font-family: 'Cormorant Garamond', serif; font-size: 1.7rem; font-weight: 300; font-style: italic; color: var(--text-ghost); margin-bottom: 0.5rem; }
.empty-sub { font-size: 0.8rem; color: var(--text-ghost); max-width: 300px; margin: 0 auto; line-height: 1.8; opacity: 0.7; }
.upload-drawer { background: linear-gradient(135deg, rgba(107,45,107,0.18) 0%, rgba(13,11,18,0.95) 100%); border: 1px solid rgba(139,58,139,0.45); border-radius: 12px; padding: 1rem 1.1rem 0.7rem; margin-bottom: 0.6rem; animation: slideDown 0.2s ease; }
.upload-drawer-title { font-family: 'Space Mono', monospace; font-size: 0.62rem; letter-spacing: 0.15em; text-transform: uppercase; color: var(--velvet-gl); margin-bottom: 0.6rem; }
@keyframes slideDown { from{opacity:0;transform:translateY(-6px);} to{opacity:1;transform:translateY(0);} }
.src-card { background: var(--card); border: 1px solid var(--border); border-left: 3px solid var(--velvet-gl); border-radius: 0 8px 8px 0; padding: 0.7rem 0.9rem; margin: 0.4rem 0; font-size: 0.82rem; transition: border-left-color 0.2s; }
.src-card:hover { border-left-color: var(--accent); background: var(--card-2); }
.src-name { font-family: 'Space Mono', monospace; font-size: 0.7rem; color: var(--accent); margin-bottom: 0.15rem; }
.src-score { font-family: 'Space Mono', monospace; font-size: 0.62rem; color: var(--text-ghost); }
.src-preview { color: var(--text-dim); line-height: 1.55; margin-top: 0.2rem; }
.vfooter { text-align: center; padding: 1.8rem 0 0.5rem; position: relative; margin-top: 2.5rem; }
.vfooter::before { content: ''; position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 180px; height: 1px; background: linear-gradient(90deg, transparent, rgba(107,45,107,0.5), transparent); }
.vfooter-text { font-family: 'Space Mono', monospace; font-size: 0.56rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--text-ghost); }
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
# DATA FETCH HELPERS
# ══════════════════════════════════════════════════════════════════════════════
_HEADERS = {"User-Agent": "Mozilla/5.0"}

@st.cache_data(ttl=300)
def fetch_yahoo_series(symbol: str, period: str, interval: str):
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?range={period}&interval={interval}&includePrePost=false"
    )
    try:
        r = requests.get(url, headers=_HEADERS, timeout=10)
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
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=2d&interval=1d"
    try:
        r    = requests.get(url, headers=_HEADERS, timeout=8)
        r.raise_for_status()
        data = r.json()
        res  = data["chart"]["result"][0]
        q    = [x for x in res["indicators"]["quote"][0]["close"] if x is not None]
        if not q:
            return None
        pct  = (q[-1] - q[-2]) / q[-2] * 100 if len(q) >= 2 else 0.0
        return {"price": q[-1], "pct": pct}
    except Exception:
        return None

@st.cache_data(ttl=60)
def fetch_multi_quotes(symbols: tuple):
    """Fetch multiple quotes efficiently."""
    results = {}
    for sym in symbols:
        info = fetch_quote(sym)
        if info:
            results[sym] = info
    return results

def _parse_rss_text(text, source_name, max_items):
    import re, html as _html
    results = []
    items = re.findall(r"<item[^>]*>(.*?)</item>", text, re.DOTALL)
    if not items:
        items = re.findall(r"<entry[^>]*>(.*?)</entry>", text, re.DOTALL)
    for item in items[:max_items]:
        title_m = re.search(r"<title[^>]*>(.*?)</title>", item, re.DOTALL | re.IGNORECASE)
        link_m  = re.search(r'<link[^>]*href=["\'](https?://[^"\' ]+)["\']', item, re.DOTALL | re.IGNORECASE)
        if not link_m:
            link_m = re.search(r"<link[^>]*>\s*(https?://[^\s<\"]+)", item, re.DOTALL | re.IGNORECASE)
        if not link_m:
            link_m = re.search(r"<link>(.*?)</link>", item, re.DOTALL | re.IGNORECASE)
        date_m  = re.search(r"<pubDate[^>]*>(.*?)</pubDate>|<published[^>]*>(.*?)</published>", item, re.IGNORECASE | re.DOTALL)
        raw = title_m.group(1).strip() if title_m else ""
        cdata = re.match(r"<!\[CDATA\[(.*?)\]\]>", raw, re.DOTALL)
        title = cdata.group(1).strip() if cdata else raw
        title = _html.unescape(re.sub(r"<[^>]+>", "", title)).strip()
        link  = (link_m.group(1) or "").strip() if link_m else "#"
        if not link.startswith("http"):
            link = "#"
        grp = ""
        if date_m:
            grp = date_m.group(1) or date_m.group(2) or ""
        pub = grp.strip()[:22]
        if title and len(title) > 8:
            results.append({"title": title, "link": link, "pub": pub, "source": source_name})
    return results


@st.cache_data(ttl=300)
def fetch_gnews(query, source_label, max_items=5):
    import urllib.parse
    q_enc = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={q_enc}&hl=en-US&gl=US&ceid=US:en"
    try:
        r = requests.get(url, headers=_HEADERS, timeout=10)
        r.raise_for_status()
        return _parse_rss_text(r.text, source_label, max_items)
    except Exception:
        return []


@st.cache_data(ttl=300)
def fetch_news_rss(feed_url, source_name, max_items=4):
    try:
        hdrs = {**_HEADERS, "Accept": "application/rss+xml,application/xml,text/xml,*/*"}
        r = requests.get(feed_url, headers=hdrs, timeout=8)
        r.raise_for_status()
        results = _parse_rss_text(r.text, source_name, max_items)
        if results:
            return results
    except Exception:
        pass
    return fetch_gnews(f"{source_name} finance economy", source_name, max_items)


@st.cache_data(ttl=300)
def fetch_fear_greed():
    """Fetch CNN Fear & Greed index via alternative.me (crypto) as fallback proxy."""
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", headers=_HEADERS, timeout=8)
        data = r.json()
        val = int(data["data"][0]["value"])
        label = data["data"][0]["value_classification"]
        return {"value": val, "label": label}
    except Exception:
        return {"value": 50, "label": "Neutral"}


def make_chip_html(sym: str, name: str, price: float, pct: float,
                   prefix: str = "$", suffix: str = "", decimals: int = 2,
                   icon: str = "") -> str:
    """Render a single price chip as HTML string (no nested f-string quotes)."""
    arrow = "▲" if pct > 0.005 else ("▼" if pct < -0.005 else "●")
    chg_class = "up" if pct > 0.005 else ("down" if pct < -0.005 else "flat")
    if price >= 1000:
        price_str = prefix + f"{price:,.{decimals}f}" + suffix
    elif price >= 1:
        price_str = prefix + f"{price:,.{decimals}f}" + suffix
    else:
        price_str = prefix + f"{price:.6f}" + suffix
    pct_str = f"{arrow} {abs(pct):.2f}%"
    icon_html = f'<span style="font-size:1rem;margin-right:0.2rem;">{icon}</span>' if icon else ""
    return (
        '<div class="price-chip">'
        f'<div class="pc-sym">{icon_html}{sym}</div>'
        f'<div class="pc-name">{name}</div>'
        f'<div class="pc-val">{price_str}</div>'
        f'<div class="pc-chg {chg_class}">{pct_str}</div>'
        '</div>'
    )

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

    model  = load_model()
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
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.4rem;font-weight:300;color:#EDE8F5;line-height:1.1;">
        RAG <em style="color:#C084C8;font-style:italic;">Assistant</em>
      </div>
      <div style="font-family:'Space Mono',monospace;font-size:0.52rem;letter-spacing:0.22em;color:#4A3858;text-transform:uppercase;margin-top:0.35rem;">
        Financial Intelligence · v4
      </div>
    </div>
    """, unsafe_allow_html=True)

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

    if st.session_state.file_names:
        st.markdown('<div class="sb-lbl">Knowledge Base</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Chunks", st.session_state.chunk_count)
        c2.metric("Docs", st.session_state.uploaded_docs)
        for fn in st.session_state.file_names:
            short = fn[:22] + "…" if len(fn) > 22 else fn
            st.markdown(f'<div class="doc-pill"><div class="doc-dot"></div>{short}</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-lbl">Quick Ask</div>', unsafe_allow_html=True)
    for q_item in [
        "What is USD/INR today?",
        "Compare INR vs JPY vs Yuan",
        "Gold price today?",
        "Bitcoin vs Ethereum?",
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

# ── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="rag-header">
  <div class="rag-kicker">Financial Intelligence Platform</div>
  <h1>Interrogate Your<br><em>Financial Documents</em></h1>
  <p>Semantic search and AI-powered analysis across Annual Reports,
     10-Ks &amp; Earnings Transcripts. Live markets &amp; crypto always on.</p>
  <div class="badge-row">
    <span class="badge v">Semantic Retrieval</span>
    <span class="badge v">Source-backed Answers</span>
    <span class="badge v">Llama 3.3 · 70B</span>
    <span class="badge">Groq</span>
    <span class="badge g">Live Data</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── STAT STRIP ────────────────────────────────────────────────────────────────
chunks = st.session_state.chunk_count
docs   = st.session_state.uploaded_docs
msgs   = len(st.session_state.messages) // 2
st.markdown(f"""
<div class="stat-strip">
  <div class="stat-cell"><div class="stat-lbl">Model</div><div class="stat-val-mono">Llama 3.3 · 70B</div></div>
  <div class="stat-cell"><div class="stat-lbl">Chunks Indexed</div><div class="stat-val {'active' if chunks else ''}">{chunks if chunks else '—'}</div></div>
  <div class="stat-cell"><div class="stat-lbl">Documents</div><div class="stat-val {'active' if docs else ''}">{docs if docs else '—'}</div></div>
  <div class="stat-cell"><div class="stat-lbl">Exchanges</div><div class="stat-val {'active' if msgs else ''}">{msgs if msgs else '—'}</div></div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MARKET MOOD BAR  (Fear & Greed + major global indices)
# ══════════════════════════════════════════════════════════════════════════════
fng = fetch_fear_greed()
fng_val   = fng["value"]
fng_label = fng["label"]
needle_pct = fng_val  # 0–100

# Major global indices: S&P, NASDAQ, FTSE 100, NIFTY 50, Nikkei
INDEX_SYMS = {
    "^GSPC":  {"name": "S&P 500",   "flag": "🇺🇸"},
    "^IXIC":  {"name": "NASDAQ",    "flag": "🇺🇸"},
    "^FTSE":  {"name": "FTSE 100",  "flag": "🇬🇧"},
    "^NSEI":  {"name": "NIFTY 50",  "flag": "🇮🇳"},
    "^N225":  {"name": "Nikkei",    "flag": "🇯🇵"},
    "^GDAXI": {"name": "DAX",       "flag": "🇩🇪"},
}

idx_quotes = fetch_multi_quotes(tuple(INDEX_SYMS.keys()))

idx_chips_html = ""
for sym, meta in INDEX_SYMS.items():
    info = idx_quotes.get(sym)
    if info:
        arrow = "▲" if info["pct"] >= 0 else "▼"
        chg_class = "up" if info["pct"] >= 0 else "down"
        idx_chips_html += (
            '<div class="mood-idx-chip">'
            f'<div class="mood-idx-name">{meta["flag"]} {meta["name"]}</div>'
            f'<div class="mood-idx-val">{info["price"]:,.0f}</div>'
            f'<div class="mood-idx-chg {chg_class}">{arrow} {abs(info["pct"]):.2f}%</div>'
            '</div>'
        )

# Mood colour
if fng_val < 25:
    mood_color = "#f87171"
elif fng_val < 45:
    mood_color = "#fb923c"
elif fng_val < 55:
    mood_color = "#facc15"
elif fng_val < 75:
    mood_color = "#86efac"
else:
    mood_color = "#4ade80"

st.markdown(f"""
<div class="mood-bar-wrap">
  <div class="mood-title">◈ Market Mood &amp; Global Indices</div>
  <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.7rem;">
    <div>
      <div style="display:flex;align-items:baseline;gap:0.4rem;">
        <span class="mood-index" style="color:{mood_color};">{fng_val}</span>
        <span class="mood-label" style="color:{mood_color};">{fng_label}</span>
      </div>
      <div style="font-family:'Space Mono',monospace;font-size:0.5rem;color:#4A3858;margin-top:0.2rem;">
        Crypto Fear &amp; Greed · alternative.me
      </div>
    </div>
    <div style="flex:1;">
      <div class="mood-track">
        <div class="mood-needle" style="left:{needle_pct}%;"></div>
      </div>
      <div class="mood-labels">
        <span>Extreme Fear</span><span>Fear</span><span>Neutral</span><span>Greed</span><span>Extreme Greed</span>
      </div>
    </div>
  </div>
  <div class="mood-indices">{idx_chips_html}</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# FINANCIAL HEADLINES + POLICY — pure Python HTML render, no JS dependency
# ═══════════════════════════════════════════════════════════════════════════
import datetime as _dtnow, html as _html_mod

_TODAY = _dtnow.datetime.now(_dtnow.timezone.utc).strftime("%b %d, %Y")

NEWS_ITEMS = [
    ("Fed signals rates on hold as inflation data stays elevated",        "https://www.bloomberg.com/markets", "Bloomberg",           "#4ADE80", ""),
    ("S&P 500 edges higher on strong tech earnings outlook",              "https://www.wsj.com/markets",       "Wall Street Journal", "#F0C040", ""),
    ("Oil prices climb as OPEC+ reaffirms production cuts",              "https://www.ft.com",                "Financial Times",     "#FB923C", ""),
    ("Gold hits multi-month high amid dollar weakness",                   "https://www.bloomberg.com/markets", "Bloomberg",           "#4ADE80", ""),
    ("China PMI beats expectations, lifting Asian stocks",                "https://www.economist.com",         "The Economist",       "#C084C8", ""),
    ("Bitcoin surges past key resistance as ETF inflows accelerate",      "https://www.wsj.com/finance",       "Wall Street Journal", "#F0C040", ""),
    ("Euro weakens as ECB minutes reveal rate cut discussions",           "https://www.ft.com",                "Financial Times",     "#FB923C", ""),
    ("India markets near record high ahead of budget announcement",       "https://www.bloomberg.com",         "Bloomberg",           "#4ADE80", ""),
    ("US Treasury yields rise on stronger-than-expected jobs data",       "https://www.wsj.com/markets",       "Wall Street Journal", "#F0C040", ""),
    ("Japanese yen weakens as Bank of Japan holds ultra-loose policy",    "https://www.economist.com",         "The Economist",       "#C084C8", ""),
]

POLICY_ITEMS = [
    ("Federal Reserve holds rates steady, cites inflation progress",         "https://www.federalreserve.gov/newsevents.htm",          "Federal Reserve",       "🇺🇸", "#60A5FA"),
    ("ECB signals rate cut in coming months as inflation cools",             "https://www.ecb.europa.eu/press",                        "European Central Bank", "🇪🇺", "#34D399"),
    ("Bank of England holds rate at 5.25%, watching wage growth closely",   "https://www.bankofengland.co.uk/monetary-policy",        "Bank of England",       "🇬🇧", "#F472B6"),
    ("IMF upgrades global growth forecast, warns of inflation risks",        "https://www.imf.org/en/News",                            "IMF",                   "🌐", "#A78BFA"),
    ("RBI holds repo rate at 6.5%, maintains accommodation withdrawal",     "https://www.rbi.org.in",                                "RBI India",             "🇮🇳", "#FB923C"),
    ("Bank of Japan hints at policy normalisation as wages rise",            "https://www.boj.or.jp/en",                              "Bank of Japan",         "🇯🇵", "#A78BFA"),
    ("US Treasury announces new debt issuance amid deficit concerns",        "https://home.treasury.gov/news",                         "US Treasury",           "🇺🇸", "#FBBF24"),
    ("China PBOC cuts reserve requirement ratio to boost bank lending",      "https://www.pbc.gov.cn/en",                             "PBOC China",            "🇨🇳", "#38BDF8"),
    ("World Bank raises $5bn in sustainability bonds for emerging markets",  "https://www.worldbank.org/en/news",                      "World Bank",            "🌍", "#4ADE80"),
    ("UK Chancellor sets out fiscal rules amid debt ceiling concerns",       "https://www.gov.uk/government/organisations/hm-treasury","UK Government",         "🇬🇧", "#F9A8D4"),
]

def _car_css():
    return """
<style>
.xcar{background:#0D0B12;border-radius:14px;padding:1.2rem 1.6rem 1.2rem;margin-bottom:1.2rem;position:relative;}
.xcar.xnews{border:1px solid rgba(139,58,139,0.25);}
.xcar.xpol{border:1px solid rgba(96,165,250,0.25);}
.xcar.xpol::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,rgba(96,165,250,0.5),rgba(167,139,250,0.5),transparent);}
.xcar-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:0.9rem;}
.xcar-ttl{font-family:'Cormorant Garamond',serif;font-size:1.1rem;font-weight:300;color:#EDE8F5;
  display:flex;align-items:center;gap:0.5rem;}
.xcar-ttl.xnews::before{content:'';display:inline-block;width:3px;height:1.1rem;
  background:linear-gradient(180deg,#6B2D6B,#C084C8);border-radius:2px;}
.xcar-ttl.xpol::before{content:'';display:inline-block;width:3px;height:1.1rem;
  background:linear-gradient(180deg,#3B82F6,#A78BFA);border-radius:2px;}
.xcar-sub{font-family:'Space Mono',monospace;font-size:0.49rem;letter-spacing:0.15em;
  text-transform:uppercase;color:#374151;margin-left:0.4rem;}
.xslides{position:relative;overflow:hidden;min-height:100px;}
.xslide{display:none;}
.xslide.xactive{display:block;}
.xcard{border-radius:0 12px 12px 0;padding:0.85rem 1.1rem;}
.xcard.xcn{background:#120E1A;border:1px solid rgba(139,58,139,0.18);}
.xcard.xcp{background:#0A0F1E;border:1px solid rgba(96,165,250,0.15);}
.xcard-src{font-family:'Space Mono',monospace;font-size:0.53rem;letter-spacing:0.13em;
  text-transform:uppercase;margin-bottom:0.35rem;display:flex;align-items:center;gap:0.4rem;}
.xbadge{font-size:0.41rem;background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.25);
  color:#93C5FD;padding:0.05rem 0.28rem;border-radius:3px;margin-left:auto;}
.xcard-ttl{font-family:'Syne',sans-serif;font-size:0.95rem;font-weight:500;color:#EDE8F5;
  line-height:1.5;text-decoration:none;display:block;margin-bottom:0.3rem;}
.xcard-ttl:hover{text-decoration:underline;text-underline-offset:3px;}
.xcard-dt{font-family:'Space Mono',monospace;font-size:0.47rem;color:#374151;}
.xprog{height:2px;border-radius:1px;margin-top:0.85rem;overflow:hidden;}
.xprog.xnp{background:rgba(139,58,139,0.15);}
.xprog.xpp{background:rgba(59,130,246,0.12);}
.xprogbar{height:100%;border-radius:1px;width:0%;}
.xprogbar.xnpb{background:linear-gradient(90deg,#6B2D6B,#C084C8);}
.xprogbar.xppb{background:linear-gradient(90deg,#3B82F6,#A78BFA);}
.xfooter{display:flex;justify-content:space-between;margin-top:0.3rem;}
.xlbl{font-family:'Space Mono',monospace;font-size:0.45rem;color:#4A3858;letter-spacing:0.08em;}
.xctr{font-family:'Space Mono',monospace;font-size:0.48rem;color:#4A3858;}
.xnav{display:flex;gap:0.5rem;align-items:center;}
.xnav button{background:none;border:1px solid rgba(139,58,139,0.3);color:#C084C8;
  border-radius:50%;width:24px;height:24px;cursor:pointer;font-size:0.8rem;
  display:flex;align-items:center;justify-content:center;padding:0;transition:background 0.2s;}
.xnav button:hover{background:rgba(139,58,139,0.2);}
.xcar.xpol .xnav button{border-color:rgba(96,165,250,0.3);color:#60A5FA;}
.xcar.xpol .xnav button:hover{background:rgba(59,130,246,0.15);}
.xdots{display:flex;gap:0.3rem;align-items:center;flex-wrap:wrap;}
.xdot{width:6px;height:6px;border-radius:50%;background:rgba(139,58,139,0.3);
  border:1px solid rgba(139,58,139,0.4);cursor:pointer;display:inline-block;transition:transform 0.2s;}
.xdot.xa{background:#C084C8;transform:scale(1.3);}
.xcar.xpol .xdot{background:rgba(96,165,250,0.25);border-color:rgba(96,165,250,0.35);}
.xcar.xpol .xdot.xa{background:#60A5FA;}
</style>"""

def _render_news_carousel(items, car_id, is_policy):
    css_type = "xpol" if is_policy else "xnews"
    title = "Policy &amp; Government Decisions" if is_policy else "Financial Headlines"
    subtitle = '<span class="xcar-sub">This Week</span>' if is_policy else ""
    prog_cls = "xppb" if is_policy else "xnpb"
    prog_track = "xpp" if is_policy else "xnp"
    card_cls = "xcp" if is_policy else "xcn"

    slides_html = ""
    dots_html = ""
    for i, item in enumerate(items):
        if is_policy:
            title_txt, link, source, flag, color = item
            badge = '<span class="xbadge">Policy</span>'
            src_content = f'{flag} {_html_mod.escape(source)} {badge}'
        else:
            title_txt, link, source, color, _ = item
            src_content = _html_mod.escape(source)

        active = " xactive" if i == 0 else ""
        slides_html += f"""
    <div class="xslide{active}" id="{car_id}-slide-{i}">
      <div class="xcard {card_cls}" style="border-left:3px solid {color}">
        <div class="xcard-src" style="color:{color}">{src_content}</div>
        <a class="xcard-ttl" href="{link}" target="_blank">{_html_mod.escape(title_txt)}</a>
        <div class="xcard-dt">{_TODAY}</div>
      </div>
    </div>"""
        dot_active = " xa" if i == 0 else ""
        dots_html += f'<span class="xdot{dot_active}" onclick="xGoTo(\'{car_id}\',{i})"></span>'

    total = len(items)
    js = f"""
<script>
(function(){{
  var _id='{car_id}', _total={total}, _cur=0, _paused=false, _timer=null;
  function xShow(n){{
    _cur=((n%_total)+_total)%_total;
    for(var i=0;i<_total;i++){{
      var s=document.getElementById(_id+'-slide-'+i);
      var d=document.querySelectorAll('#'+_id+' .xdot')[i];
      if(s)s.className='xslide'+(i===_cur?' xactive':'');
      if(d)d.className='xdot'+(i===_cur?' xa':'');
    }}
    var c=document.getElementById(_id+'-ctr');
    if(c)c.textContent=(_cur+1)+' / '+_total;
    var pb=document.getElementById(_id+'-pb');
    if(pb){{pb.style.transition='none';pb.style.width='0%';
      setTimeout(function(){{pb.style.transition='width 3000ms linear';pb.style.width='100%';}},30);}}
  }}
  window.xGoTo=window.xGoTo||function(){{}};
  var _old=window.xGoTo;
  window.xGoTo=function(id,n){{if(id===_id){{xShow(n);clearInterval(_timer);_timer=setInterval(function(){{if(!_paused)xShow(_cur+1);}},3000);}}else _old(id,n);}};
  var wrap=document.getElementById(_id);
  if(wrap){{
    wrap.addEventListener('mouseenter',function(){{_paused=true;}});
    wrap.addEventListener('mouseleave',function(){{_paused=false;}});
  }}
  xShow(0);
  _timer=setInterval(function(){{if(!_paused)xShow(_cur+1);}},3000);
}})();
</script>"""

    return f"""
<div class="xcar {css_type}" id="{car_id}">
  <div class="xcar-hdr">
    <div class="xcar-ttl {css_type}">{title}{subtitle}</div>
    <div class="xnav">
      <div class="xdots">{dots_html}</div>
      <button onclick="xGoTo('{car_id}',{{}}-1)" title="prev">&#8249;</button>
      <button onclick="xGoTo('{car_id}',{{}}+1)" title="next">&#8250;</button>
    </div>
  </div>
  <div class="xslides">{slides_html}
  </div>
  <div class="xprog {prog_track}"><div class="xprogbar {prog_cls}" id="{car_id}-pb"></div></div>
  <div class="xfooter"><div class="xlbl">&#9679; curated</div><div class="xctr" id="{car_id}-ctr">1 / {total}</div></div>
</div>
{js}"""

# Render nav buttons with correct cur reference per carousel
def _render_carousel_final(items, car_id, is_policy):
    css_type = "xpol" if is_policy else "xnews"
    title = "Policy &amp; Government Decisions" if is_policy else "Financial Headlines"
    subtitle = '<span class="xcar-sub">This Week</span>' if is_policy else ""
    prog_cls = "xppb" if is_policy else "xnpb"
    prog_track = "xpp" if is_policy else "xnp"
    card_cls = "xcp" if is_policy else "xcn"
    total = len(items)

    slides_html = ""
    dots_html = ""
    for i, item in enumerate(items):
        if is_policy:
            title_txt, link, source, flag, color = item
            badge = '<span class="xbadge">Policy</span>'
            src_content = f'{flag} {_html_mod.escape(source)} {badge}'
        else:
            title_txt, link, source, color, _ = item
            src_content = _html_mod.escape(source)
        active = " xactive" if i == 0 else ""
        slides_html += (
            f'<div class="xslide{active}" id="{car_id}-s{i}">'
            f'<div class="xcard {card_cls}" style="border-left:3px solid {color}">'
            f'<div class="xcard-src" style="color:{color}">{src_content}</div>'
            f'<a class="xcard-ttl" href="{link}" target="_blank">{_html_mod.escape(title_txt)}</a>'
            f'<div class="xcard-dt">{_TODAY}</div>'
            f'</div></div>'
        )
        dot_active = " xa" if i == 0 else ""
        dots_html += f'<span class="xdot{dot_active}" id="{car_id}-d{i}" onclick="_xGo(\'{car_id}\',{i})"></span>'

    js = (
        f'<script>(function(){{'
        f'var I="{car_id}",N={total},C=0,P=false,T=null;'
        f'function go(n){{'
        f'C=((n%N)+N)%N;'
        f'for(var i=0;i<N;i++){{'
        f'var s=document.getElementById(I+"-s"+i);'
        f'var d=document.getElementById(I+"-d"+i);'
        f'if(s)s.style.display=i===C?"block":"none";'
        f'if(d)d.className="xdot"+(i===C?" xa":"");'
        f'}}'
        f'var ct=document.getElementById(I+"-ct");if(ct)ct.textContent=(C+1)+" / "+N;'
        f'var pb=document.getElementById(I+"-pb");'
        f'if(pb){{pb.style.transition="none";pb.style.width="0%";'
        f'setTimeout(function(){{pb.style.transition="width 3200ms linear";pb.style.width="100%";}},40);}}'
        f'}}'
        f'window._xGo=window._xGo||function(){{}};'
        f'var _old=window._xGo;'
        f'window._xGo=function(id,n){{if(id===I)go(n);else _old(id,n);}};'
        f'document.getElementById(I+"-pv").onclick=function(){{go(C-1);restart();}};'
        f'document.getElementById(I+"-nx").onclick=function(){{go(C+1);restart();}};'
        f'function restart(){{clearInterval(T);T=setInterval(function(){{if(!P)go(C+1);}},3200);}}'
        f'var w=document.getElementById(I);'
        f'if(w){{w.addEventListener("mouseenter",function(){{P=true;}});'
        f'w.addEventListener("mouseleave",function(){{P=false;}});}}'
        f'go(0);restart();'
        f'}})();</script>'
    )

    return (
        f'<div class="xcar {css_type}" id="{car_id}">'
        f'<div class="xcar-hdr">'
        f'<div class="xcar-ttl {css_type}">{title}{subtitle}</div>'
        f'<div style="display:flex;align-items:center;gap:0.5rem;">'
        f'<div class="xdots">{dots_html}</div>'
        f'<button id="{car_id}-pv" class="xnavbtn" style="background:none;border:1px solid rgba(139,58,139,0.3);color:#C084C8;border-radius:50%;width:24px;height:24px;cursor:pointer;font-size:0.85rem;padding:0;">&#8249;</button>'
        f'<button id="{car_id}-nx" class="xnavbtn" style="background:none;border:1px solid rgba(139,58,139,0.3);color:#C084C8;border-radius:50%;width:24px;height:24px;cursor:pointer;font-size:0.85rem;padding:0;">&#8250;</button>'
        f'</div>'
        f'</div>'
        f'<div style="position:relative;min-height:100px;">{slides_html}</div>'
        f'<div class="xprog {prog_track}"><div class="xprogbar {prog_cls}" id="{car_id}-pb"></div></div>'
        f'<div class="xfooter"><div class="xlbl">&#9679; curated &#183; updates on refresh</div>'
        f'<div class="xctr" id="{car_id}-ct">1 / {total}</div></div>'
        f'</div>{js}'
    )

_carousel_css = _car_css()
_news_html    = _render_carousel_final(NEWS_ITEMS,   "xn", False)
_policy_html  = _render_carousel_final(POLICY_ITEMS, "xp", True)

st.markdown(_carousel_css + _news_html + _policy_html, unsafe_allow_html=True)

# COMMODITIES  (Gold, Silver, Oil, Platinum, Palladium)
# ══════════════════════════════════════════════════════════════════════════════
COMMODITY_SYMS = {
    "GC=F":  ("Gold",      "$/oz",  "🪙", 2),
    "SI=F":  ("Silver",    "$/oz",  "⚪", 3),
    "CL=F":  ("Crude Oil", "$/bbl", "🛢️", 2),
    "PL=F":  ("Platinum",  "$/oz",  "💎", 2),
    "PA=F":  ("Palladium", "$/oz",  "✨", 2),
    "HG=F":  ("Copper",    "$/lb",  "🟤", 3),
}

comm_quotes = fetch_multi_quotes(tuple(COMMODITY_SYMS.keys()))
comm_chips = ""
for sym, (name, unit, icon, dec) in COMMODITY_SYMS.items():
    info = comm_quotes.get(sym)
    if info:
        comm_chips += make_chip_html(sym, f"{name} · {unit}", info["price"], info["pct"],
                                      prefix="$", decimals=dec, icon=icon)

if comm_chips:
    st.markdown(
        '<div class="comm-panel">'
        '<div class="comm-title">Precious Metals &amp; Commodities</div>'
        '<div class="chips-row">' + comm_chips + "</div>"
        '<div style="font-family:\'Space Mono\',monospace;font-size:0.5rem;letter-spacing:0.1em;color:#4A3858;margin-top:0.65rem;text-align:right;">Futures prices · Yahoo Finance · 60s cache</div>'
        "</div>",
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# CRYPTO  (BTC, ETH, BNB, SOL, XRP, DOGE, ADA, AVAX)
# ══════════════════════════════════════════════════════════════════════════════
CRYPTO_SYMS = {
    "BTC-USD":  ("Bitcoin",   "BTC", "₿",  2),
    "ETH-USD":  ("Ethereum",  "ETH", "Ξ",  2),
    "BNB-USD":  ("BNB",       "BNB", "🔶", 2),
    "SOL-USD":  ("Solana",    "SOL", "◎",  2),
    "XRP-USD":  ("XRP",       "XRP", "✕",  4),
    "DOGE-USD": ("Dogecoin",  "DOGE","🐕", 5),
    "ADA-USD":  ("Cardano",   "ADA", "🔵", 4),
    "AVAX-USD": ("Avalanche", "AVAX","🔺", 2),
}

crypto_quotes = fetch_multi_quotes(tuple(CRYPTO_SYMS.keys()))
crypto_chips = ""
for sym, (name, ticker, icon, dec) in CRYPTO_SYMS.items():
    info = crypto_quotes.get(sym)
    if info:
        crypto_chips += make_chip_html(ticker, name, info["price"], info["pct"],
                                        prefix="$", decimals=dec, icon=icon)

if crypto_chips:
    st.markdown(
        '<div class="crypto-panel">'
        '<div class="crypto-title">Crypto Markets</div>'
        '<div class="chips-row">' + crypto_chips + "</div>"
        '<div style="font-family:\'Space Mono\',monospace;font-size:0.5rem;letter-spacing:0.1em;color:#4A3858;margin-top:0.65rem;text-align:right;">Spot prices · Yahoo Finance · 60s cache</div>'
        "</div>",
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# LIVE STOCK CHART
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div style="background:#0D0B12;border:1px solid rgba(139,58,139,0.22);border-radius:12px;padding:1.2rem 1.4rem 0.5rem;margin-bottom:1.4rem;">',
    unsafe_allow_html=True,
)
st.markdown(
    '<div style="font-family:\'Cormorant Garamond\',serif;font-size:1.1rem;font-weight:300;color:#EDE8F5;margin-bottom:0.8rem;display:flex;align-items:center;gap:0.5rem;">'
    '<span style="display:inline-block;width:3px;height:1.1rem;background:linear-gradient(180deg,#6B2D6B,#C084C8);border-radius:2px;"></span>'
    'Live Market Overview</div>',
    unsafe_allow_html=True,
)

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

period_map   = {"1D":"1d","5D":"5d","1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y"}
interval_map = {"1D":"5m","5D":"30m","1M":"1d","3M":"1d","6M":"1d","1Y":"1wk"}

if symbols:
    period   = period_map[rng]
    interval = interval_map[rng]

    # Ticker chips
    stock_quotes = fetch_multi_quotes(tuple(symbols))
    chip_parts = []
    for sym in symbols:
        info = stock_quotes.get(sym)
        if info:
            arrow = "▲" if info["pct"] >= 0 else "▼"
            chg_color = "#4ade80" if info["pct"] >= 0 else "#f87171"
            chip_parts.append(
                '<div style="display:flex;flex-direction:column;align-items:center;'
                'background:#120E1A;border:1px solid rgba(139,58,139,0.22);'
                'border-radius:8px;padding:0.45rem 0.75rem;min-width:80px;font-family:Space Mono,monospace;">'
                f'<span style="font-size:0.62rem;color:#C084C8;font-weight:700;">{sym}</span>'
                f'<span style="font-size:0.74rem;color:#EDE8F5;margin-top:0.1rem;">${info["price"]:,.2f}</span>'
                f'<span style="font-size:0.58rem;color:{chg_color};">{arrow} {abs(info["pct"]):.2f}%</span>'
                '</div>'
            )
    if chip_parts:
        st.markdown(
            '<div style="display:flex;gap:0.55rem;flex-wrap:wrap;margin-bottom:0.8rem;">'
            + "".join(chip_parts) + "</div>",
            unsafe_allow_html=True,
        )

    chart = pd.DataFrame()
    for sym in symbols:
        s = fetch_yahoo_series(sym, period, interval)
        if s is not None and not s.empty:
            chart[sym] = s

    if not chart.empty:
        chart  = chart.dropna(how="all").ffill()
        normed = (chart / chart.iloc[0] - 1) * 100
        st.line_chart(normed, height=230, use_container_width=True)
        st.caption(f"% return from period start · {rng} · {len(chart)} data points · Yahoo Finance")
    else:
        st.warning("Could not load chart data. Yahoo Finance may be rate-limiting — try again in a moment.")
else:
    st.info("Select at least one symbol above to show the chart.")

st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CURRENCY PANEL
# ══════════════════════════════════════════════════════════════════════════════
ALL_FX = {
    "USDINR=X": {"label":"USD/INR","flag":"🇮🇳","name":"Indian Rupee",       "invert":False},
    "USDJPY=X": {"label":"USD/JPY","flag":"🇯🇵","name":"Japanese Yen",       "invert":False},
    "USDCNY=X": {"label":"USD/CNY","flag":"🇨🇳","name":"Chinese Yuan",       "invert":False},
    "EURUSD=X": {"label":"EUR/USD","flag":"🇪🇺","name":"Euro",               "invert":True},
    "GBPUSD=X": {"label":"GBP/USD","flag":"🇬🇧","name":"British Pound",      "invert":True},
    "USDCHF=X": {"label":"USD/CHF","flag":"🇨🇭","name":"Swiss Franc",        "invert":False},
    "USDKRW=X": {"label":"USD/KRW","flag":"🇰🇷","name":"S. Korean Won",      "invert":False},
    "USDBRL=X": {"label":"USD/BRL","flag":"🇧🇷","name":"Brazilian Real",     "invert":False},
    "USDCAD=X": {"label":"USD/CAD","flag":"🇨🇦","name":"Canadian Dollar",    "invert":False},
    "USDAUD=X": {"label":"USD/AUD","flag":"🇦🇺","name":"Australian Dollar",  "invert":False},
    "USDSGD=X": {"label":"USD/SGD","flag":"🇸🇬","name":"Singapore Dollar",   "invert":False},
    "USDHKD=X": {"label":"USD/HKD","flag":"🇭🇰","name":"Hong Kong Dollar",   "invert":False},
    "USDMXN=X": {"label":"USD/MXN","flag":"🇲🇽","name":"Mexican Peso",       "invert":False},
    "USDTRY=X": {"label":"USD/TRY","flag":"🇹🇷","name":"Turkish Lira",       "invert":False},
    "USDRUB=X": {"label":"USD/RUB","flag":"🇷🇺","name":"Russian Ruble",      "invert":False},
    "USDZAR=X": {"label":"USD/ZAR","flag":"🇿🇦","name":"S. African Rand",    "invert":False},
    "USDAED=X": {"label":"USD/AED","flag":"🇦🇪","name":"UAE Dirham",         "invert":False},
    "USDNOK=X": {"label":"USD/NOK","flag":"🇳🇴","name":"Norwegian Krone",    "invert":False},
    "USDSEK=X": {"label":"USD/SEK","flag":"🇸🇪","name":"Swedish Krona",      "invert":False},
    "USDDKK=X": {"label":"USD/DKK","flag":"🇩🇰","name":"Danish Krone",       "invert":False},
    "USDNZD=X": {"label":"USD/NZD","flag":"🇳🇿","name":"New Zealand Dollar", "invert":False},
    "USDPLN=X": {"label":"USD/PLN","flag":"🇵🇱","name":"Polish Zloty",       "invert":False},
    "USDTHB=X": {"label":"USD/THB","flag":"🇹🇭","name":"Thai Baht",          "invert":False},
    "USDIDR=X": {"label":"USD/IDR","flag":"🇮🇩","name":"Indonesian Rupiah",  "invert":False},
    "USDPHP=X": {"label":"USD/PHP","flag":"🇵🇭","name":"Philippine Peso",    "invert":False},
}

fx_options     = {f"{m['flag']} {m['label']} · {m['name']}": sym for sym, m in ALL_FX.items()}
default_labels = [k for k, v in fx_options.items() if v in ("USDINR=X","USDJPY=X","USDCNY=X","EURUSD=X","GBPUSD=X","USDCHF=X")]

st.markdown(
    '<div class="fx-panel">'
    '<div class="fx-panel-title">Currencies vs USD</div>',
    unsafe_allow_html=True,
)

fx_row1, fx_row2 = st.columns([5, 1])
with fx_row1:
    selected_labels = st.multiselect(
        "currencies", options=list(fx_options.keys()), default=default_labels,
        label_visibility="collapsed", key="fx_select",
    )
with fx_row2:
    fx_rng = st.selectbox("fx_range", ["1M","3M","6M","1Y"], index=0, label_visibility="collapsed", key="fx_rng")

selected_syms = [fx_options[lbl] for lbl in selected_labels]
st.session_state["fx_select_syms"] = selected_syms

fx_period_map   = {"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y"}
fx_interval_map = {"1M":"1d", "3M":"1d", "6M":"1d", "1Y":"1wk"}

if selected_syms:
    fx_chart = pd.DataFrame()
    for sym in selected_syms:
        meta = ALL_FX[sym]
        s    = fetch_yahoo_series(sym, fx_period_map[fx_rng], fx_interval_map[fx_rng])
        if s is not None and not s.empty:
            if meta["invert"]:
                s = 1.0 / s
            s = (s / s.iloc[0] - 1) * 100
            s.name = meta["flag"] + " " + meta["label"]
            fx_chart[s.name] = s

    if not fx_chart.empty:
        fx_chart = fx_chart.dropna(how="all").ffill()
        st.line_chart(fx_chart, height=220, use_container_width=True)
        st.caption(f"% change from {fx_rng} start · Rising = USD strengthening · EUR/GBP inverted · Yahoo Finance")
    else:
        st.warning("Chart data unavailable — try again shortly.")

    # FX chips — built with make_chip_html to avoid nested quote escaping issues
    fx_quotes = fetch_multi_quotes(tuple(selected_syms))
    chip_html_parts = []
    for sym in selected_syms:
        meta = ALL_FX[sym]
        info = fx_quotes.get(sym)
        if info:
            rate = info["price"]
            pct  = info["pct"]
            rate_str = f"{rate:,.2f}" if rate >= 10 else f"{rate:.4f}"
            arrow = "▲" if pct > 0.005 else ("▼" if pct < -0.005 else "●")
            chg_class = "up" if pct > 0.005 else ("down" if pct < -0.005 else "flat")
            chip_html_parts.append(
                '<div class="price-chip">'
                f'<div class="pc-sym">{meta["flag"]} {meta["label"]}</div>'
                f'<div class="pc-name">{meta["name"]}</div>'
                f'<div class="pc-val">{rate_str}</div>'
                f'<div class="pc-chg {chg_class}">{arrow} {abs(pct):.3f}%</div>'
                '</div>'
            )

    if chip_html_parts:
        now_ist = _dt.datetime.utcnow() + _dt.timedelta(hours=5, minutes=30)
        st.markdown(
            '<div class="chips-row" style="margin-top:0.75rem;">'
            + "".join(chip_html_parts)
            + "</div>"
            + f'<div style="font-family:Space Mono,monospace;font-size:0.5rem;letter-spacing:0.1em;color:#4A3858;margin-top:0.6rem;text-align:right;">Live · {now_ist.strftime("%H:%M")} IST · 60s cache</div>',
            unsafe_allow_html=True,
        )
else:
    st.info("Select at least one currency pair above.")

st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHAT SECTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="font-family:'Cormorant Garamond',serif;font-size:1.35rem;font-weight:300;color:#EDE8F5;margin:0.5rem 0 0.8rem;">
  Ask Anything — Markets, Currencies, Gold &amp; Documents
</div>
""", unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="empty">
      <div class="empty-orb">◈</div>
      <div class="empty-title">Ready without uploads</div>
      <div class="empty-sub">
        Ask about <strong>live stocks</strong>, <strong>gold &amp; silver</strong>,
        <strong>crypto</strong>, <strong>currency rates</strong>, macro trends — no documents needed.<br><br>
        Use <strong>＋</strong> to upload financial reports for deeper document analysis.
      </div>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander(f"↳ {len(msg['sources'])} source(s)"):
                for src in msg["sources"]:
                    st.markdown(
                        f'<div class="src-card"><div class="src-name">📄 {src["filename"]}</div>'
                        f'<div class="src-score">relevance: {src["score"]}</div>'
                        f'<div class="src-preview">{src["preview"]}…</div></div>',
                        unsafe_allow_html=True,
                    )

# Upload drawer
if st.session_state.show_upload:
    st.markdown('<div class="upload-drawer"><div class="upload-drawer-title">◈ Upload Financial Documents</div>', unsafe_allow_html=True)
    inline_files = st.file_uploader(
        "Upload", type=["pdf","txt"], accept_multiple_files=True,
        label_visibility="collapsed", key="drawer_upload",
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

bar_col1, bar_col2 = st.columns([1, 16], gap="small")
with bar_col1:
    if st.button("＋", key="plus_btn", use_container_width=True, help="Upload documents"):
        st.session_state.show_upload = not st.session_state.show_upload
        st.rerun()
with bar_col2:
    prefill  = st.session_state.pop("_prefill", None)
    question = st.chat_input("Ask about stocks, gold, crypto, currencies, or your documents…")

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

                # Live stock context
                stock_lines = []
                for sym in symbols:
                    info = fetch_quote(sym)
                    if info:
                        arrow = "▲" if info["pct"] >= 0 else "▼"
                        stock_lines.append(f"  {sym}: ${info['price']:,.2f} ({arrow}{abs(info['pct']):.2f}%)")
                stock_str = "\n".join(stock_lines) if stock_lines else "  (none selected)"

                # Live FX context
                fx_lines = []
                fx_syms_for_chat = tuple(st.session_state.get("fx_select_syms", ("USDINR=X","USDJPY=X","USDCNY=X")))
                for sym in fx_syms_for_chat:
                    info = fetch_quote(sym)
                    if info:
                        meta = ALL_FX.get(sym, {})
                        label = meta.get("label", sym)
                        rate_str = f"{info['price']:,.2f}" if info["price"] >= 10 else f"{info['price']:.4f}"
                        fx_lines.append(f"  {label}: {rate_str} ({'+' if info['pct']>=0 else ''}{info['pct']:.3f}%)")
                fx_str = "\n".join(fx_lines) if fx_lines else "  (unavailable)"

                # Commodities context
                comm_lines = []
                for sym, (name, unit, _, dec) in COMMODITY_SYMS.items():
                    info = fetch_quote(sym)
                    if info:
                        comm_lines.append(f"  {name}: ${info['price']:,.{dec}f} {unit} ({'+' if info['pct']>=0 else ''}{info['pct']:.2f}%)")
                comm_str = "\n".join(comm_lines) if comm_lines else "  (unavailable)"

                # Crypto context
                crypto_lines = []
                for sym, (name, ticker, _, dec) in CRYPTO_SYMS.items():
                    info = fetch_quote(sym)
                    if info:
                        crypto_lines.append(f"  {ticker}: ${info['price']:,.{dec}f} ({'+' if info['pct']>=0 else ''}{info['pct']:.2f}%)")
                crypto_str = "\n".join(crypto_lines) if crypto_lines else "  (unavailable)"

                utc_now = _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
                live_context = f"""=== LIVE MARKET DATA ({utc_now}) ===

STOCKS:
{stock_str}

COMMODITIES (Gold, Silver, Oil etc.):
{comm_str}

CRYPTO:
{crypto_str}

CURRENCIES (vs USD):
{fx_str}

MARKET MOOD: Fear & Greed Index = {fng_val} ({fng_label})
""".strip()

                doc_context  = ""
                sources_data = []
                if st.session_state.vectorstore:
                    vs    = st.session_state.vectorstore
                    q_emb = vs["model"].encode([q], normalize_embeddings=True).tolist()
                    res   = vs["collection"].query(
                        query_embeddings=q_emb, n_results=5,
                        include=["documents","metadatas","distances"],
                    )
                    cks = res["documents"][0]
                    mts = res["metadatas"][0]
                    dts = res["distances"][0]
                    doc_context = "\n---\n".join(f"[{m['filename']}]\n{c}" for c, m in zip(cks, mts))
                    sources_data = [
                        {"filename": m["filename"], "score": round(1-d/2, 3), "preview": c[:220]}
                        for c, m, d in zip(cks, mts, dts)
                    ]

                user_msg = (
                    f"{live_context}\n\n=== DOCUMENT CONTEXT ===\n{doc_context}\n\nQuestion: {q}"
                    if doc_context else
                    f"{live_context}\n\nQuestion: {q}"
                )

                system_prompt = """You are an expert financial analyst with real-time data access covering equities, commodities (gold, silver, oil), crypto, and FX markets.

You have been given:
1. LIVE MARKET DATA — current prices for stocks, gold, silver, oil, crypto, and FX rates.
2. DOCUMENT CONTEXT — relevant excerpts from any uploaded financial reports.

Rules:
- Use the live data provided for any market/price/rate questions.
- For document questions, cite specific numbers and dates from the context.
- Combine live and document data intelligently when both are relevant.
- Be concise, precise, and cite your sources.
- Never fabricate numbers."""

                history_msgs = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[:-1]
                ]

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
                            st.markdown(
                                f'<div class="src-card"><div class="src-name">📄 {src["filename"]}</div>'
                                f'<div class="src-score">relevance: {src["score"]}</div>'
                                f'<div class="src-preview">{src["preview"]}…</div></div>',
                                unsafe_allow_html=True,
                            )

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
