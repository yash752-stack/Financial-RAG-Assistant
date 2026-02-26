"""
app.py — Financial RAG Assistant
Royal Velvet & Black Theme  |  v4
Run: streamlit run app.py
"""

import os
import datetime as _dt
import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Financial RAG Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── HIDE STREAMLIT CHROME + RESPONSIVE ───────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], .stDeployButton { display:none !important; }

/* ── Sidebar toggle button (☰) ──────────────────────── */
[data-testid="collapsedControl"] {
  background: rgba(107,45,107,0.18) !important;
  border: 1px solid rgba(139,58,139,0.45) !important;
  border-radius: 8px !important;
  color: #C084C8 !important;
  top: 0.9rem !important;
}
[data-testid="collapsedControl"]:hover {
  background: rgba(107,45,107,0.35) !important;
  box-shadow: 0 0 12px rgba(107,45,107,0.4) !important;
}

/* ── Responsive breakpoints ─────────────────────────── */
/* Tablet (768–1024px): tighten padding, shrink fonts */
@media (max-width: 1024px) {
  [data-testid="block-container"] { padding: 0 1rem !important; }
  .stat-strip { grid-template-columns: repeat(2,1fr) !important; }
}
/* Mobile (<768px): collapse to single column */
@media (max-width: 767px) {
  [data-testid="block-container"] { padding: 0 0.5rem !important; max-width:100% !important; }
  [data-testid="stSidebar"] { min-width: 260px !important; width: 260px !important; }
  .stat-strip { grid-template-columns: repeat(2,1fr) !important; }
  .rag-header h1 { font-size: 2rem !important; }
  .rag-header { padding: 1.2rem 1rem !important; }
  [data-testid="stColumns"] > div { min-width: 0 !important; }
}
/* Very small (<480px) */
@media (max-width: 479px) {
  .stat-strip { grid-template-columns: repeat(1,1fr) !important; }
  .rag-header h1 { font-size: 1.6rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROYAL VELVET & BLACK DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Syne:wght@400;500;600;700&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

:root {
  --black:      #07060C;
  --card:       #0D0B12;
  --card-2:     #120E1A;
  --panel:      #0F0C16;
  --border:     rgba(139,58,139,0.22);
  --border-l:   rgba(176,107,176,0.45);
  --velvet:     #6B2D6B;
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
.stTextInput input, .stTextArea textarea { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; color: var(--text) !important; }
[data-testid="stChatInput"] { background: var(--card-2) !important; border: 1px solid var(--border-l) !important; border-radius: 14px !important; box-shadow: 0 0 30px rgba(107,45,107,0.12) !important; }
[data-testid="stChatInput"] textarea { background: transparent !important; border: none !important; color: var(--text) !important; }
[data-testid="stChatInput"]:focus-within { border-color: rgba(139,58,139,0.7) !important; }
[data-testid="stChatMessage"] { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; padding: 0.8rem 1rem !important; margin-bottom: 0.5rem !important; }
[data-testid="stFileUploader"] { background: rgba(107,45,107,0.05) !important; border: 1.5px dashed rgba(139,58,139,0.4) !important; border-radius: 10px !important; }
[data-testid="stExpander"] { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; }
[data-testid="stAlert"] { background: rgba(107,45,107,0.1) !important; border: 1px solid var(--border-l) !important; border-radius: 8px !important; }
div[data-testid="stSuccess"] { background: rgba(74,222,128,0.07) !important; }
div[data-testid="stError"] { background: rgba(248,113,113,0.07) !important; }
.stProgress > div > div { background: linear-gradient(90deg, var(--velvet), var(--accent)) !important; }
[data-testid="stMultiSelect"] > div { background: var(--card) !important; border-color: var(--border) !important; border-radius: 8px !important; }
.stMultiSelect span[data-baseweb="tag"] { background: rgba(107,45,107,0.3) !important; border: 1px solid var(--velvet-gl) !important; color: var(--lilac) !important; border-radius: 999px !important; }
[data-testid="stSelectbox"] > div > div { background: var(--card) !important; border-color: var(--border) !important; border-radius: 8px !important; }
hr { border-color: var(--border) !important; }
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
.mood-needle { position: absolute; top: -5px; width: 16px; height: 16px; border-radius: 50%; border: 2px solid #fff; background: var(--accent); transform: translateX(-50%); box-shadow: 0 0 8px rgba(192,132,200,0.6); }
.mood-labels { display: flex; justify-content: space-between; font-family: 'Space Mono', monospace; font-size: 0.5rem; color: var(--text-ghost); }
.mood-index { font-family: 'Cormorant Garamond', serif; font-size: 2rem; font-weight: 300; }
.mood-indices { display: flex; gap: 1rem; margin-top: 0.8rem; flex-wrap: wrap; }
.mood-idx-chip { display: flex; flex-direction: column; background: var(--card-2); border: 1px solid var(--border); border-radius: 8px; padding: 0.4rem 0.8rem; font-family: 'Space Mono', monospace; min-width: 90px; }
.mood-idx-name { font-size: 0.52rem; color: var(--text-ghost); letter-spacing: 0.1em; }
.mood-idx-val  { font-size: 0.72rem; color: var(--text); margin-top: 0.1rem; }
.mood-idx-chg.up   { font-size: 0.56rem; color: #4ade80; }
.mood-idx-chg.down { font-size: 0.56rem; color: #f87171; }

/* ── PRICE CHIP ── */
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
.comm-panel { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.1rem 1.4rem 0.9rem; margin-bottom: 1.4rem; }
.comm-title { font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; font-weight: 300; color: var(--text); margin-bottom: 0.9rem; display: flex; align-items: center; gap: 0.5rem; }
.comm-title::before { content: ''; display: inline-block; width: 3px; height: 1.1rem; background: linear-gradient(180deg, #F0C040, #C084C8); border-radius: 2px; }
.crypto-panel { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.1rem 1.4rem 0.9rem; margin-bottom: 1.4rem; }
.crypto-title { font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; font-weight: 300; color: var(--text); margin-bottom: 0.9rem; display: flex; align-items: center; gap: 0.5rem; }
.crypto-title::before { content: ''; display: inline-block; width: 3px; height: 1.1rem; background: linear-gradient(180deg, #fb923c, #C084C8); border-radius: 2px; }

/* ── MISC ── */
.sb-lbl { font-family: 'Space Mono', monospace; font-size: 0.54rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--velvet-gl); padding: 1.2rem 0 0.45rem; border-top: 1px solid var(--border); margin-top: 0.5rem; }
.key-ok { display: flex; align-items: center; gap: 0.5rem; background: rgba(74,222,128,0.07); border: 1px solid rgba(74,222,128,0.2); color: #86efac; padding: 0.38rem 0.7rem; border-radius: 6px; font-family: 'Space Mono', monospace; font-size: 0.6rem; }
.key-dot { width: 5px; height: 5px; border-radius: 50%; background: #4ade80; box-shadow: 0 0 6px #4ade80; animation: blink 2s infinite; }
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.3;} }
.doc-pill { display: flex; align-items: center; gap: 0.4rem; background: rgba(107,45,107,0.1); border: 1px solid var(--border); padding: 0.32rem 0.65rem; border-radius: 4px; margin-bottom: 0.3rem; font-family: 'Space Mono', monospace; font-size: 0.58rem; color: var(--text-dim); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.doc-dot { width:4px; height:4px; border-radius:50%; background:var(--velvet-gl); flex-shrink:0; }
.empty { text-align: center; padding: 4rem 2rem; }
.empty-orb { width: 100px; height: 100px; border-radius: 50%; background: radial-gradient(circle, rgba(107,45,107,0.28) 0%, transparent 70%); border: 1px solid var(--border); margin: 0 auto 1.5rem; display: flex; align-items: center; justify-content: center; font-size: 2rem; color: var(--velvet-gl); }
.empty-title { font-family: 'Cormorant Garamond', serif; font-size: 1.7rem; font-weight: 300; font-style: italic; color: var(--text-ghost); margin-bottom: 0.5rem; }
.empty-sub { font-size: 0.8rem; color: var(--text-ghost); max-width: 300px; margin: 0 auto; line-height: 1.8; opacity: 0.7; }
.upload-drawer { background: linear-gradient(135deg, rgba(107,45,107,0.18) 0%, rgba(13,11,18,0.95) 100%); border: 1px solid rgba(139,58,139,0.45); border-radius: 12px; padding: 1rem 1.1rem 0.7rem; margin-bottom: 0.6rem; }
.upload-drawer-title { font-family: 'Space Mono', monospace; font-size: 0.62rem; letter-spacing: 0.15em; text-transform: uppercase; color: var(--velvet-gl); margin-bottom: 0.6rem; }
.src-card { background: var(--card); border: 1px solid var(--border); border-left: 3px solid var(--velvet-gl); border-radius: 0 8px 8px 0; padding: 0.7rem 0.9rem; margin: 0.4rem 0; font-size: 0.82rem; }
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
_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ── RATE LIMITER (token bucket — prevents DDOS of Yahoo / APIs) ──────────────
import threading as _threading, time as _time

class _TokenBucket:
    """Thread-safe token bucket: max `capacity` calls per `refill_every` seconds."""
    def __init__(self, capacity: int = 30, refill_every: float = 60.0):
        self._cap      = capacity
        self._tokens   = float(capacity)
        self._interval = refill_every / capacity   # seconds per token
        self._lock     = _threading.Lock()
        self._last     = _time.monotonic()

    def acquire(self, timeout: float = 5.0) -> bool:
        deadline = _time.monotonic() + timeout
        while True:
            with self._lock:
                now    = _time.monotonic()
                earned = (now - self._last) / self._interval
                self._tokens = min(self._cap, self._tokens + earned)
                self._last   = now
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return True
            if _time.monotonic() >= deadline:
                return False
            _time.sleep(0.05)

# Singleton bucket — 30 market-data calls per 60 s (shared across all Streamlit threads)
@st.cache_resource
def _get_bucket():
    return _TokenBucket(capacity=30, refill_every=60.0)

def _throttled_get(url: str, timeout: int = 10) -> "requests.Response":
    """requests.get with token-bucket throttle. Raises RuntimeError if bucket empty."""
    if not _get_bucket().acquire(timeout=4.0):
        raise RuntimeError("Rate limit reached — please wait a few seconds and try again.")
    return requests.get(url, headers=_HEADERS, timeout=timeout)


@st.cache_data(ttl=300)
def fetch_yahoo_series(symbol: str, period: str, interval: str):
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?range={period}&interval={interval}&includePrePost=false"
    )
    try:
        r = _throttled_get(url, timeout=10)
        r.raise_for_status()
        data  = r.json()
        res   = data["chart"]["result"][0]
        ts    = res["timestamp"]
        close = res["indicators"]["quote"][0]["close"]
        idx   = pd.to_datetime(ts, unit="s", utc=True).tz_convert("US/Eastern")
        return pd.Series(close, index=idx, name=symbol).dropna()
    except Exception:
        return None

@st.cache_data(ttl=60)
def fetch_quote(symbol: str):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=2d&interval=1d"
    try:
        r = _throttled_get(url, timeout=8)
        r.raise_for_status()
        data = r.json()
        q = [x for x in data["chart"]["result"][0]["indicators"]["quote"][0]["close"] if x is not None]
        if not q:
            return None
        pct = (q[-1] - q[-2]) / q[-2] * 100 if len(q) >= 2 else 0.0
        return {"price": q[-1], "pct": pct}
    except Exception:
        return None

@st.cache_data(ttl=60)
def fetch_multi_quotes(symbols: tuple):
    return {sym: info for sym in symbols if (info := fetch_quote(sym))}

@st.cache_data(ttl=300)
def fetch_fear_greed():
    try:
        r = _throttled_get("https://api.alternative.me/fng/?limit=1", timeout=8)
        d = r.json()["data"][0]
        return {"value": int(d["value"]), "label": d["value_classification"]}
    except Exception:
        return {"value": 50, "label": "Neutral"}

@st.cache_data(ttl=600)
def fetch_rss_with_images(feed_url: str, source_name: str, accent: str, max_items: int = 8):
    """
    Fetch RSS feed, extract title + link + image (og:image or media:thumbnail or enclosure).
    Returns list of dicts: title, link, source, accent, img_url
    """
    import re, html as _h, urllib.parse

    FALLBACK_IMGS = {
        "Bloomberg":           "https://assets.bbhub.io/company/sites/51/2019/08/BBG-Logo-Black.png",
        "Wall Street Journal": "https://s.wsj.net/media/wsj_logo_black_sm.png",
        "Financial Times":     "https://about.ft.com/files/2020/04/ft_logo.png",
        "Reuters":             "https://www.reuters.com/pf/resources/images/reuters/logo-vertical-default.png",
        "CNBC":                "https://www.cnbc.com/2020/07/21/cnbc-social-card-2019.jpg",
        "The Economist":       "https://www.economist.com/img/b/1280/720/90/sites/default/files/images/2023/10/articles/main/20231021_blp502.jpg",
        "Federal Reserve":     "https://www.federalreserve.gov/img/federal-reserve-seal.svg",
        "IMF":                 "https://www.imf.org/~/media/Images/IMF/About/IMF-Emblem-Social-Media.ashx",
        "RBI India":           "https://rbidocs.rbi.org.in/rdocs/content/images/RBI-logo.png",
        "Bank of Japan":       "https://www.boj.or.jp/en/about/outline/history/img/historyphoto01.jpg",
        "ECB":                 "https://www.ecb.europa.eu/shared/img/logos/ecb-logo.en.svg",
    }

    try:
        hdrs = {**_HEADERS, "Accept": "application/rss+xml,application/xml,text/xml,*/*"}
        r = requests.get(feed_url, headers=hdrs, timeout=10)
        r.raise_for_status()
        text = r.text
    except Exception:
        return []

    results = []
    items = re.findall(r"<item[^>]*>(.*?)</item>", text, re.DOTALL)
    if not items:
        items = re.findall(r"<entry[^>]*>(.*?)</entry>", text, re.DOTALL)

    for item in items[:max_items]:
        # Title
        tm = re.search(r"<title[^>]*>(.*?)</title>", item, re.DOTALL | re.IGNORECASE)
        raw = tm.group(1).strip() if tm else ""
        cdata = re.match(r"<!\[CDATA\[(.*?)\]\]>", raw, re.DOTALL)
        title = cdata.group(1).strip() if cdata else raw
        title = _h.unescape(re.sub(r"<[^>]+>", "", title)).strip()
        if not title or len(title) < 10:
            continue

        # Link
        lm = (
            re.search(r'<link[^>]*href=["\'](https?://[^"\' >]+)["\']', item, re.IGNORECASE | re.DOTALL) or
            re.search(r"<link[^>]*/?\s*>\s*(https?://[^\s<]+)", item, re.DOTALL) or
            re.search(r"<link>(.*?)</link>", item, re.DOTALL | re.IGNORECASE)
        )
        link = (lm.group(1) or "#").strip() if lm else "#"
        if not link.startswith("http"):
            link = "#"

        # Image — try multiple sources
        img_url = ""
        # 1. media:content or media:thumbnail
        mm = re.search(r'<media:(?:content|thumbnail)[^>]+url=["\'](https?://[^"\']+)["\']', item, re.IGNORECASE)
        if mm:
            img_url = mm.group(1)
        # 2. enclosure
        if not img_url:
            em = re.search(r'<enclosure[^>]+url=["\'](https?://[^"\']+(?:jpg|jpeg|png|webp))["\']', item, re.IGNORECASE)
            if em:
                img_url = em.group(1)
        # 3. First <img> in description/content
        if not img_url:
            dm = re.search(r'<description[^>]*>(.*?)</description>|<content[^>]*>(.*?)</content>', item, re.DOTALL | re.IGNORECASE)
            if dm:
                desc = dm.group(1) or dm.group(2) or ""
                cdata2 = re.match(r"<!\[CDATA\[(.*?)\]\]>", desc.strip(), re.DOTALL)
                desc2 = cdata2.group(1) if cdata2 else desc
                im2 = re.search(r'<img[^>]+src=["\'](https?://[^"\']+)["\']', desc2, re.IGNORECASE)
                if im2:
                    img_url = im2.group(1)
        # 4. Fallback
        if not img_url:
            img_url = FALLBACK_IMGS.get(source_name, "")

        results.append({
            "title":   title,
            "link":    link,
            "source":  source_name,
            "accent":  accent,
            "img_url": img_url,
        })

    return results

@st.cache_data(ttl=600)
def fetch_gnews_with_images(query: str, source_label: str, accent: str, max_items: int = 6):
    import urllib.parse
    q_enc = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={q_enc}&hl=en-US&gl=US&ceid=US:en"
    return fetch_rss_with_images(url, source_label, accent, max_items)


def make_chip_html(sym, name, price, pct, prefix="$", suffix="", decimals=2, icon=""):
    arrow = "▲" if pct > 0.005 else ("▼" if pct < -0.005 else "●")
    cls   = "up" if pct > 0.005 else ("down" if pct < -0.005 else "flat")
    price_str = f"{prefix}{price:,.{decimals}f}{suffix}"
    icon_html = f'<span style="font-size:1rem;margin-right:0.2rem;">{icon}</span>' if icon else ""
    return (
        '<div class="price-chip">'
        f'<div class="pc-sym">{icon_html}{sym}</div>'
        f'<div class="pc-name">{name}</div>'
        f'<div class="pc-val">{price_str}</div>'
        f'<div class="pc-chg {cls}">{arrow} {abs(pct):.2f}%</div>'
        '</div>'
    )

# ══════════════════════════════════════════════════════════════════════════════
# NEWS DATA  — fetch from multiple RSS feeds
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=600)
def get_all_news():
    news = []
    feeds = [
        ("https://feeds.bloomberg.com/markets/news.rss",                    "Bloomberg",           "#4ADE80"),
        ("https://feeds.a.dj.com/rss/RSSMarketsMain.xml",                   "Wall Street Journal", "#F0C040"),
        ("https://www.ft.com/?format=rss",                                  "Financial Times",     "#FB923C"),
        ("https://www.cnbc.com/id/100003114/device/rss/rss.html",           "CNBC",                "#C084C8"),
        ("https://feeds.reuters.com/reuters/businessNews",                  "Reuters",             "#60A5FA"),
    ]
    for url, src, color in feeds:
        items = fetch_rss_with_images(url, src, color, max_items=4)
        news.extend(items)
    # Fallback to Google News if any feed returned nothing
    if len(news) < 6:
        extra = fetch_gnews_with_images("financial markets economy", "Google News", "#9CA3AF", 8)
        news.extend(extra)
    return news[:16]

@st.cache_data(ttl=600)
def get_policy_news():
    policy = []
    feeds = [
        ("https://www.federalreserve.gov/feeds/press_all.xml",              "Federal Reserve",     "🇺🇸", "#60A5FA"),
        ("https://www.ecb.europa.eu/rss/press.html",                        "ECB",                 "🇪🇺", "#34D399"),
        ("https://www.imf.org/en/News/rss?language=eng",                    "IMF",                 "🌐", "#A78BFA"),
        ("https://www.rbi.org.in/scripts/rss.aspx",                        "RBI India",           "🇮🇳", "#FB923C"),
        ("https://www.bankofengland.co.uk/rss/publications",               "Bank of England",     "🇬🇧", "#F472B6"),
    ]
    for url, src, flag, color in feeds:
        items = fetch_rss_with_images(url, src, color, max_items=3)
        for item in items:
            item["flag"]   = flag
            item["policy"] = True
        policy.extend(items)
    if len(policy) < 4:
        extra = fetch_gnews_with_images("central bank monetary policy rate decision", "Policy News", "#A78BFA", 6)
        for item in extra:
            item["flag"]   = "🏦"
            item["policy"] = True
        policy.extend(extra)
    return policy[:12]


# ══════════════════════════════════════════════════════════════════════════════
# IFRAME CAROUSEL BUILDER — JS runs inside its own iframe, bypasses Streamlit
# ══════════════════════════════════════════════════════════════════════════════
def build_carousel_html(items: list, is_policy: bool = False, height_px: int = 380) -> str:
    """
    Build a fully self-contained HTML carousel that auto-slides every 3s.
    Rendered inside st.components.v1.html() so JS works freely.
    """
    import json, html as _h

    accent_gradient = "linear-gradient(90deg,#3B82F6,#A78BFA)" if is_policy else "linear-gradient(90deg,#6B2D6B,#C084C8)"
    title_text      = "Policy &amp; Government Decisions" if is_policy else "Financial Headlines"
    title_bar_color = "#3B82F6" if is_policy else "#C084C8"
    bg_card         = "#0A0F1E" if is_policy else "#120E1A"
    border_color    = "rgba(59,130,246,0.3)" if is_policy else "rgba(139,58,139,0.3)"

    slides_js = json.dumps([
        {
            "title":   item["title"],
            "link":    item.get("link", "#"),
            "source":  item.get("source", ""),
            "accent":  item.get("accent", "#C084C8"),
            "img":     item.get("img_url", ""),
            "flag":    item.get("flag", ""),
            "policy":  item.get("policy", False),
        }
        for item in items
    ])

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #0D0B12;
    font-family: 'Segoe UI', system-ui, sans-serif;
    color: #EDE8F5;
    height: {height_px}px;
    overflow: hidden;
  }}
  .car-wrap {{
    background: #0D0B12;
    border: 1px solid {border_color};
    border-radius: 14px;
    height: {height_px}px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
  }}
  .car-wrap::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: {accent_gradient};
  }}
  .car-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 1.1rem 0.6rem;
    flex-shrink: 0;
    border-bottom: 1px solid rgba(139,58,139,0.12);
  }}
  .car-title {{
    font-family: 'Georgia', serif;
    font-size: 1.0rem;
    font-weight: 300;
    color: #EDE8F5;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }}
  .car-title::before {{
    content: '';
    display: inline-block;
    width: 3px; height: 1rem;
    background: {accent_gradient};
    border-radius: 2px;
    flex-shrink: 0;
  }}
  .car-nav {{
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }}
  .nav-btn {{
    background: rgba(107,45,107,0.15);
    border: 1px solid {border_color};
    color: {title_bar_color};
    width: 26px; height: 26px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 1rem;
    display: flex; align-items: center; justify-content: center;
    transition: background 0.2s;
    flex-shrink: 0;
  }}
  .nav-btn:hover {{ background: rgba(107,45,107,0.35); }}
  .dots {{
    display: flex;
    gap: 4px;
    align-items: center;
    flex-wrap: wrap;
    max-width: 160px;
  }}
  .dot {{
    width: 6px; height: 6px;
    border-radius: 50%;
    background: rgba(139,58,139,0.3);
    border: 1px solid rgba(139,58,139,0.4);
    cursor: pointer;
    transition: all 0.2s;
    flex-shrink: 0;
  }}
  .dot.active {{ background: {title_bar_color}; transform: scale(1.3); }}
  .slide-area {{
    flex: 1;
    position: relative;
    overflow: hidden;
  }}
  .slide {{
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    display: flex;
    flex-direction: column;
    opacity: 0;
    transform: translateX(40px);
    transition: opacity 0.45s ease, transform 0.45s ease;
    pointer-events: none;
  }}
  .slide.active {{
    opacity: 1;
    transform: translateX(0);
    pointer-events: all;
  }}
  .slide.leaving {{
    opacity: 0;
    transform: translateX(-40px);
  }}
  .slide-img {{
    width: 100%;
    height: 160px;
    object-fit: cover;
    flex-shrink: 0;
    background: #120E1A;
  }}
  .img-placeholder {{
    width: 100%;
    height: 160px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5rem;
    background: linear-gradient(135deg, #120E1A 0%, #1a1028 100%);
    border-bottom: 1px solid rgba(139,58,139,0.15);
  }}
  .slide-body {{
    padding: 0.7rem 1rem 0.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    flex: 1;
    background: {bg_card};
  }}
  .slide-src {{
    font-family: 'Courier New', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    flex-wrap: wrap;
  }}
  .policy-badge {{
    font-size: 0.45rem;
    background: rgba(59,130,246,0.15);
    border: 1px solid rgba(59,130,246,0.3);
    color: #93C5FD;
    padding: 0.05rem 0.35rem;
    border-radius: 3px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }}
  .slide-title {{
    font-size: 0.9rem;
    font-weight: 500;
    color: #EDE8F5;
    line-height: 1.45;
    text-decoration: none;
    display: block;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
  }}
  .slide-title:hover {{ color: {title_bar_color}; text-decoration: underline; text-underline-offset: 3px; }}
  .slide-meta {{
    font-family: 'Courier New', monospace;
    font-size: 0.48rem;
    color: #4A3858;
    margin-top: auto;
  }}
  .prog-bar-wrap {{
    flex-shrink: 0;
    height: 2px;
    background: rgba(139,58,139,0.12);
    overflow: hidden;
  }}
  .prog-bar {{
    height: 100%;
    width: 0%;
    background: {accent_gradient};
    border-radius: 1px;
    transition: width 3s linear;
  }}
  .car-footer {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.3rem 1rem;
    flex-shrink: 0;
    background: rgba(0,0,0,0.3);
  }}
  .footer-lbl {{
    font-family: 'Courier New', monospace;
    font-size: 0.44rem;
    color: #4A3858;
    letter-spacing: 0.08em;
  }}
  .footer-ctr {{
    font-family: 'Courier New', monospace;
    font-size: 0.48rem;
    color: #4A3858;
  }}
</style>
</head>
<body>
<div class="car-wrap" id="car">
  <div class="car-header">
    <div class="car-title">{title_text}</div>
    <div class="car-nav">
      <div class="dots" id="dots"></div>
      <button class="nav-btn" id="prev">&#8249;</button>
      <button class="nav-btn" id="next">&#8250;</button>
    </div>
  </div>
  <div class="slide-area" id="slides"></div>
  <div class="prog-bar-wrap"><div class="prog-bar" id="pb"></div></div>
  <div class="car-footer">
    <div class="footer-lbl">&#9679; live · refreshes every 10 min</div>
    <div class="footer-ctr" id="ctr">1 / 1</div>
  </div>
</div>

<script>
(function() {{
  var SLIDES = {slides_js};
  var N = SLIDES.length;
  var cur = 0;
  var paused = false;
  var timer = null;
  var pbTimer = null;

  var slidesEl = document.getElementById('slides');
  var dotsEl   = document.getElementById('dots');
  var ctrEl    = document.getElementById('ctr');
  var pb       = document.getElementById('pb');

  // Build slides
  SLIDES.forEach(function(s, i) {{
    var sd = document.createElement('div');
    sd.className = 'slide' + (i === 0 ? ' active' : '');
    sd.id = 'sl' + i;

    var imgHtml = '';
    if (s.img) {{
      imgHtml = '<img class="slide-img" src="' + s.img + '" alt="" onerror="this.style.display=\\'none\\';this.nextElementSibling.style.display=\\'flex\\';">'
               + '<div class="img-placeholder" style="display:none;">📰</div>';
    }} else {{
      imgHtml = '<div class="img-placeholder">📰</div>';
    }}

    var srcHtml = s.policy
      ? '<span style="color:' + s.accent + '">' + s.flag + ' ' + s.source + '</span><span class="policy-badge">Policy</span>'
      : '<span style="color:' + s.accent + '">' + s.source + '</span>';

    sd.innerHTML = imgHtml
      + '<div class="slide-body">'
      +   '<div class="slide-src">' + srcHtml + '</div>'
      +   '<a class="slide-title" href="' + s.link + '" target="_blank">' + s.title + '</a>'
      +   '<div class="slide-meta">&#128336; 3 sec auto-advance</div>'
      + '</div>';

    slidesEl.appendChild(sd);

    var dot = document.createElement('span');
    dot.className = 'dot' + (i === 0 ? ' active' : '');
    dot.id = 'dot' + i;
    dot.onclick = (function(idx) {{ return function() {{ goTo(idx); }}; }})(i);
    dotsEl.appendChild(dot);
  }});

  function startPB() {{
    clearTimeout(pbTimer);
    pb.style.transition = 'none';
    pb.style.width = '0%';
    pbTimer = setTimeout(function() {{
      pb.style.transition = 'width 3s linear';
      pb.style.width = '100%';
    }}, 40);
  }}

  function goTo(n) {{
    var prev = cur;
    cur = ((n % N) + N) % N;
    if (prev === cur) return;

    var oldEl = document.getElementById('sl' + prev);
    var newEl = document.getElementById('sl' + cur);
    var oldDot = document.getElementById('dot' + prev);
    var newDot = document.getElementById('dot' + cur);

    if (oldEl) {{ oldEl.className = 'slide leaving'; }}
    setTimeout(function() {{
      if (oldEl) oldEl.className = 'slide';
    }}, 450);

    if (newEl) newEl.className = 'slide active';
    if (oldDot) oldDot.className = 'dot';
    if (newDot) newDot.className = 'dot active';
    ctrEl.textContent = (cur + 1) + ' / ' + N;
    startPB();
  }}

  function next() {{ goTo(cur + 1); }}
  function prev() {{ goTo(cur - 1); }}

  document.getElementById('next').onclick = function() {{ next(); restart(); }};
  document.getElementById('prev').onclick = function() {{ prev(); restart(); }};

  function restart() {{
    clearInterval(timer);
    timer = setInterval(function() {{ if (!paused) next(); }}, 3000);
  }}

  document.getElementById('car').addEventListener('mouseenter', function() {{ paused = true; }});
  document.getElementById('car').addEventListener('mouseleave', function() {{ paused = false; }});

  ctrEl.textContent = '1 / ' + N;
  startPB();
  restart();
}})();
</script>
</body>
</html>"""


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

    # ── Rate limit indicator ─────────────────────────────────────────────────
    bucket  = _get_bucket()
    tokens_left = int(bucket._tokens)
    pct_full    = tokens_left / bucket._cap
    bar_color   = "#4ade80" if pct_full > 0.5 else ("#f0c040" if pct_full > 0.2 else "#f87171")
    st.markdown(
        f'<div style="margin:0.6rem 0 0.3rem;">'
        f'<div style="font-family:Space Mono,monospace;font-size:0.52rem;letter-spacing:0.2em;'
        f'color:#4A3858;text-transform:uppercase;margin-bottom:0.3rem;">API Rate Limit</div>'
        f'<div style="background:#0D0B12;border:1px solid rgba(139,58,139,0.22);border-radius:4px;height:5px;overflow:hidden;">'
        f'<div style="height:100%;width:{int(pct_full*100)}%;background:{bar_color};border-radius:4px;'
        f'transition:width 0.4s;"></div></div>'
        f'<div style="font-family:Space Mono,monospace;font-size:0.5rem;color:#4A3858;margin-top:0.2rem;">'
        f'{tokens_left}/{bucket._cap} calls remaining · resets per 60s</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.file_names:
        st.markdown('<div class="sb-lbl">Knowledge Base</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Chunks", st.session_state.chunk_count)
        c2.metric("Docs",   st.session_state.uploaded_docs)
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

# ── STAT STRIP ───────────────────────────────────────────────────────────────
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

# ── MARKET MOOD + GLOBAL INDICES ─────────────────────────────────────────────
fng       = fetch_fear_greed()
fng_val   = fng["value"]
fng_label = fng["label"]

INDEX_SYMS = {
    "^GSPC":  {"name": "S&P 500",  "flag": "🇺🇸"},
    "^IXIC":  {"name": "NASDAQ",   "flag": "🇺🇸"},
    "^FTSE":  {"name": "FTSE 100", "flag": "🇬🇧"},
    "^NSEI":  {"name": "NIFTY 50", "flag": "🇮🇳"},
    "^N225":  {"name": "Nikkei",   "flag": "🇯🇵"},
    "^GDAXI": {"name": "DAX",      "flag": "🇩🇪"},
}
idx_quotes = fetch_multi_quotes(tuple(INDEX_SYMS.keys()))
idx_chips  = ""
for sym, meta in INDEX_SYMS.items():
    info = idx_quotes.get(sym)
    if info:
        arrow = "▲" if info["pct"] >= 0 else "▼"
        cls   = "up" if info["pct"] >= 0 else "down"
        idx_chips += (
            '<div class="mood-idx-chip">'
            f'<div class="mood-idx-name">{meta["flag"]} {meta["name"]}</div>'
            f'<div class="mood-idx-val">{info["price"]:,.0f}</div>'
            f'<div class="mood-idx-chg {cls}">{arrow} {abs(info["pct"]):.2f}%</div>'
            '</div>'
        )

mood_color = "#f87171" if fng_val < 25 else ("#fb923c" if fng_val < 45 else ("#facc15" if fng_val < 55 else ("#86efac" if fng_val < 75 else "#4ade80")))
st.markdown(f"""
<div class="mood-bar-wrap">
  <div class="mood-title">◈ Market Mood &amp; Global Indices</div>
  <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.7rem;">
    <div>
      <div style="display:flex;align-items:baseline;gap:0.4rem;">
        <span class="mood-index" style="color:{mood_color};">{fng_val}</span>
        <span style="font-family:'Space Mono',monospace;font-size:0.62rem;letter-spacing:0.1em;color:{mood_color};">{fng_label}</span>
      </div>
      <div style="font-family:'Space Mono',monospace;font-size:0.5rem;color:#4A3858;margin-top:0.2rem;">Crypto Fear &amp; Greed · alternative.me</div>
    </div>
    <div style="flex:1;">
      <div class="mood-track"><div class="mood-needle" style="left:{fng_val}%;"></div></div>
      <div class="mood-labels"><span>Extreme Fear</span><span>Fear</span><span>Neutral</span><span>Greed</span><span>Extreme Greed</span></div>
    </div>
  </div>
  <div class="mood-indices">{idx_chips}</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# NEWS CAROUSELS — rendered inside iframes so JS runs freely
# ══════════════════════════════════════════════════════════════════════════════
news_items   = get_all_news()
policy_items = get_policy_news()

car_col1, car_col2 = st.columns(2)
with car_col1:
    if news_items:
        components.html(build_carousel_html(news_items, is_policy=False, height_px=400), height=400, scrolling=False)
    else:
        st.info("News unavailable — check back in a moment.")
with car_col2:
    if policy_items:
        components.html(build_carousel_html(policy_items, is_policy=True, height_px=400), height=400, scrolling=False)
    else:
        st.info("Policy news unavailable.")

# ══════════════════════════════════════════════════════════════════════════════
# COMMODITIES
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
comm_chips  = "".join(
    make_chip_html(sym, f"{name} · {unit}", info["price"], info["pct"], prefix="$", decimals=dec, icon=icon)
    for sym, (name, unit, icon, dec) in COMMODITY_SYMS.items()
    if (info := comm_quotes.get(sym))
)
if comm_chips:
    st.markdown(
        '<div class="comm-panel"><div class="comm-title">Precious Metals &amp; Commodities</div>'
        '<div class="chips-row">' + comm_chips + '</div>'
        '<div style="font-family:Space Mono,monospace;font-size:0.5rem;color:#4A3858;margin-top:0.65rem;text-align:right;">Futures · Yahoo Finance · 60s cache</div>'
        '</div>',
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# CRYPTO
# ══════════════════════════════════════════════════════════════════════════════
CRYPTO_SYMS = {
    "BTC-USD":  ("Bitcoin",   "BTC",  "₿",  2),
    "ETH-USD":  ("Ethereum",  "ETH",  "Ξ",  2),
    "BNB-USD":  ("BNB",       "BNB",  "🔶", 2),
    "SOL-USD":  ("Solana",    "SOL",  "◎",  2),
    "XRP-USD":  ("XRP",       "XRP",  "✕",  4),
    "DOGE-USD": ("Dogecoin",  "DOGE", "🐕", 5),
    "ADA-USD":  ("Cardano",   "ADA",  "🔵", 4),
    "AVAX-USD": ("Avalanche", "AVAX", "🔺", 2),
}
crypto_quotes = fetch_multi_quotes(tuple(CRYPTO_SYMS.keys()))
crypto_chips  = "".join(
    make_chip_html(ticker, name, info["price"], info["pct"], prefix="$", decimals=dec, icon=icon)
    for sym, (name, ticker, icon, dec) in CRYPTO_SYMS.items()
    if (info := crypto_quotes.get(sym))
)
if crypto_chips:
    st.markdown(
        '<div class="crypto-panel"><div class="crypto-title">Crypto Markets</div>'
        '<div class="chips-row">' + crypto_chips + '</div>'
        '<div style="font-family:Space Mono,monospace;font-size:0.5rem;color:#4A3858;margin-top:0.65rem;text-align:right;">Spot · Yahoo Finance · 60s cache</div>'
        '</div>',
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
    '<div style="font-family:\'Cormorant Garamond\',serif;font-size:1.1rem;font-weight:300;color:#EDE8F5;margin-bottom:0.8rem;'
    'display:flex;align-items:center;gap:0.5rem;">'
    '<span style="display:inline-block;width:3px;height:1.1rem;background:linear-gradient(180deg,#6B2D6B,#C084C8);border-radius:2px;"></span>'
    'Live Stock Chart</div>',
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
    stock_quotes = fetch_multi_quotes(tuple(symbols))
    chip_parts = []
    for sym in symbols:
        info = stock_quotes.get(sym)
        if info:
            arrow     = "▲" if info["pct"] >= 0 else "▼"
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
        s = fetch_yahoo_series(sym, period_map[rng], interval_map[rng])
        if s is not None and not s.empty:
            chart[sym] = s
    if not chart.empty:
        normed = (chart.dropna(how="all").ffill() / chart.dropna(how="all").ffill().iloc[0] - 1) * 100
        st.line_chart(normed, height=230, use_container_width=True)
        st.caption(f"% return from period start · {rng} · Yahoo Finance")
    else:
        st.warning("Chart data unavailable — try again in a moment.")
else:
    st.info("Select at least one symbol above.")
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

st.markdown('<div class="fx-panel"><div class="fx-panel-title">Currencies vs USD</div>', unsafe_allow_html=True)

fx_r1, fx_r2 = st.columns([5, 1])
with fx_r1:
    selected_labels = st.multiselect(
        "currencies", options=list(fx_options.keys()), default=default_labels,
        label_visibility="collapsed", key="fx_select",
    )
with fx_r2:
    fx_rng = st.selectbox("fx_range", ["1M","3M","6M","1Y"], index=0, label_visibility="collapsed", key="fx_rng")

selected_syms = [fx_options[lbl] for lbl in selected_labels]
st.session_state["fx_select_syms"] = selected_syms

fx_period   = {"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y"}
fx_interval = {"1M":"1d", "3M":"1d", "6M":"1d", "1Y":"1wk"}

if selected_syms:
    fx_chart = pd.DataFrame()
    for sym in selected_syms:
        meta = ALL_FX[sym]
        s    = fetch_yahoo_series(sym, fx_period[fx_rng], fx_interval[fx_rng])
        if s is not None and not s.empty:
            if meta["invert"]:
                s = 1.0 / s
            s = (s / s.iloc[0] - 1) * 100
            s.name = meta["flag"] + " " + meta["label"]
            fx_chart[s.name] = s
    if not fx_chart.empty:
        st.line_chart(fx_chart.dropna(how="all").ffill(), height=220, use_container_width=True)
        st.caption(f"% change from {fx_rng} start · Rising = USD strengthening · EUR/GBP inverted · Yahoo Finance")
    else:
        st.warning("Chart unavailable — try again shortly.")

    fx_quotes = fetch_multi_quotes(tuple(selected_syms))
    chip_parts_fx = []
    for sym in selected_syms:
        meta = ALL_FX[sym]
        info = fx_quotes.get(sym)
        if info:
            rate      = info["price"]
            pct       = info["pct"]
            rate_str  = f"{rate:,.2f}" if rate >= 10 else f"{rate:.4f}"
            arrow     = "▲" if pct > 0.005 else ("▼" if pct < -0.005 else "●")
            cls       = "up" if pct > 0.005 else ("down" if pct < -0.005 else "flat")
            chip_parts_fx.append(
                '<div class="price-chip">'
                f'<div class="pc-sym">{meta["flag"]} {meta["label"]}</div>'
                f'<div class="pc-name">{meta["name"]}</div>'
                f'<div class="pc-val">{rate_str}</div>'
                f'<div class="pc-chg {cls}">{arrow} {abs(pct):.3f}%</div>'
                '</div>'
            )
    if chip_parts_fx:
        now_ist = _dt.datetime.utcnow() + _dt.timedelta(hours=5, minutes=30)
        st.markdown(
            '<div class="chips-row" style="margin-top:0.75rem;">'
            + "".join(chip_parts_fx) + "</div>"
            + f'<div style="font-family:Space Mono,monospace;font-size:0.5rem;color:#4A3858;margin-top:0.6rem;text-align:right;">Live · {now_ist.strftime("%H:%M")} IST · 60s cache</div>',
            unsafe_allow_html=True,
        )
else:
    st.info("Select at least one currency pair above.")
st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INDIA NEWS & POLICY PANEL
# ══════════════════════════════════════════════════════════════════════════════

NEWS_SOURCES = {
    "📰 Business Standard": {
        "rss": "https://www.business-standard.com/rss/home_page_top_stories.rss",
        "tag": "Markets",
    },
    "📰 Economic Times": {
        "rss": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "tag": "Markets",
    },
    "📰 Mint": {
        "rss": "https://www.livemint.com/rss/markets",
        "tag": "Markets",
    },
    "📰 Hindu BusinessLine": {
        "rss": "https://www.thehindubusinessline.com/markets/feeder/default.rss",
        "tag": "Markets",
    },
    "🏛️ RBI Notifications": {
        "rss": "https://www.rbi.org.in/Scripts/Notifications_Rss.aspx",
        "tag": "Policy",
    },
    "🏛️ SEBI Orders": {
        "rss": "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doGetPublicationRss=yes&rssHead=4",
        "tag": "Policy",
    },
    "🏛️ Finance Ministry": {
        "rss": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
        "tag": "Policy",
    },
    "🏛️ PIB – Economy": {
        "rss": "https://pib.gov.in/RssMain.aspx?ModId=4&Lang=1&Regid=3",
        "tag": "Policy",
    },
}

@st.cache_data(ttl=600)   # 10-minute cache for news
def fetch_rss(url: str, max_items: int = 6):
    """Parse an RSS feed and return list of {title, link, date, summary}."""
    import xml.etree.ElementTree as ET
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }
    try:
        r = requests.get(url, headers=headers, timeout=12)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        ns   = {"media": "http://search.yahoo.com/mrss/"}
        items = root.findall(".//item")
        results = []
        for item in items[:max_items]:
            title   = (item.findtext("title") or "").strip()
            link    = (item.findtext("link")  or "").strip()
            pub     = (item.findtext("pubDate") or "").strip()
            desc    = (item.findtext("description") or "").strip()
            # Strip HTML tags from description
            import re
            desc = re.sub(r"<[^>]+>", "", desc)[:180].strip()
            # Shorten date
            try:
                from email.utils import parsedate_to_datetime
                dt  = parsedate_to_datetime(pub)
                pub = dt.strftime("%d %b, %H:%M")
            except Exception:
                pub = pub[:16]
            if title:
                results.append({"title": title, "link": link, "date": pub, "summary": desc})
        return results
    except Exception:
        return []

# ── Controls row ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.8rem;">
  <span style="display:inline-block;width:3px;height:1.4rem;background:linear-gradient(180deg,#6B2D6B,#C084C8);border-radius:2px;flex-shrink:0;"></span>
  <span style="font-family:'Cormorant Garamond',serif;font-size:1.35rem;font-weight:300;color:#EDE8F5;">
    India News &amp; Policy
  </span>
</div>
""", unsafe_allow_html=True)

news_ctrl1, news_ctrl2, news_ctrl3 = st.columns([3, 2, 1])
with news_ctrl1:
    sel_sources = st.multiselect(
        "sources",
        options=list(NEWS_SOURCES.keys()),
        default=["📰 Economic Times", "📰 Business Standard", "🏛️ RBI Notifications", "🏛️ Finance Ministry"],
        label_visibility="collapsed",
        key="news_sources",
    )
with news_ctrl2:
    news_filter = st.selectbox(
        "filter", ["All", "Markets", "Policy"],
        index=0, label_visibility="collapsed", key="news_filter"
    )
with news_ctrl3:
    n_per_source = st.selectbox(
        "items", [3, 5, 8, 10],
        index=0, label_visibility="collapsed", key="news_n"
    )

# Apply tag filter
active_sources = [
    s for s in sel_sources
    if news_filter == "All" or NEWS_SOURCES[s]["tag"] == news_filter
]

if active_sources:
    # Fetch all selected feeds
    all_articles: list[dict] = []
    for src_name in active_sources:
        src_cfg  = NEWS_SOURCES[src_name]
        articles = fetch_rss(src_cfg["rss"], max_items=n_per_source)
        for a in articles:
            a["source"]  = src_name
            a["src_tag"] = src_cfg["tag"]
        all_articles.extend(articles)

    if all_articles:
        # Split into 2 columns for compact display
        left_arts  = all_articles[0::2]
        right_arts = all_articles[1::2]

        def render_card(a: dict) -> str:
            tag_color   = "#C084C8" if a["src_tag"] == "Policy" else "#4ade80"
            tag_bg      = "rgba(192,132,200,0.1)" if a["src_tag"] == "Policy" else "rgba(74,222,128,0.08)"
            tag_border  = "rgba(192,132,200,0.3)"  if a["src_tag"] == "Policy" else "rgba(74,222,128,0.25)"
            src_short   = a["source"].replace("📰 ","").replace("🏛️ ","")
            title_esc   = a["title"].replace('"', "&quot;").replace("'", "&#39;")
            link        = a.get("link", "#") or "#"
            summary     = a.get("summary", "")
            date_str    = a.get("date", "")
            return f"""
<div style="background:#0D0B12;border:1px solid rgba(139,58,139,0.22);border-radius:10px;
            padding:0.8rem 1rem;margin-bottom:0.6rem;border-left:3px solid {tag_color};
            transition:all 0.2s;">
  <div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.4rem;flex-wrap:wrap;">
    <span style="background:{tag_bg};border:1px solid {tag_border};color:{tag_color};
                 font-family:'Space Mono',monospace;font-size:0.52rem;letter-spacing:0.1em;
                 padding:0.1rem 0.4rem;border-radius:3px;text-transform:uppercase;">
      {a['src_tag']}
    </span>
    <span style="font-family:'Space Mono',monospace;font-size:0.52rem;color:#4A3858;">
      {src_short}
    </span>
    <span style="font-family:'Space Mono',monospace;font-size:0.5rem;color:#4A3858;margin-left:auto;">
      {date_str}
    </span>
  </div>
  <a href="{link}" target="_blank" style="text-decoration:none;">
    <div style="font-family:'Syne',sans-serif;font-size:0.82rem;font-weight:500;
                color:#EDE8F5;line-height:1.45;margin-bottom:0.35rem;
                cursor:pointer;">
      {title_esc}
    </div>
  </a>
  <div style="font-family:'Syne',sans-serif;font-size:0.72rem;color:#4A3858;
              line-height:1.5;overflow:hidden;display:-webkit-box;
              -webkit-line-clamp:2;-webkit-box-orient:vertical;">
    {summary}
  </div>
</div>"""

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("".join(render_card(a) for a in left_arts), unsafe_allow_html=True)
        with col_r:
            st.markdown("".join(render_card(a) for a in right_arts), unsafe_allow_html=True)

        import datetime as _ndt
        now_ist_news = _ndt.datetime.utcnow() + _ndt.timedelta(hours=5, minutes=30)
        st.markdown(
            f'<div style="font-family:Space Mono,monospace;font-size:0.5rem;color:#4A3858;'
            f'text-align:right;margin-top:0.2rem;">'
            f'Fetched {now_ist_news.strftime("%H:%M")} IST · {len(all_articles)} articles · 10min cache'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("No articles loaded — feeds may be slow. Try refreshing or selecting different sources.")
else:
    st.info("Select at least one source above, or change the filter to 'All'.")

st.markdown("<hr style='border-color:rgba(139,58,139,0.15);margin:1.4rem 0;'>", unsafe_allow_html=True)

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
        <strong>crypto</strong>, <strong>currency rates</strong> — no documents needed.<br><br>
        Use <strong>＋</strong> to upload financial reports for document analysis.
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
                st.error("Enter your Groq API key first.")
            else:
                try:
                    n = ingest_documents(inline_files)
                    st.success(f"✓ {n} chunks from {len(inline_files)} file(s)")
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

                # Live context
                stock_lines = [
                    f"  {sym}: ${info['price']:,.2f} ({'▲' if info['pct']>=0 else '▼'}{abs(info['pct']):.2f}%)"
                    for sym in symbols if (info := fetch_quote(sym))
                ]
                comm_lines = [
                    f"  {name}: ${info['price']:,.{dec}f} {unit} ({'+' if info['pct']>=0 else ''}{info['pct']:.2f}%)"
                    for sym, (name, unit, _, dec) in COMMODITY_SYMS.items() if (info := fetch_quote(sym))
                ]
                crypto_lines = [
                    f"  {ticker}: ${info['price']:,.{dec}f} ({'+' if info['pct']>=0 else ''}{info['pct']:.2f}%)"
                    for sym, (name, ticker, _, dec) in CRYPTO_SYMS.items() if (info := fetch_quote(sym))
                ]
                fx_lines = []
                for _fxsym in st.session_state.get("fx_select_syms", ("USDINR=X","USDJPY=X","USDCNY=X")):
                    _fxi = fetch_quote(_fxsym)
                    if _fxi:
                        _p = _fxi["price"]
                        _rs = f"{_p:,.2f}" if _p >= 10 else f"{_p:.4f}"
                        _sg = "+" if _fxi["pct"] >= 0 else ""
                        fx_lines.append(f"  {ALL_FX.get(_fxsym,{}).get('label',_fxsym)}: {_rs} ({_sg}{_fxi['pct']:.3f}%)")

                utc_now = _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
                live_context = f"""=== LIVE MARKET DATA ({utc_now}) ===
STOCKS:\n{chr(10).join(stock_lines) or '  (none)'}
COMMODITIES:\n{chr(10).join(comm_lines) or '  (unavailable)'}
CRYPTO:\n{chr(10).join(crypto_lines) or '  (unavailable)'}
CURRENCIES (vs USD):\n{chr(10).join(fx_lines) or '  (unavailable)'}
MARKET MOOD: Fear & Greed = {fng_val} ({fng_label})""".strip()

                doc_context  = ""
                sources_data = []
                if st.session_state.vectorstore:
                    vs    = st.session_state.vectorstore
                    q_emb = vs["model"].encode([q], normalize_embeddings=True).tolist()
                    res   = vs["collection"].query(query_embeddings=q_emb, n_results=5, include=["documents","metadatas","distances"])
                    cks, mts, dts = res["documents"][0], res["metadatas"][0], res["distances"][0]
                    doc_context  = "\n---\n".join(f"[{m['filename']}]\n{c}" for c, m in zip(cks, mts))
                    sources_data = [{"filename":m["filename"],"score":round(1-d/2,3),"preview":c[:220]} for c,m,d in zip(cks,mts,dts)]

                user_msg = (
                    f"{live_context}\n\n=== DOCUMENT CONTEXT ===\n{doc_context}\n\nQuestion: {q}"
                    if doc_context else f"{live_context}\n\nQuestion: {q}"
                )

                resp = oai.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": (
                            "You are an expert financial analyst with real-time data access. "
                            "You have live prices for stocks, gold, silver, oil, crypto, and FX rates. "
                            "Use live data for market questions. For document questions, cite specific numbers. "
                            "Be concise, precise, never fabricate numbers."
                        )},
                        *[{"role":m["role"],"content":m["content"]} for m in st.session_state.messages[:-1]],
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=0.15, max_tokens=1500,
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
                st.session_state.messages.append({"role":"assistant","content":answer,"sources":sources_data})

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
