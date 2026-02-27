from __future__ import annotations
"""
app.py  —  Financial RAG Assistant  v9
Changes from v8:
  ① Aesthetic + upload button (animated SVG circle with rotate-on-hover)
  ② Price chips get red diagonal sweep when down, green when up (CSS ::before overlay)
  ③ Mood index chips same red/green top-bar + border treatment
  ④ FX chips same treatment
  ⑤ Global stock search — Yahoo Finance fuzzy search, any exchange world-wide
  ⑥ 200+ pre-loaded tickers across 20 markets (US, India, UK, DE, FR, JP, HK, KR, AU, CA, BR, SG…)
  ⑦ Exchange suffix guide in portfolio tab
  ⑧ Manage Holdings: search-to-add from any world exchange
Run: streamlit run app.py
"""

import os, re, json, math, io, html as _ht
import datetime as _dt
import threading as _th, time as _tm
import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from typing import Optional

# ── Portfolio / charting deps (graceful degradation if missing) ──────────────
try:
    import yfinance as yf
    import numpy as np
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    from scipy import stats as scipy_stats
    _PORTFOLIO_READY = True
except ImportError:
    _PORTFOLIO_READY = False

load_dotenv()

st.set_page_config(
    page_title="Financial RAG Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for _k, _v in [
    ("messages",        []),
    ("vectorstore",     None),
    ("uploaded_docs",   0),
    ("chunk_count",     0),
    ("file_names",      []),
    ("show_upload",     False),
    ("show_chat",       False),
    ("doc_full_text",   ""),
    ("auto_metrics",    []),
    ("auto_generated",  False),
    ("search_query",    ""),
    ("search_results",  []),
    ("show_analytics",      False),
    # v7: portfolio
    ("show_portfolio",      False),
    ("portfolio_holdings",  {}),
    ("portfolio_watchlist", []),
    ("portfolio_prices_cache", {}),
    ("portfolio_ai_report", ""),
    # v8: analyst mode
    ("analyst_mode",        False),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ─────────────────────────────────────────────────────────────────────────────
# HIDE STREAMLIT CHROME + RESPONSIVE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu,footer,header,[data-testid="stToolbar"],
[data-testid="stDecoration"],.stDeployButton{display:none!important}
[data-testid="collapsedControl"]{background:rgba(107,45,107,.18)!important;
  border:1px solid rgba(139,58,139,.45)!important;border-radius:8px!important;
  color:#C084C8!important;top:.9rem!important}
[data-testid="collapsedControl"]:hover{background:rgba(107,45,107,.35)!important;
  box-shadow:0 0 12px rgba(107,45,107,.4)!important}
@media(max-width:1024px){[data-testid="block-container"]{padding:0 1rem!important}
  .stat-strip{grid-template-columns:repeat(2,1fr)!important}}
@media(max-width:767px){[data-testid="block-container"]{padding:0 .5rem!important;max-width:100%!important}
  .stat-strip{grid-template-columns:repeat(2,1fr)!important}
  .rag-header h1{font-size:2rem!important}.rag-header{padding:1.2rem 1rem!important}}
@media(max-width:479px){.stat-strip{grid-template-columns:1fr!important}
  .rag-header h1{font-size:1.6rem!important}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Syne:wght@400;500;600;700&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');
:root{--black:#07060C;--card:#0D0B12;--card-2:#120E1A;--panel:#0F0C16;
  --border:rgba(139,58,139,.22);--border-l:rgba(176,107,176,.45);
  --velvet:#6B2D6B;--velvet-gl:#B06BB0;--accent:#C084C8;--lilac:#D4A8D8;
  --text:#EDE8F5;--text-dim:#9A8AAA;--text-ghost:#4A3858;
  --green:#4ADE80;--red:#F87171;--gold:#F0C040}
*,*::before,*::after{box-sizing:border-box}
html,body,[class*="css"]{font-family:'Syne',sans-serif!important;color:var(--text)!important}
.stApp,[data-testid="stAppViewContainer"]{background:
  radial-gradient(ellipse 110% 55% at 0% 0%,rgba(107,45,107,.20) 0%,transparent 55%),
  radial-gradient(ellipse  80% 50% at 100% 100%,rgba(107,45,107,.14) 0%,transparent 55%),
  var(--black)!important}
[data-testid="stMain"],[data-testid="block-container"]{background:transparent!important;
  padding-top:0!important;max-width:1120px!important}
[data-testid="stSidebar"]{background:var(--panel)!important;
  border-right:1px solid var(--border-l)!important;
  box-shadow:4px 0 40px rgba(107,45,107,.08)!important}
[data-testid="stSidebar"]>div{padding:1.4rem 1.2rem!important}
h1,h2,h3,h4{font-family:'Cormorant Garamond',serif!important;color:var(--text)!important}
code,pre{font-family:'Space Mono',monospace!important}
[data-testid="stMetric"]{background:var(--card)!important;border:1px solid var(--border)!important;
  border-radius:8px!important;padding:.9rem 1rem!important}
[data-testid="stMetricLabel"] p{font-family:'Space Mono',monospace!important;font-size:.58rem!important;
  color:var(--text-ghost)!important;text-transform:uppercase!important;letter-spacing:.18em!important}
[data-testid="stMetricValue"]{font-family:'Cormorant Garamond',serif!important;font-size:1.7rem!important;
  font-weight:300!important;color:var(--accent)!important}
.stButton>button{background:transparent!important;border:1px solid var(--border)!important;
  border-radius:6px!important;color:var(--text-dim)!important;font-family:'Syne',sans-serif!important;
  font-size:.8rem!important;transition:all .22s ease!important;text-align:left!important}
.stButton>button:hover{background:rgba(107,45,107,.14)!important;border-color:var(--velvet-gl)!important;
  color:var(--accent)!important;box-shadow:0 0 18px rgba(107,45,107,.22)!important;transform:translateY(-1px)!important}
.stTextInput input,.stTextArea textarea{background:var(--card)!important;
  border:1px solid var(--border)!important;border-radius:8px!important;color:var(--text)!important}
[data-testid="stChatInput"]{background:var(--card-2)!important;border:1px solid var(--border-l)!important;
  border-radius:14px!important;box-shadow:0 0 30px rgba(107,45,107,.12)!important}
[data-testid="stChatInput"] textarea{background:transparent!important;border:none!important;color:var(--text)!important}
[data-testid="stChatInput"]:focus-within{border-color:rgba(139,58,139,.7)!important}
[data-testid="stChatMessage"]{background:var(--card)!important;border:1px solid var(--border)!important;
  border-radius:12px!important;padding:.8rem 1rem!important;margin-bottom:.5rem!important}
[data-testid="stFileUploader"]{background:rgba(107,45,107,.05)!important;
  border:1.5px dashed rgba(139,58,139,.4)!important;border-radius:10px!important}
[data-testid="stExpander"]{background:var(--card)!important;border:1px solid var(--border)!important;
  border-radius:8px!important}
[data-testid="stAlert"]{background:rgba(107,45,107,.1)!important;
  border:1px solid var(--border-l)!important;border-radius:8px!important}
div[data-testid="stSuccess"]{background:rgba(74,222,128,.07)!important}
div[data-testid="stError"]{background:rgba(248,113,113,.07)!important}
.stProgress>div>div{background:linear-gradient(90deg,var(--velvet),var(--accent))!important}
[data-testid="stMultiSelect"]>div{background:var(--card)!important;
  border-color:var(--border)!important;border-radius:8px!important}
.stMultiSelect span[data-baseweb="tag"]{background:rgba(107,45,107,.3)!important;
  border:1px solid var(--velvet-gl)!important;color:var(--lilac)!important;border-radius:999px!important}
[data-testid="stSelectbox"]>div>div{background:var(--card)!important;
  border-color:var(--border)!important;border-radius:8px!important}
hr{border-color:var(--border)!important}
::-webkit-scrollbar{width:3px}
::-webkit-scrollbar-thumb{background:rgba(107,45,107,.35);border-radius:2px}

/* ── TOP UPLOAD BAR (sticky) ── */
.top-upload-bar{
  position:sticky;top:0;z-index:2000;
  background:linear-gradient(180deg,rgba(7,6,12,.98) 85%,transparent);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  padding:.5rem 0 .3rem;margin-bottom:.5rem;
  border-bottom:1px solid rgba(139,58,139,.12);
}

/* ── AESTHETIC + UPLOAD BUTTON (legacy small circle, hidden) ── */
.plus-upload-btn{display:none}

/* ══════════════════════════════════════════════════════════════
   TOP ACTION BUTTONS — v11: equal cubes + mood-reactive portfolio
   ══════════════════════════════════════════════════════════════ */

/* Shared cube base — both equal */
.sq-btn-upload div[data-testid="stButton"] > button,
.sq-btn-simulate div[data-testid="stButton"] > button {
  width: 100% !important;
  height: 4.8rem !important;
  border-radius: 14px !important;
  padding: .45rem .5rem !important;
  font-family: 'Space Mono', monospace !important;
  font-size: .54rem !important;
  letter-spacing: .12em !important;
  text-transform: uppercase !important;
  line-height: 1.65 !important;
  transition: transform .28s cubic-bezier(.34,1.56,.64,1),
              box-shadow .28s ease,
              background .22s ease,
              border-color .22s ease !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  white-space: pre-line !important;
  position: relative !important;
  overflow: hidden !important;
  gap: 0 !important;
}

/* ── Upload Cube — obsidian with velvet edge glow ── */
@keyframes cube-velvet-pulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(192,132,200,.42), 0 3px 18px rgba(0,0,0,.75); }
  55%      { box-shadow: 0 0 0 9px rgba(192,132,200,0), 0 3px 18px rgba(0,0,0,.75); }
}
.sq-btn-upload div[data-testid="stButton"] > button {
  background: linear-gradient(155deg,#16121f,#0c0a12) !important;
  border: 1.5px solid rgba(192,132,200,.36) !important;
  color: #C084C8 !important;
  animation: cube-velvet-pulse 2.8s ease-in-out infinite !important;
}
.sq-btn-upload div[data-testid="stButton"] > button::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 50% -15%, rgba(192,132,200,.12) 0%, transparent 55%);
  pointer-events: none;
  border-radius: 14px;
}
/* Top edge shimmer */
.sq-btn-upload div[data-testid="stButton"] > button::after {
  content: '';
  position: absolute;
  top: 0; left: 10%; right: 10%; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(192,132,200,.6), transparent);
  border-radius: 1px;
}
.sq-btn-upload div[data-testid="stButton"] > button:hover {
  background: linear-gradient(155deg,#231835,#160f22) !important;
  border-color: rgba(192,132,200,.82) !important;
  color: #EDE8F5 !important;
  transform: translateY(-3px) scale(1.04) !important;
  animation: none !important;
  box-shadow: 0 0 30px rgba(192,132,200,.3), 0 10px 28px rgba(0,0,0,.75) !important;
}

/* ── Portfolio Cube — mood-reactive ── */
/* Default: Neutral gold */
@keyframes mood-neutral-glow {
  0%,100% { box-shadow: 0 0 0 0 rgba(240,192,64,.38), 0 3px 18px rgba(0,0,0,.6); }
  55%      { box-shadow: 0 0 0 8px rgba(240,192,64,0), 0 3px 18px rgba(0,0,0,.6); }
}
@keyframes mood-bull-glow {
  0%,100% { box-shadow: 0 0 0 0 rgba(74,222,128,.42), 0 3px 18px rgba(0,0,0,.55); }
  55%      { box-shadow: 0 0 0 9px rgba(74,222,128,0), 0 3px 18px rgba(0,0,0,.55); }
}
@keyframes mood-bear-glow {
  0%,100% { box-shadow: 0 0 0 0 rgba(248,113,113,.42), 0 3px 18px rgba(0,0,0,.55); }
  55%      { box-shadow: 0 0 0 9px rgba(248,113,113,0), 0 3px 18px rgba(0,0,0,.55); }
}

.sq-btn-simulate div[data-testid="stButton"] > button {
  background: linear-gradient(155deg,rgba(48,35,10,.95),rgba(28,20,5,.98)) !important;
  border: 1.5px solid rgba(240,192,64,.42) !important;
  color: #F0C040 !important;
  animation: mood-neutral-glow 3s ease-in-out infinite !important;
}
.sq-btn-simulate div[data-testid="stButton"] > button::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at 50% -15%, rgba(240,192,64,.09) 0%, transparent 55%);
  pointer-events: none; border-radius: 14px;
}
.sq-btn-simulate div[data-testid="stButton"] > button::after {
  content: '';
  position: absolute;
  top: 0; left: 10%; right: 10%; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(240,192,64,.5), transparent);
  border-radius: 1px;
}

/* Bull market override */
.sq-btn-simulate.mood-bull div[data-testid="stButton"] > button {
  background: linear-gradient(155deg,rgba(12,42,24,.95),rgba(7,25,14,.98)) !important;
  border-color: rgba(74,222,128,.46) !important;
  color: #4ade80 !important;
  animation: mood-bull-glow 2.5s ease-in-out infinite !important;
}
.sq-btn-simulate.mood-bull div[data-testid="stButton"] > button::before {
  background: radial-gradient(ellipse at 50% -15%, rgba(74,222,128,.09) 0%, transparent 55%);
}
.sq-btn-simulate.mood-bull div[data-testid="stButton"] > button::after {
  background: linear-gradient(90deg, transparent, rgba(74,222,128,.5), transparent);
}

/* Bear market override */
.sq-btn-simulate.mood-bear div[data-testid="stButton"] > button {
  background: linear-gradient(155deg,rgba(52,12,12,.95),rgba(30,7,7,.98)) !important;
  border-color: rgba(248,113,113,.46) !important;
  color: #f87171 !important;
  animation: mood-bear-glow 2.5s ease-in-out infinite !important;
}
.sq-btn-simulate.mood-bear div[data-testid="stButton"] > button::before {
  background: radial-gradient(ellipse at 50% -15%, rgba(248,113,113,.09) 0%, transparent 55%);
}
.sq-btn-simulate.mood-bear div[data-testid="stButton"] > button::after {
  background: linear-gradient(90deg, transparent, rgba(248,113,113,.5), transparent);
}

/* Portfolio open state */
.sq-btn-simulate.pf-open div[data-testid="stButton"] > button {
  border-width: 2px !important;
  box-shadow: 0 0 22px rgba(192,132,200,.2), inset 0 0 0 1px rgba(192,132,200,.1) !important;
}

/* Hover — all variants */
.sq-btn-simulate div[data-testid="stButton"] > button:hover,
.sq-btn-simulate.mood-bull div[data-testid="stButton"] > button:hover,
.sq-btn-simulate.mood-bear div[data-testid="stButton"] > button:hover {
  transform: translateY(-3px) scale(1.04) !important;
  animation: none !important;
  filter: brightness(1.22) saturate(1.12) !important;
  box-shadow: 0 10px 30px rgba(0,0,0,.65) !important;
}

.ub-icon{font-size:1.4rem;flex-shrink:0}
.ub-text{font-family:'Space Mono',monospace;font-size:.6rem;letter-spacing:.12em;
  text-transform:uppercase;color:var(--velvet-gl);}
.ub-badge{font-family:'Space Mono',monospace;font-size:.5rem;color:var(--text-ghost);
  background:rgba(107,45,107,.1);border:1px solid var(--border);
  padding:.1rem .4rem;border-radius:3px;margin-left:.3rem;}

/* ── HERO ── */
.rag-header{position:relative;padding:2rem 2.2rem;
  background:linear-gradient(135deg,rgba(107,45,107,.22) 0%,rgba(13,11,18,.98) 55%,rgba(107,45,107,.12) 100%);
  border:1px solid rgba(255,255,255,.08);border-radius:18px;
  box-shadow:0 8px 40px rgba(0,0,0,.4);margin-bottom:1.4rem;overflow:hidden}
.rag-header::before{content:'';position:absolute;top:-80px;right:-80px;width:280px;height:280px;
  border-radius:50%;background:radial-gradient(circle,rgba(107,45,107,.25) 0%,transparent 70%);pointer-events:none}
.rag-header::after{content:'';position:absolute;bottom:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent 0%,rgba(107,45,107,.6) 30%,rgba(192,132,200,.8) 50%,rgba(107,45,107,.6) 70%,transparent 100%)}
.rag-kicker{font-family:'Space Mono',monospace;font-size:.6rem;letter-spacing:.3em;
  color:var(--velvet-gl);text-transform:uppercase;margin-bottom:.9rem;
  display:flex;align-items:center;gap:.6rem}
.rag-kicker::before{content:'';display:inline-block;width:20px;height:1px;background:var(--velvet-gl);opacity:.6}
.rag-header h1{font-family:'Cormorant Garamond',serif!important;font-size:3.2rem!important;
  font-weight:300!important;line-height:1.0!important;color:var(--text)!important;
  margin:0 0 .2rem!important;letter-spacing:-.02em!important}
.rag-header h1 em{font-style:italic;
  background:linear-gradient(135deg,var(--velvet-gl) 0%,var(--accent) 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.rag-header p{font-family:'Syne',sans-serif;font-size:.86rem;color:var(--text-dim);
  margin:.6rem 0 0!important;max-width:480px}
.badge-row{display:flex;gap:.4rem;margin-top:.9rem;flex-wrap:wrap}
.badge{font-family:'Space Mono',monospace;font-size:.62rem;letter-spacing:.08em;padding:.2rem .55rem;
  border-radius:999px;border:1px solid var(--border);color:var(--text-ghost);background:rgba(255,255,255,.04)}
.badge.v{border-color:rgba(139,58,139,.5);color:var(--accent);background:rgba(107,45,107,.12)}
.badge.g{border-color:rgba(74,222,128,.3);color:#86efac;background:rgba(74,222,128,.07)}
.badge.b{border-color:rgba(96,165,250,.4);color:#60a5fa;background:rgba(96,165,250,.07)}

/* ── STAT STRIP ── */
.stat-strip{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;
  background:rgba(107,45,107,.22);border-radius:10px;overflow:hidden;
  border:1px solid rgba(107,45,107,.22);margin-bottom:1.4rem}
.stat-cell{background:var(--card);padding:1rem 1.2rem;position:relative;transition:background .25s}
.stat-cell:hover{background:var(--card-2)}
.stat-cell::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,var(--velvet),var(--accent));opacity:0;transition:opacity .25s}
.stat-cell:hover::before{opacity:1}
.stat-lbl{font-family:'Space Mono',monospace;font-size:.52rem;letter-spacing:.2em;
  text-transform:uppercase;color:var(--text-ghost);margin-bottom:.4rem}
.stat-val{font-family:'Cormorant Garamond',serif;font-size:1.7rem;font-weight:300;
  color:var(--text);line-height:1}
.stat-val.active{color:var(--accent)}
.stat-val-mono{font-family:'Space Mono',monospace;font-size:.68rem;color:var(--accent);line-height:1.4}

/* ── MARKET MOOD ── */
.mood-bar-wrap{background:var(--card);border:1px solid var(--border);border-radius:12px;
  padding:1rem 1.4rem;margin-bottom:1.4rem}
.mood-title{font-family:'Space Mono',monospace;font-size:.58rem;letter-spacing:.2em;
  text-transform:uppercase;color:var(--velvet-gl);margin-bottom:.7rem}
.mood-track{height:6px;border-radius:3px;
  background:linear-gradient(90deg,#f87171 0%,#fb923c 25%,#facc15 50%,#86efac 75%,#4ade80 100%);
  position:relative;margin-bottom:.5rem}
.mood-needle{position:absolute;top:-5px;width:16px;height:16px;border-radius:50%;
  border:2px solid #fff;background:var(--accent);transform:translateX(-50%);
  box-shadow:0 0 8px rgba(192,132,200,.6)}
.mood-labels{display:flex;justify-content:space-between;font-family:'Space Mono',monospace;
  font-size:.5rem;color:var(--text-ghost)}
.mood-index{font-family:'Cormorant Garamond',serif;font-size:2rem;font-weight:300}
.mood-indices{display:flex;gap:1rem;margin-top:.8rem;flex-wrap:wrap}

/* ── PRICE CHIP — with red/green diagonal flash line ── */
.price-chip{
  display:flex;flex-direction:column;
  background:var(--card-2);
  border-radius:10px;padding:.75rem 1rem;min-width:120px;
  font-family:'Space Mono',monospace;transition:all .22s;
  position:relative;overflow:hidden;cursor:default;
  border:1px solid transparent;
}
/* Diagonal colour streak across the card */
.price-chip::before{
  content:'';position:absolute;
  top:0;left:0;right:0;bottom:0;
  pointer-events:none;
  border-radius:10px;
  opacity:.13;
}
.price-chip.chip-up{border-color:rgba(74,222,128,.3);}
.price-chip.chip-up::before{
  background:linear-gradient(135deg,rgba(74,222,128,.9) 0%,transparent 45%);
}
.price-chip.chip-down{border-color:rgba(248,113,113,.3);}
.price-chip.chip-down::before{
  background:linear-gradient(135deg,rgba(248,113,113,.9) 0%,transparent 45%);
}
.price-chip.chip-flat{border-color:rgba(148,163,184,.2);}
.price-chip.chip-flat::before{
  background:linear-gradient(135deg,rgba(148,163,184,.4) 0%,transparent 45%);
}
/* Thin accent line at very top of chip */
.price-chip::after{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  border-radius:10px 10px 0 0;
}
.price-chip.chip-up::after{background:linear-gradient(90deg,#4ade80,transparent);}
.price-chip.chip-down::after{background:linear-gradient(90deg,#f87171,transparent);}
.price-chip.chip-flat::after{background:linear-gradient(90deg,#94a3b8,transparent);}
.price-chip:hover{transform:translateY(-2px);box-shadow:0 6px 24px rgba(0,0,0,.35);}
.pc-sym{font-size:.6rem;color:var(--accent);font-weight:700;letter-spacing:.08em;white-space:nowrap}
.pc-name{font-size:.5rem;color:var(--text-ghost);margin-bottom:.2rem}
.pc-val{font-family:'Cormorant Garamond',serif;font-size:1.5rem;font-weight:300;
  color:var(--text);line-height:1}
.pc-chg.up{font-size:.58rem;color:#4ade80;margin-top:.15rem;display:flex;align-items:center;gap:.2rem}
.pc-chg.down{font-size:.58rem;color:#f87171;margin-top:.15rem;display:flex;align-items:center;gap:.2rem}
.pc-chg.flat{font-size:.58rem;color:var(--text-ghost);margin-top:.15rem}
.chips-row{display:flex;gap:.6rem;flex-wrap:wrap}

/* Mood index chip — same treatment */
.mood-idx-chip{
  display:flex;flex-direction:column;
  border-radius:8px;padding:.4rem .8rem;
  font-family:'Space Mono',monospace;min-width:90px;
  position:relative;overflow:hidden;
  transition:border-color .2s;
}
.mood-idx-chip.chip-up{
  background:rgba(74,222,128,.04);
  border:1px solid rgba(74,222,128,.22);
}
.mood-idx-chip.chip-up::before{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,#4ade80,transparent);border-radius:8px 8px 0 0;
}
.mood-idx-chip.chip-down{
  background:rgba(248,113,113,.04);
  border:1px solid rgba(248,113,113,.22);
}
.mood-idx-chip.chip-down::before{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,#f87171,transparent);border-radius:8px 8px 0 0;
}
.mood-idx-chip.chip-flat{
  background:var(--card-2);border:1px solid var(--border);
}
.mood-idx-name{font-size:.52rem;color:var(--text-ghost);letter-spacing:.1em}
.mood-idx-val{font-size:.72rem;color:var(--text);margin-top:.1rem}
.mood-idx-chg.up{font-size:.56rem;color:#4ade80}
.mood-idx-chg.down{font-size:.56rem;color:#f87171}

/* ── MARKET PANELS ── */
.fx-panel,.comm-panel,.crypto-panel{background:var(--card);border:1px solid var(--border);
  border-radius:12px;padding:1.1rem 1.4rem .9rem;margin-bottom:1.4rem}
.fx-panel-title,.comm-title,.crypto-title{font-family:'Cormorant Garamond',serif;
  font-size:1.1rem;font-weight:300;color:var(--text);margin-bottom:.9rem;
  display:flex;align-items:center;gap:.5rem}
.fx-panel-title::before{content:'';display:inline-block;width:3px;height:1.1rem;
  background:linear-gradient(180deg,var(--velvet),var(--accent));border-radius:2px}
.comm-title::before{content:'';display:inline-block;width:3px;height:1.1rem;
  background:linear-gradient(180deg,#F0C040,#C084C8);border-radius:2px}
.crypto-title::before{content:'';display:inline-block;width:3px;height:1.1rem;
  background:linear-gradient(180deg,#fb923c,#C084C8);border-radius:2px}

/* ── MISC ── */
.sb-lbl{font-family:'Space Mono',monospace;font-size:.54rem;letter-spacing:.22em;
  text-transform:uppercase;color:var(--velvet-gl);padding:1.2rem 0 .45rem;
  border-top:1px solid var(--border);margin-top:.5rem}
.key-ok{display:flex;align-items:center;gap:.5rem;background:rgba(74,222,128,.07);
  border:1px solid rgba(74,222,128,.2);color:#86efac;padding:.38rem .7rem;
  border-radius:6px;font-family:'Space Mono',monospace;font-size:.6rem}
.key-dot{width:5px;height:5px;border-radius:50%;background:#4ade80;
  box-shadow:0 0 6px #4ade80;animation:blink 2s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
.doc-pill{display:flex;align-items:center;gap:.4rem;background:rgba(107,45,107,.1);
  border:1px solid var(--border);padding:.32rem .65rem;border-radius:4px;
  margin-bottom:.3rem;font-family:'Space Mono',monospace;font-size:.58rem;
  color:var(--text-dim);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.doc-dot{width:4px;height:4px;border-radius:50%;background:var(--velvet-gl);flex-shrink:0}
.empty{text-align:center;padding:4rem 2rem}
.empty-orb{width:100px;height:100px;border-radius:50%;
  background:radial-gradient(circle,rgba(107,45,107,.28) 0%,transparent 70%);
  border:1px solid var(--border);margin:0 auto 1.5rem;
  display:flex;align-items:center;justify-content:center;font-size:2rem;color:var(--velvet-gl)}
.empty-title{font-family:'Cormorant Garamond',serif;font-size:1.7rem;font-weight:300;
  font-style:italic;color:var(--text-ghost);margin-bottom:.5rem}
.empty-sub{font-size:.8rem;color:var(--text-ghost);max-width:300px;margin:0 auto;line-height:1.8;opacity:.7}

/* ── INLINE UPLOAD DRAWER ── */
.upload-drawer{background:linear-gradient(135deg,rgba(107,45,107,.18) 0%,rgba(13,11,18,.95) 100%);
  border:1px solid rgba(139,58,139,.45);border-radius:12px;padding:1rem 1.1rem .7rem;margin-bottom:.6rem}
.upload-drawer-title{font-family:'Space Mono',monospace;font-size:.62rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--velvet-gl);margin-bottom:.6rem}
.src-card{background:var(--card);border:1px solid var(--border);border-left:3px solid var(--velvet-gl);
  border-radius:0 8px 8px 0;padding:.7rem .9rem;margin:.4rem 0;font-size:.82rem}
.src-name{font-family:'Space Mono',monospace;font-size:.7rem;color:var(--accent);margin-bottom:.15rem}
.src-score{font-family:'Space Mono',monospace;font-size:.62rem;color:var(--text-ghost)}
.src-preview{color:var(--text-dim);line-height:1.55;margin-top:.2rem}

/* ── CHAT PANEL ── */
.chat-panel{background:var(--card);border:1px solid var(--border-l);
  border-radius:16px;padding:1.2rem 1.4rem;margin-bottom:1.4rem}
.chat-panel-title{font-family:'Cormorant Garamond',serif;font-size:1.15rem;font-weight:300;
  color:var(--text);margin-bottom:1rem;display:flex;align-items:center;gap:.5rem}
.chat-panel-title::before{content:'';display:inline-block;width:3px;height:1.1rem;
  background:linear-gradient(180deg,#60a5fa,#C084C8);border-radius:2px}

/* ── ANALYTICS PANEL (inline) ── */
.analytics-panel{background:linear-gradient(135deg,rgba(74,222,128,.04) 0%,rgba(107,45,107,.08) 100%);
  border:1px solid rgba(74,222,128,.18);border-radius:14px;
  padding:1.2rem 1.4rem;margin-bottom:1.4rem}
.analytics-panel-hdr{font-family:'Cormorant Garamond',serif;font-size:1.35rem;font-weight:300;
  color:#EDE8F5;margin-bottom:.3rem;display:flex;align-items:center;gap:.6rem}
.analytics-panel-hdr::before{content:'';display:inline-block;width:3px;height:1.2rem;
  background:linear-gradient(180deg,#4ade80,#C084C8);border-radius:2px}
.analytics-panel-sub{font-family:'Space Mono',monospace;font-size:.54rem;
  letter-spacing:.15em;text-transform:uppercase;color:#4A3858;margin-bottom:1rem}

/* ── ANALYTICS BANNER ── */
.analytics-banner{
  background:linear-gradient(135deg,rgba(74,222,128,.07) 0%,rgba(107,45,107,.10) 100%);
  border:1px solid rgba(74,222,128,.22);border-radius:10px;
  padding:.7rem 1.1rem;margin-bottom:1rem;
  display:flex;align-items:flex-start;gap:.75rem}
.ab-icon{font-size:1.4rem;flex-shrink:0;line-height:1.2}
.ab-title{font-family:'Syne',sans-serif;font-size:.84rem;font-weight:600;color:#86efac;margin-bottom:.1rem}
.ab-sub{font-family:'Space Mono',monospace;font-size:.52rem;color:var(--text-ghost)}

/* ── SEARCH BAR ── */
.gsearch-wrap{
  background:var(--card);border:1px solid var(--border);border-radius:10px;
  padding:.6rem .9rem;margin-bottom:.9rem;}
.sr-wrap{background:var(--card);border:1px solid var(--border);
  border-radius:10px;padding:.75rem 1rem;margin-bottom:.9rem}
.sr-title{font-family:'Space Mono',monospace;font-size:.52rem;letter-spacing:.18em;
  text-transform:uppercase;color:var(--accent);margin-bottom:.6rem}
.sr-hit{background:var(--card-2);border:1px solid var(--border);
  border-left:3px solid var(--accent);border-radius:0 8px 8px 0;
  padding:.55rem .9rem;margin-bottom:.4rem}
.sr-fname{font-family:'Space Mono',monospace;font-size:.56rem;color:var(--accent);margin-bottom:.18rem}
.sr-snippet{font-size:.79rem;color:var(--text-dim);line-height:1.55}

/* ── COMPARISON TABLE ── */
.cmp-table{width:100%;border-collapse:collapse;font-size:.75rem}
.cmp-table th{background:rgba(107,45,107,.18);border:1px solid var(--border);
  padding:.45rem .8rem;font-family:'Space Mono',monospace;font-size:.5rem;
  text-transform:uppercase;letter-spacing:.12em;color:var(--velvet-gl);text-align:left}
.cmp-table td{border:1px solid var(--border);padding:.4rem .8rem;
  font-family:'Space Mono',monospace;color:var(--text-dim);vertical-align:top}
.cmp-table tr:nth-child(even) td{background:rgba(107,45,107,.04)}
.td-doc{color:var(--accent)!important}
.td-mkt{color:#86efac!important}
.td-pos{color:#4ade80!important}
.td-neg{color:#f87171!important}
.td-neu{color:var(--text-ghost)!important}

/* ════════════════════════════════════════════
   v8  SOURCE PANEL + ANALYST MODE STYLES
   ════════════════════════════════════════════ */

/* Mode toggle bar */
.mode-toggle-bar{
  display:flex;align-items:center;gap:.5rem;
  background:rgba(107,45,107,.08);border:1px solid rgba(139,58,139,.25);
  border-radius:10px;padding:.35rem .5rem;margin-bottom:.7rem;
}
.mode-toggle-label{
  font-family:'Space Mono',monospace;font-size:.52rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--text-ghost);margin-right:.4rem;
}
.mode-pill{
  font-family:'Space Mono',monospace;font-size:.58rem;letter-spacing:.06em;
  padding:.28rem .7rem;border-radius:6px;cursor:pointer;transition:all .2s;
  border:1px solid transparent;text-transform:uppercase;
}
.mode-pill.chat-pill{
  background:rgba(107,45,107,.2);border-color:rgba(139,58,139,.4);color:var(--accent);
}
.mode-pill.analyst-pill{
  background:rgba(240,192,64,.1);border-color:rgba(240,192,64,.35);color:var(--gold);
}
.mode-pill.inactive{
  background:transparent!important;border-color:transparent!important;color:var(--text-ghost)!important;
}

/* Source evidence panel */
.src-evidence-wrap{
  margin-top:.6rem;
  border:1px solid rgba(139,58,139,.22);border-radius:10px;overflow:hidden;
}
.src-evidence-hdr{
  display:flex;align-items:center;justify-content:space-between;
  padding:.45rem .85rem;
  background:linear-gradient(90deg,rgba(107,45,107,.18),rgba(13,11,18,.9));
  border-bottom:1px solid rgba(139,58,139,.18);
}
.src-evidence-title{
  font-family:'Space Mono',monospace;font-size:.52rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--velvet-gl);
  display:flex;align-items:center;gap:.45rem;
}
.src-evidence-count{
  font-family:'Space Mono',monospace;font-size:.48rem;
  background:rgba(107,45,107,.2);border:1px solid rgba(139,58,139,.3);
  color:var(--accent);padding:.1rem .38rem;border-radius:4px;
}
.src-chunk{
  padding:.7rem .9rem;border-bottom:1px solid rgba(139,58,139,.1);
  position:relative;transition:background .2s;
}
.src-chunk:last-child{border-bottom:none}
.src-chunk:hover{background:rgba(107,45,107,.05)}
.src-chunk-head{
  display:flex;align-items:center;justify-content:space-between;
  flex-wrap:wrap;gap:.3rem;margin-bottom:.4rem;
}
.src-chunk-file{
  font-family:'Space Mono',monospace;font-size:.58rem;color:var(--accent);
  display:flex;align-items:center;gap:.35rem;
}
.src-chunk-meta{
  display:flex;align-items:center;gap:.4rem;flex-wrap:wrap;
}
.src-badge{
  font-family:'Space Mono',monospace;font-size:.46rem;letter-spacing:.08em;
  text-transform:uppercase;padding:.1rem .38rem;border-radius:4px;
}
.src-badge.page{background:rgba(96,165,250,.1);border:1px solid rgba(96,165,250,.25);color:#60a5fa;}
.src-badge.section{background:rgba(192,132,200,.1);border:1px solid rgba(192,132,200,.25);color:var(--accent);}
.src-badge.score-hi{background:rgba(74,222,128,.1);border:1px solid rgba(74,222,128,.25);color:#4ade80;}
.src-badge.score-md{background:rgba(240,192,64,.1);border:1px solid rgba(240,192,64,.25);color:var(--gold);}
.src-badge.score-lo{background:rgba(148,163,184,.1);border:1px solid rgba(148,163,184,.2);color:#94a3b8;}
.src-chunk-text{
  font-family:'Syne',sans-serif;font-size:.78rem;color:var(--text-dim);line-height:1.65;
  border-left:2px solid rgba(139,58,139,.3);padding-left:.6rem;
  display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden;
}
.src-chunk-text.expanded{-webkit-line-clamp:unset;overflow:visible;}
.src-expand-hint{
  font-family:'Space Mono',monospace;font-size:.46rem;color:var(--text-ghost);
  margin-top:.3rem;cursor:pointer;text-align:right;
}

/* Analyst mode output */
.analyst-card{
  background:linear-gradient(135deg,rgba(107,45,107,.12) 0%,rgba(13,11,18,.97) 100%);
  border:1px solid rgba(192,132,200,.3);border-radius:14px;
  padding:1.1rem 1.3rem;margin-top:.4rem;overflow:hidden;
  position:relative;
}
.analyst-card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,var(--gold),var(--accent),#60a5fa);
}
.analyst-card-hdr{
  display:flex;align-items:center;justify-content:space-between;
  margin-bottom:.9rem;padding-bottom:.6rem;
  border-bottom:1px solid rgba(139,58,139,.18);
}
.analyst-card-title{
  font-family:'Cormorant Garamond',serif;font-size:1.1rem;font-weight:300;
  color:var(--text);display:flex;align-items:center;gap:.5rem;
}
.analyst-card-title::before{
  content:'';display:inline-block;width:3px;height:1rem;
  background:linear-gradient(180deg,var(--gold),var(--accent));border-radius:2px;
}
.analyst-mode-badge{
  font-family:'Space Mono',monospace;font-size:.48rem;letter-spacing:.1em;
  text-transform:uppercase;background:rgba(240,192,64,.1);
  border:1px solid rgba(240,192,64,.3);color:var(--gold);
  padding:.15rem .45rem;border-radius:4px;
}
.analyst-row{
  display:grid;grid-template-columns:repeat(2,1fr);gap:.5rem;margin-bottom:.5rem;
}
.analyst-metric{
  background:rgba(13,11,18,.8);border:1px solid rgba(139,58,139,.2);
  border-radius:8px;padding:.55rem .75rem;
}
.am-label{
  font-family:'Space Mono',monospace;font-size:.46rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--text-ghost);margin-bottom:.25rem;
}
.am-value{
  font-family:'Cormorant Garamond',serif;font-size:1.3rem;font-weight:300;
  color:var(--text);line-height:1;
}
.am-value.pos{color:#4ade80}
.am-value.neg{color:#f87171}
.am-value.neu{color:var(--accent)}
.analyst-section{margin-top:.7rem;}
.analyst-section-title{
  font-family:'Space Mono',monospace;font-size:.5rem;letter-spacing:.18em;
  text-transform:uppercase;color:var(--gold);margin-bottom:.4rem;
  display:flex;align-items:center;gap:.4rem;
}
.analyst-section-title::before{
  content:'';display:inline-block;width:12px;height:1px;background:var(--gold);opacity:.5;
}
.analyst-risk-item{
  display:flex;gap:.5rem;align-items:flex-start;
  font-family:'Syne',sans-serif;font-size:.78rem;color:var(--text-dim);
  padding:.25rem 0;border-bottom:1px solid rgba(139,58,139,.07);line-height:1.5;
}
.analyst-risk-item:last-child{border-bottom:none}
.analyst-risk-bullet{
  flex-shrink:0;width:6px;height:6px;border-radius:50%;
  background:var(--gold);margin-top:.4rem;
}
.analyst-verdict{
  display:flex;align-items:center;gap:.7rem;
  background:rgba(107,45,107,.12);border:1px solid rgba(139,58,139,.25);
  border-radius:8px;padding:.6rem .9rem;margin-top:.7rem;
}
.av-icon{font-size:1.3rem}
.av-text{font-family:'Syne',sans-serif;font-size:.82rem;color:var(--text-dim);line-height:1.55}
.av-text strong{color:var(--text)}

.vfooter{text-align:center;padding:1.8rem 0 .5rem;position:relative;margin-top:2.5rem}
.vfooter::before{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);
  width:180px;height:1px;background:linear-gradient(90deg,transparent,rgba(107,45,107,.5),transparent)}
.vfooter-text{font-family:'Space Mono',monospace;font-size:.56rem;
  letter-spacing:.2em;text-transform:uppercase;color:var(--text-ghost)}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS ENGINE
# ─────────────────────────────────────────────────────────────────────────────
TAXONOMY: dict[str, list[str]] = {
    "Income Statement":["revenue","net revenue","total revenue","net sales","gross profit",
        "gross margin","operating income","ebit","ebitda","net income","net profit",
        "earnings","eps","earnings per share","diluted eps","operating expense",
        "cost of revenue","cost of goods sold","cogs","research and development","r&d",
        "selling general administrative","sg&a","tax","income tax","interest expense"],
    "Balance Sheet":["total assets","total liabilities","shareholders equity",
        "stockholders equity","book value","cash and equivalents","short-term investments",
        "accounts receivable","inventory","goodwill","intangible assets","long-term debt",
        "current liabilities","current assets","retained earnings","common stock","treasury stock"],
    "Cash Flow":["operating cash flow","cash from operations","free cash flow","fcf",
        "capital expenditure","capex","investing activities","financing activities",
        "dividends paid","share repurchase","buyback","depreciation","amortization"],
    "Ratios & Valuation":["p/e ratio","price to earnings","p/b ratio","price to book",
        "roe","return on equity","roa","return on assets","debt to equity","d/e ratio",
        "current ratio","quick ratio","gross margin","net margin","operating margin",
        "ebitda margin","interest coverage","dividend yield","payout ratio",
        "price to sales","ev/ebitda","enterprise value"],
    "Growth & Guidance":["year over year","yoy","quarter over quarter","qoq",
        "guidance","outlook","forecast","projection","growth rate","cagr","compound annual"],
    "Risk Factors":["risk","uncertainty","competition","regulatory","litigation",
        "geopolitical","macroeconomic","supply chain","inflation",
        "interest rate risk","credit risk","liquidity risk","cyber"],
}

def tag_chunk(text: str) -> list[str]:
    tl = text.lower()
    return [c for c, kws in TAXONOMY.items() if any(kw in tl for kw in kws)]

_METRIC_PATTERNS = [
    ("Revenue",          "USD", r"(?:total\s+)?(?:net\s+)?revenue[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
    ("Net Income",       "USD", r"net\s+income[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
    ("Gross Profit",     "USD", r"gross\s+profit[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
    ("Operating Income", "USD", r"operating\s+income[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
    ("EBITDA",           "USD", r"ebitda[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
    ("Free Cash Flow",   "USD", r"free\s+cash\s+flow[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
    ("CapEx",            "USD", r"capital\s+expenditures?[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
    ("EPS (Basic)",      "USD", r"basic\s+(?:earnings|eps)[^\n]{0,60}?\$\s*([\d,\.]+)"),
    ("EPS (Diluted)",    "USD", r"diluted\s+(?:earnings|eps)[^\n]{0,60}?\$\s*([\d,\.]+)"),
    ("Gross Margin",     "%",   r"gross\s+margin[^\n]{0,60}?([\d\.]+)\s*%"),
    ("Net Margin",       "%",   r"net\s+(?:profit\s+)?margin[^\n]{0,60}?([\d\.]+)\s*%"),
    ("Operating Margin", "%",   r"operating\s+margin[^\n]{0,60}?([\d\.]+)\s*%"),
    ("ROE",              "%",   r"return\s+on\s+equity[^\n]{0,60}?([\d\.]+)\s*%"),
    ("ROA",              "%",   r"return\s+on\s+assets[^\n]{0,60}?([\d\.]+)\s*%"),
    ("Debt/Equity",      "x",   r"debt[- ]to[- ]equity[^\n]{0,60}?([\d\.]+)"),
    ("Current Ratio",    "x",   r"current\s+ratio[^\n]{0,60}?([\d\.]+)"),
    ("Shares Outstanding","M",  r"shares?\s+outstanding[^\n]{0,60}?([\d,\.]+)\s*(million|billion|M|B)?"),
]
_SCALE = {"billion":1e9,"b":1e9,"million":1e6,"m":1e6,None:1.0,"":1.0}

def extract_metrics(full_text: str) -> list[dict]:
    tl = full_text.lower(); results: list[dict] = []; seen: set[str] = set()
    for label, unit, pattern in _METRIC_PATTERNS:
        for m in re.finditer(pattern, tl, re.IGNORECASE):
            rn = m.group(1).replace(",","")
            sk = (m.group(2) or "").lower() if m.lastindex and m.lastindex >= 2 else ""
            try:
                val = float(rn) * _SCALE.get(sk, 1.0)
            except:
                continue
            if label in seen:
                continue
            seen.add(label)
            results.append({"label":label,"value":val,"unit":unit,
                             "raw":m.group(0).strip()[:120],"category":_mcat(label)})
    return results

def _mcat(label: str) -> str:
    ll = label.lower()
    if any(k in ll for k in ["eps","diluted","basic"]):   return "Per Share"
    if any(k in ll for k in ["margin","roe","roa","ratio","debt"]): return "Ratios"
    if any(k in ll for k in ["cash flow","capex"]):       return "Cash Flow"
    if any(k in ll for k in ["revenue","income","profit","ebitda"]): return "Income Statement"
    return "Other"

def fmt_val(val: float, unit: str) -> str:
    if unit == "USD":
        if val >= 1e9: return f"${val/1e9:.2f}B"
        if val >= 1e6: return f"${val/1e6:.1f}M"
        if val >= 1e3: return f"${val/1e3:.1f}K"
        return f"${val:.2f}"
    if unit == "%":  return f"{val:.1f}%"
    if unit == "x":  return f"{val:.2f}x"
    if unit == "M":  return f"{val/1e9:.2f}B" if val >= 1e9 else f"{val:.1f}M"
    return f"{val:,.2f}"

def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())

class HybridRetriever:
    def __init__(self, chunks, embeddings):
        self.chunks = chunks; self.embeddings = embeddings; self._bm25 = None; self._ce = None
        try:
            from rank_bm25 import BM25Okapi
            self._bm25 = BM25Okapi([_tokenize(c) for c in chunks])
        except: pass
    def _cos(self, a, b):
        d = sum(x*y for x,y in zip(a,b))
        na = math.sqrt(sum(x*x for x in a)); nb = math.sqrt(sum(x*x for x in b))
        return d/(na*nb+1e-9)
    def retrieve(self, query, qe, n=8, bw=0.35, rerank=True):
        N = len(self.chunks)
        dense = [self._cos(qe, e) for e in self.embeddings]
        if self._bm25:
            br = self._bm25.get_scores(_tokenize(query)); bm = max(br) or 1.0
            bn = [s/bm for s in br]
        else:
            bn = [0.0]*N
        hyb = [(1-bw)*d+bw*b for d,b in zip(dense,bn)]
        cands = sorted(range(N), key=lambda i: hyb[i], reverse=True)[:max(16,n)]
        if rerank:
            try:
                from sentence_transformers import CrossEncoder
                if self._ce is None: self._ce = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-2-v2")
                sc = self._ce.predict([(query, self.chunks[i]) for i in cands]).tolist()
                cands = sorted(cands, key=lambda i: sc[cands.index(i)], reverse=True)
            except: pass
        return [{"idx":i,"chunk":self.chunks[i],"score":hyb[i],"bm25":bn[i],"dense":dense[i]}
                for i in cands[:n]]

VELVET = {"bg":"#07060C","card":"#0D0B12","card2":"#120E1A","border":"rgba(139,58,139,0.25)",
          "accent":"#C084C8","green":"#4ade80","red":"#f87171","gold":"#F0C040",
          "text":"#EDE8F5","dim":"#9A8AAA","ghost":"#4A3858"}
CAT_COLORS = {"Income Statement":"#C084C8","Balance Sheet":"#60a5fa","Cash Flow":"#4ade80",
              "Ratios":"#F0C040","Per Share":"#fb923c","Growth":"#34d399",
              "Risk Factors":"#f87171","Other":"#9A8AAA"}

def _metric_card(label, value, category="Other"):
    c = CAT_COLORS.get(category, VELVET["dim"])
    return (f'<div style="background:{VELVET["card2"]};border:1px solid {VELVET["border"]};'
            f'border-top:2px solid {c};border-radius:10px;padding:.8rem 1rem;">'
            f'<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.15em;'
            f'text-transform:uppercase;color:{VELVET["ghost"]};margin-bottom:.35rem;">{label}</div>'
            f'<div style="font-family:\'Cormorant Garamond\',serif;font-size:1.6rem;font-weight:300;'
            f'color:{VELVET["text"]};line-height:1;">{value}</div>'
            f'<div style="font-family:Space Mono,monospace;font-size:.46rem;color:{c};'
            f'margin-top:.3rem;text-transform:uppercase;letter-spacing:.1em;">{category}</div></div>')

def render_metrics_dashboard(metrics: list[dict]) -> None:
    if not metrics:
        st.info("No financial metrics extracted."); return
    by_cat: dict[str, list] = {}
    for m in metrics: by_cat.setdefault(m["category"], []).append(m)
    for cat in ["Income Statement","Per Share","Cash Flow","Ratios","Balance Sheet","Other"]:
        items = by_cat.get(cat, [])
        if not items: continue
        c = CAT_COLORS.get(cat, VELVET["dim"])
        st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:.56rem;letter-spacing:.2em;'
                    f'text-transform:uppercase;color:{c};margin:1rem 0 .5rem;padding-bottom:.3rem;'
                    f'border-bottom:1px solid rgba(139,58,139,.2);">{cat}</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(items), 4))
        for i, m in enumerate(items):
            with cols[i % 4]:
                st.markdown(_metric_card(m["label"], fmt_val(m["value"],m["unit"]), category=cat),
                            unsafe_allow_html=True)

def render_trend_chart(metrics: list[dict]) -> None:
    for unit, color, lbl in [("USD","#C084C8","USD Metrics (Billions $)"),
                              ("%","#F0C040","% Metrics (Margins & Returns)"),
                              ("x","#4ade80","Ratio Metrics (×)")]:
        items = [m for m in metrics if m["unit"] == unit and m["value"] > 0]
        if not items: continue
        st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:.54rem;letter-spacing:.15em;'
                    f'text-transform:uppercase;color:{color};margin:.8rem 0 .3rem;">{lbl}</div>',
                    unsafe_allow_html=True)
        df = pd.DataFrame(items).set_index("label")["value"]
        if unit == "USD": df = df / 1e9
        st.bar_chart(df, height=160, use_container_width=True)

TEMPLATES = {
    "Revenue Summary":        {"icon":"💰","category":"Income Statement",
        "prompt":"Extract and summarise revenue figures: total revenue, segment breakdown, YoY growth, guidance. Present as a structured table."},
    "Profitability Deep-Dive":{"icon":"📊","category":"Income Statement",
        "prompt":"Analyse profitability: gross profit & margin, operating income & margin, EBITDA, net income & net margin. Compare to prior year. Highlight one-time items."},
    "EPS Analysis":           {"icon":"📈","category":"Per Share",
        "prompt":"What is basic and diluted EPS? Change YoY/QoQ? What drove it — revenue growth, cost cuts, buybacks, or tax?"},
    "Balance Sheet Snapshot": {"icon":"🏦","category":"Balance Sheet",
        "prompt":"Total assets, liabilities, shareholders equity, cash, debt. Debt-to-equity and book value per share."},
    "Liquidity Assessment":   {"icon":"💧","category":"Balance Sheet",
        "prompt":"Current ratio, quick ratio, cash, short-term debt. Is the company at risk of a liquidity crunch?"},
    "Free Cash Flow Analysis":{"icon":"🌊","category":"Cash Flow",
        "prompt":"Operating cash flow, CapEx, FCF, FCF conversion rate. How is cash deployed?"},
    "Capital Allocation":     {"icon":"🎯","category":"Cash Flow",
        "prompt":"Dividends, buybacks, M&A, R&D, debt repayment. What % of FCF returned to shareholders?"},
    "Key Ratios & Benchmarks":{"icon":"⚖️","category":"Ratios",
        "prompt":"ROE, ROA, Gross Margin, Net Margin, Operating Margin, Debt/Equity, Current Ratio, Interest Coverage. Flag concerns."},
    "Risk Factor Summary":    {"icon":"⚠️","category":"Risk Factors",
        "prompt":"Top 5 material risk factors: name, description, financial impact, mitigation."},
    "Growth & Guidance":      {"icon":"🚀","category":"Growth",
        "prompt":"3-year revenue CAGR, management guidance, key growth drivers and headwinds."},
    "Competitive Position":   {"icon":"🏆","category":"Strategy",
        "prompt":"Competitive moat, market share, key differentiators, strategic priorities. What could erode this position?"},
}

EVAL_QUESTIONS = [
    {"id":"fb_001","question":"What was total revenue?","expected_keywords":["revenue","billion","million","$"],"category":"Income Statement"},
    {"id":"fb_002","question":"What was diluted EPS?","expected_keywords":["eps","diluted","$","per share"],"category":"Per Share"},
    {"id":"fb_003","question":"What was the gross margin?","expected_keywords":["gross margin","%","percent"],"category":"Ratios"},
    {"id":"fb_004","question":"What was free cash flow?","expected_keywords":["free cash flow","operating","capex","capital expenditure"],"category":"Cash Flow"},
    {"id":"fb_005","question":"What are the main risk factors?","expected_keywords":["risk","competition","regulatory","uncertainty"],"category":"Risk Factors"},
    {"id":"fb_006","question":"What is the company's revenue guidance?","expected_keywords":["guidance","outlook","forecast","expect","anticipate"],"category":"Growth"},
    {"id":"fb_007","question":"What is the debt-to-equity ratio?","expected_keywords":["debt","equity","ratio","leverage"],"category":"Ratios"},
    {"id":"fb_008","question":"How much did the company spend on R&D?","expected_keywords":["research","development","r&d","billion","million"],"category":"Income Statement"},
]

def score_answer(answer: str, kws: list[str]) -> dict:
    al = answer.lower(); hits = sum(1 for kw in kws if kw.lower() in al)
    return {"recall":hits/len(kws) if kws else 0,"hits":hits,"total":len(kws),
            "score_pct":round(hits/len(kws)*100 if kws else 0,1)}

def render_eval_dashboard(results: list[dict]) -> None:
    if not results: return
    avg = sum(r["score"]["score_pct"] for r in results) / len(results)
    c = VELVET["green"] if avg >= 70 else (VELVET["gold"] if avg >= 40 else VELVET["red"])
    st.markdown(f'<div style="background:{VELVET["card2"]};border:1px solid {VELVET["border"]};'
                f'border-radius:10px;padding:1rem 1.2rem;margin-bottom:1rem;">'
                f'<div style="font-family:Space Mono,monospace;font-size:.54rem;letter-spacing:.15em;'
                f'text-transform:uppercase;color:{VELVET["ghost"]};">Overall Recall Score</div>'
                f'<div style="font-family:Cormorant Garamond,serif;font-size:2.2rem;font-weight:300;color:{c};">{avg:.1f}%</div>'
                f'<div style="font-family:Space Mono,monospace;font-size:.5rem;color:{VELVET["ghost"]};">{len(results)} questions evaluated</div>'
                f'</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([{"Question":r["question"][:60]+"…","Category":r.get("category","—"),
                                 "Score":f'{r["score"]["score_pct"]}%',"Hits":f'{r["score"]["hits"]}/{r["score"]["total"]}'}
                                for r in results]), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# DOC vs MARKET COMPARISON
# ─────────────────────────────────────────────────────────────────────────────
SECTOR_BENCHMARKS = {
    "Gross Margin":     {"Technology":55,"Financials":40,"Energy":30,"Healthcare":50,
                         "Industrials":33,"Consumer Discretionary":30,"Consumer Staples":28,"S&P 500 Avg":38},
    "Net Margin":       {"Technology":22,"Financials":18,"Energy":8,"Healthcare":14,
                         "Industrials":9,"Consumer Discretionary":6,"Consumer Staples":8,"S&P 500 Avg":11.5},
    "Operating Margin": {"Technology":28,"Financials":20,"Energy":12,"Healthcare":16,
                         "Industrials":12,"Consumer Discretionary":9,"Consumer Staples":10,"S&P 500 Avg":15},
    "ROE":              {"Technology":35,"Financials":12,"Energy":18,"Healthcare":22,
                         "Industrials":20,"Consumer Discretionary":28,"Consumer Staples":25,"S&P 500 Avg":19},
    "ROA":              {"Technology":15,"Financials":1.2,"Energy":7,"Healthcare":9,
                         "Industrials":7.5,"Consumer Discretionary":7,"Consumer Staples":8,"S&P 500 Avg":8},
}

SECTOR_ETFS = {
    "XLK":"Technology","XLF":"Financials","XLE":"Energy","XLV":"Healthcare",
    "XLI":"Industrials","XLY":"Consumer Discretionary","XLP":"Consumer Staples",
    "XLB":"Materials","XLRE":"Real Estate","XLU":"Utilities",
}

def render_comparison_section(metrics: list[dict], groq_api_key: str) -> None:
    if not metrics:
        return

    def section_hdr(title: str, grad: str = "linear-gradient(180deg,#6B2D6B,#C084C8)") -> str:
        return (f'<div style="font-family:\'Cormorant Garamond\',serif;font-size:1.15rem;'
                f'font-weight:300;color:#EDE8F5;margin:.9rem 0 .5rem;'
                f'display:flex;align-items:center;gap:.5rem;">'
                f'<span style="display:inline-block;width:3px;height:1rem;'
                f'background:{grad};border-radius:2px;"></span>{title}</div>')

    st.markdown(section_hdr("Document Margins vs Sector Benchmarks"), unsafe_allow_html=True)
    pct_m = {m["label"]: m["value"] for m in metrics if m["unit"] == "%"}
    sectors = ["S&P 500 Avg","Technology","Financials","Energy","Healthcare",
               "Industrials","Consumer Discretionary","Consumer Staples"]
    sector_sel = st.selectbox("Compare against sector", sectors, index=0, key="cmp_sector_inline")
    rows_html = ""
    for metric, doc_val in pct_m.items():
        bench_row = SECTOR_BENCHMARKS.get(metric, {})
        bench_val = bench_row.get(sector_sel)
        if bench_val is None: continue
        delta = doc_val - bench_val
        dstr  = f"+{delta:.1f}%" if delta >= 0 else f"{delta:.1f}%"
        dcls  = "td-pos" if delta > 1 else ("td-neg" if delta < -1 else "td-neu")
        rows_html += (f'<tr><td>{metric}</td>'
                      f'<td class="td-doc">{doc_val:.1f}%</td>'
                      f'<td class="td-mkt">{bench_val:.1f}%</td>'
                      f'<td class="{dcls}">{dstr}</td></tr>')
    if rows_html:
        st.markdown(
            f'<table class="cmp-table"><thead><tr>'
            f'<th>Metric</th><th>Your Document</th><th>{sector_sel} Benchmark</th><th>Delta</th>'
            f'</tr></thead><tbody>{rows_html}</tbody></table>',
            unsafe_allow_html=True,
        )
    else:
        st.info("No comparable margin metrics found in this document.")

# ─────────────────────────────────────────────────────────────────────────────
# INLINE ANALYTICS DASHBOARD (rendered below chat)
# ─────────────────────────────────────────────────────────────────────────────
def render_inline_analytics(vectorstore, groq_api_key, doc_full_text="", auto_metrics=None):
    """Renders analytics as an inline section below the chat panel."""
    st.markdown('<div class="analytics-panel">', unsafe_allow_html=True)
    st.markdown('<div class="analytics-panel-hdr">📊 Document Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="analytics-panel-sub">Finance-specific embeddings · Auto-extracted metrics · Market comparison</div>', unsafe_allow_html=True)

    sub_tabs = st.tabs(["📊 Metrics","📈 vs Market","📋 Templates","🔍 Hybrid Search","🧪 Eval"])

    with sub_tabs[0]:
        metrics = auto_metrics if auto_metrics else []
        if not metrics and doc_full_text:
            with st.spinner("Extracting metrics…"):
                metrics = extract_metrics(doc_full_text)
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:.54rem;letter-spacing:.18em;'
                    'text-transform:uppercase;color:#C084C8;margin-bottom:.8rem;">'
                    'Auto-Extracted Financial Metrics — FinBERT-Enhanced</div>', unsafe_allow_html=True)
        if metrics:
            render_metrics_dashboard(metrics)
            st.markdown("<hr style='border-color:rgba(139,58,139,.15);margin:1rem 0;'>", unsafe_allow_html=True)
            render_trend_chart(metrics)
            with st.expander("📄 Raw extraction table"):
                st.dataframe(pd.DataFrame([{"Metric":m["label"],"Value":fmt_val(m["value"],m["unit"]),
                                             "Unit":m["unit"],"Category":m["category"],"Raw Text":m["raw"]}
                                            for m in metrics]), use_container_width=True, hide_index=True)
        else:
            st.info("No metrics matched. Try Templates tab for LLM extraction.")

    with sub_tabs[1]:
        render_comparison_section(auto_metrics or [], groq_api_key)

    with sub_tabs[2]:
        cats = sorted({v["category"] for v in TEMPLATES.values()})
        chosen_cat = st.selectbox("Filter by category", ["All"]+cats, label_visibility="collapsed", key="tpl_cat_inline")
        visible = {k:v for k,v in TEMPLATES.items() if chosen_cat=="All" or v["category"]==chosen_cat}
        items = list(visible.items())
        for rs in range(0, len(items), 3):
            cols = st.columns(3)
            for ci, (tn, tm) in enumerate(items[rs:rs+3]):
                with cols[ci]:
                    color = CAT_COLORS.get(tm["category"], VELVET["dim"])
                    st.markdown(f'<div style="background:{VELVET["card2"]};border:1px solid rgba(139,58,139,.22);'
                                f'border-top:2px solid {color};border-radius:10px;padding:.8rem .9rem .6rem;">'
                                f'<div style="font-size:1.2rem;">{tm["icon"]}</div>'
                                f'<div style="font-family:Syne,sans-serif;font-size:.82rem;font-weight:600;'
                                f'color:{VELVET["text"]};margin:.3rem 0 .2rem;">{tn}</div>'
                                f'<div style="font-family:Space Mono,monospace;font-size:.52rem;color:{color};'
                                f'text-transform:uppercase;">{tm["category"]}</div></div>', unsafe_allow_html=True)
                    if st.button("Run Analysis →", key=f"tpl_inl_{tn[:20]}", use_container_width=True):
                        st.session_state["_prefill"] = tm["prompt"]
                        st.success(f"✓ '{tn}' sent to chat ↑")

    with sub_tabs[3]:
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:.54rem;letter-spacing:.18em;'
                    'text-transform:uppercase;color:#C084C8;margin-bottom:.8rem;">'
                    'Hybrid BM25 + Dense Retrieval (FinBERT embeddings)</div>', unsafe_allow_html=True)
        hs_q = st.text_input("Search", placeholder="e.g. free cash flow capital expenditure 2023",
                             label_visibility="collapsed", key="hs_inline")
        c1, c2 = st.columns(2)
        with c1: bw = st.slider("BM25 weight", 0.0, 1.0, 0.35, 0.05, key="bw_inline")
        with c2: tn = st.slider("Results", 3, 10, 5, key="tn_inline")
        tf = st.multiselect("Taxonomy filter", list(TAXONOMY.keys()), default=[], label_visibility="collapsed", key="tf_inline")
        if hs_q and vectorstore:
            with st.spinner("Retrieving…"):
                try:
                    vs = vectorstore
                    ar = vs["collection"].get(include=["documents","embeddings","metadatas"])
                    cks, emb, mts = ar["documents"], ar["embeddings"], ar["metadatas"]
                    if tf:
                        fi = [i for i,c in enumerate(cks) if any(t in tag_chunk(c) for t in tf)]
                        cks, emb, mts = [cks[i] for i in fi],[emb[i] for i in fi],[mts[i] for i in fi]
                    if not cks:
                        st.warning("No chunks match filter.")
                    else:
                        qe = vs["model"].encode([hs_q], normalize_embeddings=True).tolist()[0]
                        hits = HybridRetriever(cks, emb).retrieve(hs_q, qe, n=tn, bw=bw, rerank=False)
                        for rank, h in enumerate(hits, 1):
                            mt = mts[h["idx"]] if h["idx"] < len(mts) else {}
                            tags = tag_chunk(h["chunk"])
                            th = " ".join(f'<span style="background:rgba(139,58,139,.15);border:1px solid rgba(139,58,139,.3);'
                                          f'font-family:Space Mono,monospace;font-size:.5rem;padding:.1rem .35rem;'
                                          f'border-radius:3px;color:{CAT_COLORS.get(t,VELVET["dim"])};">{t}</span>'
                                          for t in tags)
                            st.markdown(f'<div style="background:{VELVET["card"]};border:1px solid rgba(139,58,139,.22);'
                                        f'border-left:3px solid #C084C8;border-radius:0 8px 8px 0;'
                                        f'padding:.7rem .9rem;margin-bottom:.5rem;">'
                                        f'<div style="display:flex;justify-content:space-between;margin-bottom:.35rem;">'
                                        f'<div style="font-family:Space Mono,monospace;font-size:.58rem;color:#C084C8;">'
                                        f'#{rank} · 📄 {mt.get("filename","—")}</div>'
                                        f'<div style="font-family:Space Mono,monospace;font-size:.52rem;color:#4A3858;">'
                                        f'score:{h["score"]:.3f}</div></div>'
                                        f'<div style="font-size:.8rem;color:#9A8AAA;line-height:1.55;">{h["chunk"][:320]}…</div>'
                                        f'<div style="margin-top:.4rem;display:flex;gap:.3rem;flex-wrap:wrap;">{th}</div></div>',
                                        unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Search error: {e}")
        elif hs_q:
            st.info("Upload and ingest documents first.")

    with sub_tabs[4]:
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:.54rem;letter-spacing:.18em;'
                    'text-transform:uppercase;color:#C084C8;margin-bottom:.8rem;">'
                    'FinanceBench-Style QA Accuracy Evaluation</div>', unsafe_allow_html=True)
        if st.button("▶  Run Benchmark", key="run_bench_inline"):
            if not vectorstore or not groq_api_key:
                st.error("Need documents and API key.")
            else:
                er = []; prog = st.progress(0, text="Evaluating…")
                for i, eq in enumerate(EVAL_QUESTIONS):
                    try:
                        from openai import OpenAI
                        oai = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
                        vs = vectorstore
                        qe = vs["model"].encode([eq["question"]], normalize_embeddings=True).tolist()
                        res = vs["collection"].query(query_embeddings=qe, n_results=4,
                                                     include=["documents","metadatas","distances"])
                        ctx = "\n---\n".join(res["documents"][0])
                        resp = oai.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role":"system","content":"Answer concisely using only the provided context."},
                                      {"role":"user","content":f"Context:\n{ctx}\n\nQuestion: {eq['question']}"}],
                            temperature=0.05, max_tokens=400)
                        ans = resp.choices[0].message.content; sc = score_answer(ans, eq["expected_keywords"])
                        er.append({"question":eq["question"],"category":eq["category"],"answer":ans,"score":sc})
                    except Exception as exc:
                        er.append({"question":eq["question"],"category":eq["category"],
                                   "answer":f"Error:{exc}","score":{"recall":0,"hits":0,"total":0,"score_pct":0}})
                    prog.progress((i+1)/len(EVAL_QUESTIONS), text=f"Q{i+1}/{len(EVAL_QUESTIONS)}")
                prog.empty(); render_eval_dashboard(er)

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# v8: SOURCE EVIDENCE PANEL + ANALYST MODE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

# ── Infer section title from chunk text ──────────────────────────────────────
_SECTION_PATTERNS = [
    (r"management.{0,10}discussion",        "Management Discussion & Analysis"),
    (r"risk factor",                        "Risk Factors"),
    (r"financial statement",                "Financial Statements"),
    (r"consolidated.{0,10}(balance sheet|statement)", "Consolidated Financial Statements"),
    (r"income statement|profit.{0,5}loss",  "Income Statement"),
    (r"cash flow",                          "Cash Flow Statement"),
    (r"balance sheet",                      "Balance Sheet"),
    (r"notes to.{0,10}financial",           "Notes to Financial Statements"),
    (r"earnings per share|eps",             "EPS & Per-Share Data"),
    (r"revenue recognition",                "Revenue Recognition Policy"),
    (r"segment.{0,8}(information|result)",  "Segment Information"),
    (r"forward.looking|outlook|guidance",   "Outlook & Guidance"),
    (r"dividend",                           "Dividends & Capital Return"),
    (r"executive compensation",             "Executive Compensation"),
    (r"audit.{0,10}report|independent auditor","Auditor's Report"),
    (r"liquidity|capital resource",         "Liquidity & Capital Resources"),
    (r"critical accounting",                "Critical Accounting Policies"),
    (r"goodwill|intangible asset",          "Goodwill & Intangibles"),
    (r"debt|borrowing|credit facilit",      "Debt & Financing"),
    (r"tax|income tax",                     "Tax & Deferred Items"),
]

def _infer_section(chunk_text: str) -> str:
    tl = chunk_text[:400].lower()
    for pat, name in _SECTION_PATTERNS:
        if re.search(pat, tl):
            return name
    return "Document Content"

def _infer_page(chunk_meta: dict, chunk_idx: int) -> str | None:
    """Estimate page from metadata if available, else from chunk index."""
    if chunk_meta.get("page"):
        return str(chunk_meta["page"])
    if chunk_meta.get("chunk") is not None:
        approx = (chunk_meta["chunk"] // 2) + 1
        return f"~{approx}"
    return None

def render_source_panel(sources_data: list[dict]) -> None:
    """
    Render the expandable evidence panel below an assistant answer.
    sources_data: list of {filename, score, preview, meta (optional), chunk_idx (optional)}
    """
    if not sources_data:
        return

    n = len(sources_data)
    # Build compact header HTML (not inside expander — we use st.expander for toggle)
    with st.expander(f"📂  View Sources  ({n} chunk{'s' if n!=1 else ''} retrieved)", expanded=False):
        st.markdown('<div class="src-evidence-wrap">', unsafe_allow_html=True)
        for idx, src in enumerate(sources_data, 1):
            score      = src.get("score", 0)
            filename   = src.get("filename", "—")
            preview    = src.get("preview", "")
            meta       = src.get("meta", {})
            chunk_idx  = src.get("chunk_idx")

            section    = _infer_section(preview)
            page_str   = _infer_page(meta, chunk_idx or idx)
            rel_pct    = int(score * 100)

            # Score badge class
            if rel_pct >= 75:   score_cls, score_icon = "score-hi", "●"
            elif rel_pct >= 50: score_cls, score_icon = "score-md", "●"
            else:               score_cls, score_icon = "score-lo", "●"

            page_badge    = f'<span class="src-badge page">pg {page_str}</span>' if page_str else ""
            section_badge = f'<span class="src-badge section">{section}</span>'
            score_badge   = f'<span class="src-badge {score_cls}">{score_icon} {rel_pct}% match</span>'

            # Truncated preview (full shown via CSS line-clamp, JS expand on click not needed with st)
            clean_preview = preview.replace("<","&lt;").replace(">","&gt;")

            st.markdown(f"""
<div class="src-chunk">
  <div class="src-chunk-head">
    <div class="src-chunk-file">
      <span style="opacity:.6;">#{idx}</span>
      📄 {_ht.escape(filename)}
    </div>
    <div class="src-chunk-meta">
      {page_badge}{section_badge}{score_badge}
    </div>
  </div>
  <div class="src-chunk-text">{clean_preview}…</div>
</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ── ANALYST MODE — structured financial extraction ──────────────────────────

# Regex patterns for structured extraction from LLM output
_ANA_EXTRACT = [
    # label, regex, unit
    ("Revenue",           r"(?:total\s+)?(?:net\s+)?revenue[^\n]{0,80}?([\$₹€£]?\s*[\d,\.]+\s*(?:billion|million|B|M|Cr|T)?)", "figure"),
    ("Net Income",        r"net\s+income[^\n]{0,80}?([\$₹€£]?\s*[\d,\.]+\s*(?:billion|million|B|M|Cr|T)?)",                    "figure"),
    ("Gross Profit",      r"gross\s+profit[^\n]{0,80}?([\$₹€£]?\s*[\d,\.]+\s*(?:billion|million|B|M|Cr|T)?)",                  "figure"),
    ("EBITDA",            r"ebitda[^\n]{0,80}?([\$₹€£]?\s*[\d,\.]+\s*(?:billion|million|B|M|Cr|T)?)",                         "figure"),
    ("Free Cash Flow",    r"free\s+cash\s+flow[^\n]{0,80}?([\$₹€£]?\s*[\d,\.]+\s*(?:billion|million|B|M|Cr|T)?)",             "figure"),
    ("EPS (Diluted)",     r"diluted\s+(?:eps|earnings)[^\n]{0,80}?([\$₹€£]?\s*[\d,\.]+)",                                       "figure"),
    ("Revenue Growth",    r"revenue\s+(?:growth|increased?|grew)[^\n]{0,80}?([\d\.]+\s*%)",                                      "pct"),
    ("Gross Margin",      r"gross\s+margin[^\n]{0,80}?([\d\.]+\s*%)",                                                            "pct"),
    ("Operating Margin",  r"operating\s+margin[^\n]{0,80}?([\d\.]+\s*%)",                                                        "pct"),
    ("Net Margin",        r"net\s+(?:profit\s+)?margin[^\n]{0,80}?([\d\.]+\s*%)",                                                "pct"),
    ("ROE",               r"return\s+on\s+equity[^\n]{0,80}?([\d\.]+\s*%)",                                                      "pct"),
    ("Debt/Equity",       r"debt[- ]to[- ]equity[^\n]{0,80}?([\d\.]+)",                                                          "ratio"),
    ("Guidance",          r"(?:guidance|outlook|forecast)[^\n]{0,200}",                                                           "text"),
]

def _extract_analyst_data(text: str) -> dict:
    """Pull structured fields from the LLM's analyst response."""
    tl = text.lower(); out = {}
    for label, pattern, kind in _ANA_EXTRACT:
        m = re.search(pattern, tl, re.IGNORECASE)
        if m:
            val = m.group(1).strip() if m.lastindex and m.lastindex >= 1 else m.group(0).strip()
            out[label] = {"value": val.replace(",","").strip(), "kind": kind}
    # Extract risk lines — look for bullet-style risk mentions
    risks = re.findall(r"(?:risk|risk factor)[^\n\.]{0,220}", text, re.IGNORECASE)
    out["_risks"] = [r.strip() for r in risks[:4]]
    # Verdict/recommendation line
    verdict_m = re.search(
        r"(?:overall|recommendation|verdict|conclusion|summary)[^\n\.]{0,300}", text, re.IGNORECASE)
    out["_verdict"] = verdict_m.group(0).strip() if verdict_m else ""
    return out

def _val_class(val_str: str) -> str:
    """Return CSS class based on whether value looks positive/negative."""
    s = val_str.lower()
    if any(k in s for k in ["increased","grew","up","positive","strong","above"]):   return "pos"
    if any(k in s for k in ["decreased","fell","down","negative","weak","below"]):   return "neg"
    if "%" in s:
        nums = re.findall(r"-?\d+\.?\d*", s)
        if nums:
            v = float(nums[0])
            return "pos" if v > 0 else ("neg" if v < 0 else "neu")
    return "neu"

def render_analyst_output(raw_answer: str, question: str) -> None:
    """Render answer in structured analyst card format."""
    data = _extract_analyst_data(raw_answer)

    # Separate figure/pct metrics from text/special
    figure_metrics = {k:v for k,v in data.items()
                      if not k.startswith("_") and v["kind"] in ("figure","pct","ratio")}
    risks          = data.get("_risks", [])
    verdict        = data.get("_verdict", "")

    st.markdown(f"""
<div class="analyst-card">
  <div class="analyst-card-hdr">
    <div class="analyst-card-title">Analyst Report</div>
    <span class="analyst-mode-badge">⚡ Analyst Mode</span>
  </div>""", unsafe_allow_html=True)

    # ── Metric grid ─────────────────────────────────────────────────────────
    if figure_metrics:
        items = list(figure_metrics.items())
        for i in range(0, len(items), 2):
            pair = items[i:i+2]
            row_html = '<div class="analyst-row">'
            for label, meta in pair:
                v    = meta["value"]
                vcls = _val_class(v)
                row_html += (f'<div class="analyst-metric">'
                             f'<div class="am-label">{label}</div>'
                             f'<div class="am-value {vcls}">{v if v else "—"}</div>'
                             f'</div>')
            if len(pair) == 1:  # pad odd row
                row_html += '<div class="analyst-metric" style="opacity:.3"><div class="am-label">—</div><div class="am-value">—</div></div>'
            row_html += "</div>"
            st.markdown(row_html, unsafe_allow_html=True)

    # ── Raw answer as prose (collapsible) ───────────────────────────────────
    with st.expander("📝 Full Analyst Narrative", expanded=not bool(figure_metrics)):
        st.markdown(f'<div style="font-size:.83rem;color:#9A8AAA;line-height:1.8;">{raw_answer}</div>',
                    unsafe_allow_html=True)

    # ── Key Risks ────────────────────────────────────────────────────────────
    if risks:
        st.markdown('<div class="analyst-section">'
                    '<div class="analyst-section-title">Key Risk Highlights</div>',
                    unsafe_allow_html=True)
        for r in risks:
            r_clean = re.sub(r"^(risk factor[s]?[\s:–-]*)", "", r, flags=re.IGNORECASE).strip()
            if r_clean:
                st.markdown(f'<div class="analyst-risk-item">'
                            f'<div class="analyst-risk-bullet"></div>'
                            f'<span>{_ht.escape(r_clean[:220])}</span></div>',
                            unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Verdict ─────────────────────────────────────────────────────────────
    if verdict:
        st.markdown(f'<div class="analyst-verdict">'
                    f'<div class="av-icon">📌</div>'
                    f'<div class="av-text"><strong>Summary:</strong> {_ht.escape(verdict[:380])}</div>'
                    f'</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # close analyst-card


# ─────────────────────────────────────────────────────────────────────────────
# DATA FETCH HELPERS
# ─────────────────────────────────────────────────────────────────────────────
_HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

class _TokenBucket:
    def __init__(self, capacity=30, refill_every=60.0):
        self._cap=capacity; self._tokens=float(capacity)
        self._interval=refill_every/capacity; self._lock=_th.Lock(); self._last=_tm.monotonic()
    def acquire(self, timeout=5.0):
        deadline=_tm.monotonic()+timeout
        while True:
            with self._lock:
                now=_tm.monotonic(); earned=(now-self._last)/self._interval
                self._tokens=min(self._cap,self._tokens+earned); self._last=now
                if self._tokens>=1.0: self._tokens-=1.0; return True
            if _tm.monotonic()>=deadline: return False
            _tm.sleep(0.05)

@st.cache_resource
def _get_bucket(): return _TokenBucket(capacity=30, refill_every=60.0)

def _throttled_get(url, timeout=10):
    if not _get_bucket().acquire(timeout=4.0):
        raise RuntimeError("Rate limit reached — wait a few seconds.")
    return requests.get(url, headers=_HEADERS, timeout=timeout)

@st.cache_data(ttl=300)
def fetch_yahoo_series(symbol, period, interval):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={period}&interval={interval}&includePrePost=false"
    try:
        r = _throttled_get(url, timeout=10); r.raise_for_status()
        data = r.json(); res = data["chart"]["result"][0]
        ts = res["timestamp"]; close = res["indicators"]["quote"][0]["close"]
        idx = pd.to_datetime(ts, unit="s", utc=True).tz_convert("US/Eastern")
        return pd.Series(close, index=idx, name=symbol).dropna()
    except: return None

@st.cache_data(ttl=60)
def fetch_quote(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=2d&interval=1d"
    try:
        r = _throttled_get(url, timeout=8); r.raise_for_status()
        data = r.json()
        q = [x for x in data["chart"]["result"][0]["indicators"]["quote"][0]["close"] if x is not None]
        if not q: return None
        return {"price":q[-1],"pct":(q[-1]-q[-2])/q[-2]*100 if len(q)>=2 else 0.0}
    except: return None

@st.cache_data(ttl=60)
def fetch_multi_quotes(symbols): return {s:i for s in symbols if (i:=fetch_quote(s))}

@st.cache_data(ttl=300)
def fetch_fear_greed():
    try:
        r = _throttled_get("https://api.alternative.me/fng/?limit=1", timeout=8)
        d = r.json()["data"][0]
        return {"value":int(d["value"]),"label":d["value_classification"]}
    except: return {"value":50,"label":"Neutral"}

@st.cache_data(ttl=600)
def fetch_rss_with_images(feed_url, source_name, accent, max_items=8):
    FALLBACK = {"Bloomberg":"https://assets.bbhub.io/company/sites/51/2019/08/BBG-Logo-Black.png",
                "Wall Street Journal":"https://s.wsj.net/media/wsj_logo_black_sm.png",
                "Financial Times":"https://about.ft.com/files/2020/04/ft_logo.png",
                "Reuters":"https://www.reuters.com/pf/resources/images/reuters/logo-vertical-default.png",
                "CNBC":"https://www.cnbc.com/2020/07/21/cnbc-social-card-2019.jpg"}
    import html as _h
    try:
        r = requests.get(feed_url, headers={**_HEADERS,"Accept":"application/rss+xml,*/*"}, timeout=10)
        r.raise_for_status(); text = r.text
    except: return []
    results = []
    items = re.findall(r"<item[^>]*>(.*?)</item>", text, re.DOTALL) or \
            re.findall(r"<entry[^>]*>(.*?)</entry>", text, re.DOTALL)
    for item in items[:max_items]:
        tm = re.search(r"<title[^>]*>(.*?)</title>", item, re.DOTALL|re.IGNORECASE)
        raw = tm.group(1).strip() if tm else ""
        cdata = re.match(r"<!\[CDATA\[(.*?)\]\]>", raw, re.DOTALL)
        title = cdata.group(1).strip() if cdata else raw
        title = _h.unescape(re.sub(r"<[^>]+>", "", title)).strip()
        if not title or len(title) < 10: continue
        lm = (re.search(r'<link[^>]*href=["\'](https?://[^"\'> ]+)["\']', item, re.IGNORECASE) or
              re.search(r"<link>(.*?)</link>", item, re.DOTALL|re.IGNORECASE))
        link = (lm.group(1) or "#").strip() if lm else "#"
        if not link.startswith("http"): link = "#"
        img = ""
        mm = re.search(r'<media:(?:content|thumbnail)[^>]+url=["\'](https?://[^"\']+)["\']', item, re.IGNORECASE)
        if mm: img = mm.group(1)
        if not img:
            em = re.search(r'<enclosure[^>]+url=["\'](https?://[^"\']+(?:jpg|jpeg|png|webp))["\']', item, re.IGNORECASE)
            if em: img = em.group(1)
        if not img: img = FALLBACK.get(source_name, "")
        results.append({"title":title,"link":link,"source":source_name,"accent":accent,"img_url":img})
    return results

@st.cache_data(ttl=600)
def fetch_gnews_with_images(query, source_label, accent, max_items=6):
    import urllib.parse
    return fetch_rss_with_images(
        f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en",
        source_label, accent, max_items)

def make_chip_html(sym, name, price, pct, prefix="$", suffix="", decimals=2, icon=""):
    arrow  = "▲" if pct > 0.005 else ("▼" if pct < -0.005 else "●")
    cls    = "up" if pct > 0.005 else ("down" if pct < -0.005 else "flat")
    chip_c = "chip-up" if pct > 0.005 else ("chip-down" if pct < -0.005 else "chip-flat")
    ih     = f'<span style="font-size:1rem;margin-right:.2rem;">{icon}</span>' if icon else ""
    return (f'<div class="price-chip {chip_c}"><div class="pc-sym">{ih}{sym}</div>'
            f'<div class="pc-name">{name}</div>'
            f'<div class="pc-val">{prefix}{price:,.{decimals}f}{suffix}</div>'
            f'<div class="pc-chg {cls}">{arrow} {abs(pct):.2f}%</div></div>')

@st.cache_data(ttl=600)
def get_all_news():
    news = []
    for url, src, color in [("https://feeds.bloomberg.com/markets/news.rss","Bloomberg","#4ADE80"),
                             ("https://feeds.a.dj.com/rss/RSSMarketsMain.xml","Wall Street Journal","#F0C040"),
                             ("https://www.ft.com/?format=rss","Financial Times","#FB923C"),
                             ("https://www.cnbc.com/id/100003114/device/rss/rss.html","CNBC","#C084C8"),
                             ("https://feeds.reuters.com/reuters/businessNews","Reuters","#60A5FA")]:
        news.extend(fetch_rss_with_images(url, src, color, max_items=4))
    if len(news) < 6:
        news.extend(fetch_gnews_with_images("financial markets economy","Google News","#9CA3AF",8))
    return news[:16]

@st.cache_data(ttl=600)
def get_policy_news():
    policy = []
    for url, src, flag, color in [("https://www.federalreserve.gov/feeds/press_all.xml","Federal Reserve","🇺🇸","#60A5FA"),
                                   ("https://www.ecb.europa.eu/rss/press.html","ECB","🇪🇺","#34D399"),
                                   ("https://www.imf.org/en/News/rss?language=eng","IMF","🌐","#A78BFA"),
                                   ("https://www.rbi.org.in/scripts/rss.aspx","RBI India","🇮🇳","#FB923C"),
                                   ("https://www.bankofengland.co.uk/rss/publications","Bank of England","🇬🇧","#F472B6")]:
        items = fetch_rss_with_images(url, src, color, max_items=3)
        for item in items: item["flag"]=flag; item["policy"]=True
        policy.extend(items)
    if len(policy) < 4:
        extra = fetch_gnews_with_images("central bank monetary policy rate decision","Policy News","#A78BFA",6)
        for item in extra: item["flag"]="🏦"; item["policy"]=True
        policy.extend(extra)
    return policy[:12]

def build_carousel_html(items, is_policy=False, height_px=380):
    ag  = "linear-gradient(90deg,#3B82F6,#A78BFA)" if is_policy else "linear-gradient(90deg,#6B2D6B,#C084C8)"
    tt  = "Policy &amp; Government Decisions" if is_policy else "Financial Headlines"
    tbc = "#3B82F6" if is_policy else "#C084C8"
    bgc = "#0A0F1E" if is_policy else "#120E1A"
    bc  = "rgba(59,130,246,.3)" if is_policy else "rgba(139,58,139,.3)"
    slides_js = json.dumps([{"title":i["title"],"link":i.get("link","#"),"source":i.get("source",""),
                              "accent":i.get("accent","#C084C8"),"img":i.get("img_url",""),
                              "flag":i.get("flag",""),"policy":i.get("policy",False)} for i in items])
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0D0B12;font-family:'Segoe UI',system-ui,sans-serif;color:#EDE8F5;height:{height_px}px;overflow:hidden}}
.cw{{background:#0D0B12;border:1px solid {bc};border-radius:14px;height:{height_px}px;
  display:flex;flex-direction:column;overflow:hidden;position:relative}}
.cw::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:{ag}}}
.ch{{display:flex;align-items:center;justify-content:space-between;
  padding:.85rem 1.1rem .6rem;flex-shrink:0;border-bottom:1px solid rgba(139,58,139,.12)}}
.ct{{font-family:Georgia,serif;font-size:1rem;font-weight:300;color:#EDE8F5;
  display:flex;align-items:center;gap:.5rem}}
.ct::before{{content:'';display:inline-block;width:3px;height:1rem;background:{ag};border-radius:2px}}
.cn{{display:flex;align-items:center;gap:.4rem}}
.nb{{background:rgba(107,45,107,.15);border:1px solid {bc};color:{tbc};width:26px;height:26px;
  border-radius:50%;cursor:pointer;font-size:1rem;display:flex;align-items:center;justify-content:center;
  transition:background .2s}}
.nb:hover{{background:rgba(107,45,107,.35)}}
.dots{{display:flex;gap:4px;align-items:center;flex-wrap:wrap;max-width:160px}}
.dot{{width:6px;height:6px;border-radius:50%;background:rgba(139,58,139,.3);
  border:1px solid rgba(139,58,139,.4);cursor:pointer;transition:all .2s}}
.dot.active{{background:{tbc};transform:scale(1.3)}}
.sa{{flex:1;position:relative;overflow:hidden}}
.sl{{position:absolute;top:0;left:0;right:0;bottom:0;display:flex;flex-direction:column;
  opacity:0;transform:translateX(40px);transition:opacity .45s,transform .45s;pointer-events:none}}
.sl.active{{opacity:1;transform:translateX(0);pointer-events:all}}
.sl.leaving{{opacity:0;transform:translateX(-40px)}}
.si{{width:100%;height:160px;object-fit:cover;flex-shrink:0;background:#120E1A}}
.ip{{width:100%;height:160px;flex-shrink:0;display:flex;align-items:center;justify-content:center;
  font-size:2.5rem;background:linear-gradient(135deg,#120E1A 0%,#1a1028 100%);
  border-bottom:1px solid rgba(139,58,139,.15)}}
.sb{{padding:.7rem 1rem .5rem;display:flex;flex-direction:column;gap:.3rem;flex:1;background:{bgc}}}
.ss{{font-family:'Courier New',monospace;font-size:.58rem;letter-spacing:.14em;text-transform:uppercase;
  display:flex;align-items:center;gap:.4rem;flex-wrap:wrap}}
.pb2{{font-size:.45rem;background:rgba(59,130,246,.15);border:1px solid rgba(59,130,246,.3);
  color:#93C5FD;padding:.05rem .35rem;border-radius:3px}}
.st{{font-size:.9rem;font-weight:500;color:#EDE8F5;line-height:1.45;text-decoration:none;
  display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
.st:hover{{color:{tbc};text-decoration:underline}}
.sm{{font-family:'Courier New',monospace;font-size:.48rem;color:#4A3858;margin-top:auto}}
.pbw{{flex-shrink:0;height:2px;background:rgba(139,58,139,.12);overflow:hidden}}
.pb{{height:100%;width:0%;background:{ag};border-radius:1px;transition:width 3s linear}}
.cf{{display:flex;justify-content:space-between;align-items:center;
  padding:.3rem 1rem;flex-shrink:0;background:rgba(0,0,0,.3)}}
.fl{{font-family:'Courier New',monospace;font-size:.44rem;color:#4A3858}}
.fc{{font-family:'Courier New',monospace;font-size:.48rem;color:#4A3858}}
</style></head><body>
<div class="cw" id="car">
  <div class="ch"><div class="ct">{tt}</div>
    <div class="cn"><div class="dots" id="dots"></div>
      <button class="nb" id="prev">&#8249;</button>
      <button class="nb" id="next">&#8250;</button>
    </div>
  </div>
  <div class="sa" id="slides"></div>
  <div class="pbw"><div class="pb" id="pb"></div></div>
  <div class="cf"><div class="fl">&#9679; live &middot; 10min cache</div>
    <div class="fc" id="ctr">1/1</div></div>
</div>
<script>
(function(){{
var S={slides_js},N=S.length,cur=0,paused=false,timer=null,pbt=null;
var se=document.getElementById('slides'),de=document.getElementById('dots'),
    ce=document.getElementById('ctr'),pb=document.getElementById('pb');
S.forEach(function(s,i){{
  var sd=document.createElement('div');sd.className='sl'+(i===0?' active':'');sd.id='sl'+i;
  var img=s.img?'<img class="si" src="'+s.img+'" alt="" onerror="this.style.display=\\'none\\';this.nextElementSibling.style.display=\\'flex\\';"><div class="ip" style="display:none">📰</div>':'<div class="ip">📰</div>';
  var src=s.policy?'<span style="color:'+s.accent+'">'+s.flag+' '+s.source+'</span><span class="pb2">Policy</span>':'<span style="color:'+s.accent+'">'+s.source+'</span>';
  sd.innerHTML=img+'<div class="sb"><div class="ss">'+src+'</div><a class="st" href="'+s.link+'" target="_blank">'+s.title+'</a><div class="sm">&#128336; 3s auto-advance</div></div>';
  se.appendChild(sd);
  var dot=document.createElement('span');dot.className='dot'+(i===0?' active':'');dot.id='dot'+i;
  dot.onclick=(function(idx){{return function(){{goTo(idx)}}}})(i);de.appendChild(dot);
}});
function startPB(){{clearTimeout(pbt);pb.style.transition='none';pb.style.width='0%';
  pbt=setTimeout(function(){{pb.style.transition='width 3s linear';pb.style.width='100%'}},40);}}
function goTo(n){{
  var p=cur;cur=((n%N)+N)%N;if(p===cur)return;
  var oe=document.getElementById('sl'+p),ne=document.getElementById('sl'+cur),
      od=document.getElementById('dot'+p),nd=document.getElementById('dot'+cur);
  if(oe){{oe.className='sl leaving';setTimeout(function(){{if(oe)oe.className='sl'}},450);}}
  if(ne)ne.className='sl active';if(od)od.className='dot';if(nd)nd.className='dot active';
  ce.textContent=(cur+1)+'/'+N;startPB();
}}
document.getElementById('next').onclick=function(){{goTo(cur+1);restart();}};
document.getElementById('prev').onclick=function(){{goTo(cur-1);restart();}};
function restart(){{clearInterval(timer);timer=setInterval(function(){{if(!paused)goTo(cur+1);}},3000);}}
document.getElementById('car').addEventListener('mouseenter',function(){{paused=true;}});
document.getElementById('car').addEventListener('mouseleave',function(){{paused=false;}});
ce.textContent='1/'+N;startPB();restart();
}})();
</script></body></html>"""

# ─────────────────────────────────────────────────────────────────────────────
# ② UNIVERSAL FILE TEXT EXTRACTOR
# ─────────────────────────────────────────────────────────────────────────────
def extract_text_from_file(f) -> str:
    name = f.name.lower()
    raw  = f.read()

    if name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(raw))
        return " ".join(pg.extract_text() or "" for pg in reader.pages)

    if name.endswith((".xlsx", ".xls")):
        try:
            dfs = pd.read_excel(io.BytesIO(raw), sheet_name=None, dtype=str)
            parts = []
            for sheet, df in dfs.items():
                parts.append(f"=== Sheet: {sheet} ===")
                parts.append(df.fillna("").to_string(index=False))
            return "\n".join(parts)
        except Exception as e:
            return f"[Excel parse error: {e}]"

    if name.endswith(".csv"):
        try:
            df = pd.read_csv(io.BytesIO(raw), dtype=str)
            return df.fillna("").to_string(index=False)
        except Exception as e:
            return f"[CSV parse error: {e}]"

    if name.endswith(".docx"):
        try:
            import zipfile, xml.etree.ElementTree as ET
            z   = zipfile.ZipFile(io.BytesIO(raw))
            xml_content = z.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
            paras = []
            for para in tree.iter(f"{W}p"):
                texts = [t.text or "" for t in para.iter(f"{W}t")]
                line  = "".join(texts).strip()
                if line: paras.append(line)
            return "\n".join(paras)
        except Exception as e:
            return f"[DOCX parse error: {e}]"

    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return raw.decode(enc)
        except: pass
    return raw.decode("utf-8", errors="ignore")

# ─────────────────────────────────────────────────────────────────────────────
# ④ FINANCE-SPECIFIC EMBEDDING MODEL (FinBERT)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_embedding_model():
    """
    Load finance-specific embedding model.
    Uses yiyanghkust/finbert-pretrain — trained on financial corpora
    (SEC filings, earnings reports, financial news).
    Falls back to all-MiniLM-L6-v2 if FinBERT unavailable.
    """
    from sentence_transformers import SentenceTransformer
    try:
        # FinBERT — finance-aware embeddings
        model = SentenceTransformer("yiyanghkust/finbert-pretrain")
        st.session_state["_embed_model_name"] = "FinBERT (yiyanghkust/finbert-pretrain)"
        return model
    except Exception:
        # Fallback to general model
        model = SentenceTransformer("all-MiniLM-L6-v2")
        st.session_state["_embed_model_name"] = "all-MiniLM-L6-v2 (fallback)"
        return model

# ─────────────────────────────────────────────────────────────────────────────
# INGEST — multi-format + finance embeddings + auto analytics
# ─────────────────────────────────────────────────────────────────────────────
def ingest_documents(files):
    from chromadb import EphemeralClient
    from chromadb.config import Settings
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    model  = load_embedding_model()  # ← Finance-specific FinBERT model
    client = EphemeralClient(settings=Settings(anonymized_telemetry=False))
    try:   client.delete_collection("financials")
    except: pass
    col = client.create_collection("financials", metadata={"hnsw:space":"cosine"})

    all_chunks, all_ids, all_meta, fnames, full_texts = [], [], [], [], []
    prog = st.progress(0, text="Reading files…")

    for i, f in enumerate(files):
        text   = extract_text_from_file(f)
        chunks = splitter.split_text(text)
        fnames.append(f.name)
        full_texts.append(text)
        for j, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(f"{f.name}_chunk_{j}")
            all_meta.append({"filename":f.name,"chunk":j})
        prog.progress((i+1)/len(files), text=f"Processed {f.name}")
    prog.empty()

    if all_chunks:
        with st.spinner(f"Embedding {len(all_chunks)} chunks with FinBERT (finance-specific)…"):
            embs = model.encode(all_chunks, normalize_embeddings=True).tolist()
            col.add(documents=all_chunks, embeddings=embs, ids=all_ids, metadatas=all_meta)

    combined_text = " ".join(full_texts)

    with st.spinner("Auto-generating analytics…"):
        auto_metrics = extract_metrics(combined_text)

    st.session_state.vectorstore    = {"collection":col,"model":model}
    st.session_state.uploaded_docs  = len(files)
    st.session_state.chunk_count    = len(all_chunks)
    st.session_state.file_names     = fnames
    st.session_state.doc_full_text  = combined_text
    st.session_state.auto_metrics   = auto_metrics
    st.session_state.auto_generated = True
    st.session_state.show_analytics = True  # ← auto-show analytics panel

    return len(all_chunks)

# ─────────────────────────────────────────────────────────────────────────────
# INDIA NEWS RSS
# ─────────────────────────────────────────────────────────────────────────────
NEWS_SOURCES = {
    "📰 Business Standard":  {"rss":"https://www.business-standard.com/rss/home_page_top_stories.rss","tag":"Markets"},
    "📰 Economic Times":     {"rss":"https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms","tag":"Markets"},
    "📰 Mint":               {"rss":"https://www.livemint.com/rss/markets","tag":"Markets"},
    "📰 Hindu BusinessLine": {"rss":"https://www.thehindubusinessline.com/markets/feeder/default.rss","tag":"Markets"},
    "🏛️ RBI Notifications":  {"rss":"https://www.rbi.org.in/Scripts/Notifications_Rss.aspx","tag":"Policy"},
    "🏛️ SEBI Orders":        {"rss":"https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doGetPublicationRss=yes&rssHead=4","tag":"Policy"},
    "🏛️ Finance Ministry":   {"rss":"https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3","tag":"Policy"},
    "🏛️ PIB – Economy":      {"rss":"https://pib.gov.in/RssMain.aspx?ModId=4&Lang=1&Regid=3","tag":"Policy"},
}

@st.cache_data(ttl=600)
def fetch_rss(url, max_items=6):
    import xml.etree.ElementTree as ET
    headers = {"User-Agent":"Mozilla/5.0 (compatible; NewsBot/1.0)","Accept":"application/rss+xml,*/*"}
    try:
        r = requests.get(url, headers=headers, timeout=12); r.raise_for_status()
        root = ET.fromstring(r.content)
        items = root.findall(".//item"); results = []
        for item in items[:max_items]:
            title = (item.findtext("title") or "").strip()
            link  = (item.findtext("link")  or "").strip()
            pub   = (item.findtext("pubDate") or "").strip()
            desc  = re.sub(r"<[^>]+>", "", (item.findtext("description") or ""))[:180].strip()
            try:
                from email.utils import parsedate_to_datetime
                pub = parsedate_to_datetime(pub).strftime("%d %b, %H:%M")
            except: pub = pub[:16]
            if title: results.append({"title":title,"link":link,"date":pub,"summary":desc})
        return results
    except: return []

# ─────────────────────────────────────────────────────────────────────────────
# MARKET SYMBOL DICTS
# ─────────────────────────────────────────────────────────────────────────────
COMMODITY_SYMS = {
    "GC=F":("Gold","$/oz","🪙",2),"SI=F":("Silver","$/oz","⚪",3),
    "CL=F":("Crude Oil","$/bbl","🛢️",2),"PL=F":("Platinum","$/oz","💎",2),
    "PA=F":("Palladium","$/oz","✨",2),"HG=F":("Copper","$/lb","🟤",3),
}
CRYPTO_SYMS = {
    "BTC-USD":("Bitcoin","BTC","₿",2),"ETH-USD":("Ethereum","ETH","Ξ",2),
    "BNB-USD":("BNB","BNB","🔶",2),"SOL-USD":("Solana","SOL","◎",2),
    "XRP-USD":("XRP","XRP","✕",4),"DOGE-USD":("Dogecoin","DOGE","🐕",5),
    "ADA-USD":("Cardano","ADA","🔵",4),"AVAX-USD":("Avalanche","AVAX","🔺",2),
}
ALL_FX = {
    "USDINR=X":{"label":"USD/INR","flag":"🇮🇳","name":"Indian Rupee","invert":False},
    "USDJPY=X":{"label":"USD/JPY","flag":"🇯🇵","name":"Japanese Yen","invert":False},
    "USDCNY=X":{"label":"USD/CNY","flag":"🇨🇳","name":"Chinese Yuan","invert":False},
    "EURUSD=X":{"label":"EUR/USD","flag":"🇪🇺","name":"Euro","invert":True},
    "GBPUSD=X":{"label":"GBP/USD","flag":"🇬🇧","name":"British Pound","invert":True},
    "USDCHF=X":{"label":"USD/CHF","flag":"🇨🇭","name":"Swiss Franc","invert":False},
    "USDKRW=X":{"label":"USD/KRW","flag":"🇰🇷","name":"S. Korean Won","invert":False},
    "USDBRL=X":{"label":"USD/BRL","flag":"🇧🇷","name":"Brazilian Real","invert":False},
    "USDCAD=X":{"label":"USD/CAD","flag":"🇨🇦","name":"Canadian Dollar","invert":False},
    "USDAUD=X":{"label":"USD/AUD","flag":"🇦🇺","name":"Australian Dollar","invert":False},
    "USDSGD=X":{"label":"USD/SGD","flag":"🇸🇬","name":"Singapore Dollar","invert":False},
    "USDHKD=X":{"label":"USD/HKD","flag":"🇭🇰","name":"Hong Kong Dollar","invert":False},
    "USDMXN=X":{"label":"USD/MXN","flag":"🇲🇽","name":"Mexican Peso","invert":False},
    "USDTRY=X":{"label":"USD/TRY","flag":"🇹🇷","name":"Turkish Lira","invert":False},
    "USDRUB=X":{"label":"USD/RUB","flag":"🇷🇺","name":"Russian Ruble","invert":False},
    "USDZAR=X":{"label":"USD/ZAR","flag":"🇿🇦","name":"S. African Rand","invert":False},
    "USDAED=X":{"label":"USD/AED","flag":"🇦🇪","name":"UAE Dirham","invert":False},
    "USDNOK=X":{"label":"USD/NOK","flag":"🇳🇴","name":"Norwegian Krone","invert":False},
    "USDSEK=X":{"label":"USD/SEK","flag":"🇸🇪","name":"Swedish Krona","invert":False},
    "USDDKK=X":{"label":"USD/DKK","flag":"🇩🇰","name":"Danish Krone","invert":False},
    "USDNZD=X":{"label":"USD/NZD","flag":"🇳🇿","name":"New Zealand Dollar","invert":False},
    "USDPLN=X":{"label":"USD/PLN","flag":"🇵🇱","name":"Polish Zloty","invert":False},
    "USDTHB=X":{"label":"USD/THB","flag":"🇹🇭","name":"Thai Baht","invert":False},
    "USDIDR=X":{"label":"USD/IDR","flag":"🇮🇩","name":"Indonesian Rupiah","invert":False},
    "USDPHP=X":{"label":"USD/PHP","flag":"🇵🇭","name":"Philippine Peso","invert":False},
}

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0 0 1rem;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.4rem;font-weight:300;
                  color:#EDE8F5;line-height:1.1;">
        RAG <em style="color:#C084C8;font-style:italic;">Assistant</em>
      </div>
      <div style="font-family:'Space Mono',monospace;font-size:.52rem;letter-spacing:.22em;
                  color:#4A3858;text-transform:uppercase;margin-top:.35rem;">
        Financial Intelligence · v11
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-lbl" style="border-top:none;padding-top:0;margin-top:0;">Configuration</div>',
                unsafe_allow_html=True)
    default_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY",""))
    if default_key:
        GROQ_API_KEY = default_key
        st.markdown('<div class="key-ok"><div class="key-dot"></div>API Key Active</div>',
                    unsafe_allow_html=True)
    else:
        GROQ_API_KEY = st.text_input("", type="password", placeholder="gsk_…",
                                     label_visibility="collapsed")
        st.markdown("<span style='font-family:Space Mono,monospace;font-size:.56rem;color:#4A3858;'>"
                    "console.groq.com → free key</span>", unsafe_allow_html=True)
        if GROQ_API_KEY:
            os.environ["GROQ_API_KEY"] = GROQ_API_KEY
            st.markdown('<div class="key-ok"><div class="key-dot"></div>API Key Active</div>',
                        unsafe_allow_html=True)

    # Embedding model status
    embed_name = st.session_state.get("_embed_model_name", "FinBERT (loads on first ingest)")
    is_finbert = "finbert" in embed_name.lower()
    emb_color = "#4ade80" if is_finbert else "#f0c040"
    emb_icon  = "🧠" if is_finbert else "⚡"
    st.markdown(f'<div style="margin:.6rem 0 .3rem;background:rgba(74,222,128,.05);'
                f'border:1px solid rgba(74,222,128,.15);border-radius:6px;padding:.5rem .7rem;">'
                f'<div style="font-family:Space Mono,monospace;font-size:.5rem;letter-spacing:.15em;'
                f'text-transform:uppercase;color:#4A3858;margin-bottom:.2rem;">Embedding Model</div>'
                f'<div style="font-family:Space Mono,monospace;font-size:.55rem;color:{emb_color};">'
                f'{emb_icon} {embed_name}</div></div>', unsafe_allow_html=True)

    bucket = _get_bucket(); tl = int(bucket._tokens); pf = tl / bucket._cap
    bc = "#4ade80" if pf > 0.5 else ("#f0c040" if pf > 0.2 else "#f87171")
    st.markdown(f'<div style="margin:.6rem 0 .3rem;">'
                f'<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.2em;'
                f'color:#4A3858;text-transform:uppercase;margin-bottom:.3rem;">API Rate Limit</div>'
                f'<div style="background:#0D0B12;border:1px solid rgba(139,58,139,.22);'
                f'border-radius:4px;height:5px;overflow:hidden;">'
                f'<div style="height:100%;width:{int(pf*100)}%;background:{bc};border-radius:4px;'
                f'transition:width .4s;"></div></div>'
                f'<div style="font-family:Space Mono,monospace;font-size:.5rem;color:#4A3858;margin-top:.2rem;">'
                f'{tl}/{bucket._cap} calls · 60s reset</div></div>',
                unsafe_allow_html=True)

    if st.session_state.file_names:
        st.markdown('<div class="sb-lbl">Knowledge Base</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Chunks", st.session_state.chunk_count)
        c2.metric("Docs",   st.session_state.uploaded_docs)
        dot_colors = {"PDF":"#f87171","XLSX":"#4ade80","XLS":"#4ade80",
                      "CSV":"#F0C040","DOCX":"#60a5fa","TXT":"#9A8AAA"}
        for fn in st.session_state.file_names:
            short = fn[:22]+"…" if len(fn) > 22 else fn
            ext   = fn.rsplit(".",1)[-1].upper() if "." in fn else "?"
            dc    = dot_colors.get(ext, "#4A3858")
            st.markdown(f'<div class="doc-pill">'
                        f'<div class="doc-dot" style="background:{dc};"></div>'
                        f'<span style="font-family:Space Mono,monospace;font-size:.44rem;'
                        f'color:{dc};margin-right:.25rem;">{ext}</span>{short}</div>',
                        unsafe_allow_html=True)

    st.markdown('<div class="sb-lbl">Quick Ask</div>', unsafe_allow_html=True)
    for q_item in ["What is USD/INR today?","Compare INR vs JPY vs Yuan",
                   "Gold price today?","Bitcoin vs Ethereum?",
                   "What was total revenue?","Main risk factors?","EPS change YoY?"]:
        if st.button(q_item, use_container_width=True, key=f"qa_{q_item[:14]}"):
            st.session_state["_prefill"] = q_item

    st.markdown('<div class="sb-lbl">Actions</div>', unsafe_allow_html=True)
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        if st.button("✕ Clear Chat", use_container_width=True):
            st.session_state.messages = []; st.rerun()
    with col_a2:
        if st.button("🗑 Clear Docs", use_container_width=True):
            for k in ["vectorstore","file_names","uploaded_docs","chunk_count",
                      "doc_full_text","auto_metrics","auto_generated","search_query",
                      "search_results","show_analytics"]:
                st.session_state[k] = (None if k=="vectorstore" else
                                       [] if k in ["file_names","auto_metrics","search_results"] else
                                       0  if k in ["uploaded_docs","chunk_count"] else
                                       False if k in ["auto_generated","show_analytics"] else "")
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# Pre-fetch market mood for mood-reactive button
_fng_pre = fetch_fear_greed(); fng_val = _fng_pre["value"]; fng_label = _fng_pre["label"]

# ─────────────────────────────────────────────────────────────────────────────
# ① TOP BAR — sticky, very top of page
#    Aesthetic + upload button | file status | analytics | chat | portfolio
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="top-upload-bar">', unsafe_allow_html=True)

# ── Three columns: [Upload cube] [Portfolio cube] [Search bar + misc] ─────────
_btn_upload, _btn_portfolio, _right_col = st.columns([1.6, 1.6, 6.8], gap="small")

# Mood class for portfolio button
_mood_cls_pf = "mood-bull" if fng_val >= 60 else ("mood-bear" if fng_val <= 35 else "")
_mood_icon   = "🐂" if fng_val >= 60 else ("🐻" if fng_val <= 35 else "◈")
_mood_word   = "Bull" if fng_val >= 60 else ("Bear" if fng_val <= 35 else "Neutral")
_n_pf_pre    = len(st.session_state.portfolio)
_pf_open_pre = st.session_state.show_portfolio
_pf_open_cls = "pf-open " if _pf_open_pre else ""
_pf_full_cls = f"sq-btn-simulate {_pf_open_cls}{_mood_cls_pf}".strip()
_pf_sub_lbl  = f"({_n_pf_pre} holdings)" if _n_pf_pre else f"{fng_label}"

with _btn_upload:
    st.markdown('<div class="sq-btn-upload">', unsafe_allow_html=True)
    _upload_icon = "✓⊞" if st.session_state.file_names else "⊞"
    _upload_lbl  = f"{_upload_icon}\n\nUpload\nDocument"
    if st.button(_upload_lbl, key="top_upload_btn", use_container_width=True,
                 help="Upload PDF · Excel · CSV · DOCX · TXT"):
        st.session_state.show_upload = not st.session_state.show_upload
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with _btn_portfolio:
    st.markdown(f'<div class="{_pf_full_cls}">', unsafe_allow_html=True)
    _pf_label = f"{_mood_icon} Portfolio\n{_mood_word} · {fng_val}\n{_pf_sub_lbl}"
    if st.button(_pf_label, key="top_portfolio_btn", use_container_width=True,
                 help=f"Market: {fng_label} ({fng_val}) · Build & simulate portfolio"):
        st.session_state.show_portfolio = not _pf_open_pre
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with _right_col:
    # Row: search bar | analytics | chat
    _right_inner = st.columns([5.5, 1.5, 0.8], gap="small")
    with _right_inner[0]:
        _raw_q = st.text_input(
            "global_search",
            value=st.session_state.search_query,
            placeholder="🔍  Search documents — revenue 2023, risk factors, gross margin…",
            label_visibility="collapsed",
            key="g_search_input",
        )
        if _raw_q and _raw_q != st.session_state.search_query:
            st.session_state.search_query = _raw_q
            hits = []
            if st.session_state.vectorstore:
                try:
                    vs    = st.session_state.vectorstore
                    q_emb = vs["model"].encode([_raw_q], normalize_embeddings=True).tolist()
                    res   = vs["collection"].query(query_embeddings=q_emb, n_results=5,
                                                   include=["documents","metadatas","distances"])
                    for chunk, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
                        hits.append({"filename": meta["filename"],
                                     "score":    round(1 - dist/2, 3),
                                     "snippet":  chunk[:300]})
                except: pass
            st.session_state.search_results = hits
        if not _raw_q and st.session_state.search_query:
            st.session_state.search_query = ""
            st.session_state.search_results = []
    with _right_inner[1]:
        if st.session_state.auto_generated:
            if st.button("📊 Analytics", use_container_width=True, key="top_analytics_btn"):
                st.session_state.show_analytics = not st.session_state.show_analytics
                st.rerun()
    with _right_inner[2]:
        if st.button("💬", key="chat_icon_btn", help="Chat"):
            st.session_state.show_chat = not st.session_state.show_chat
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Search results inline below bar
if st.session_state.search_query and st.session_state.search_results:
    st.markdown(f'<div class="sr-wrap"><div class="sr-title">'
                f'◈ {len(st.session_state.search_results)} results for '
                f'"{_ht.escape(st.session_state.search_query)}"</div>',
                unsafe_allow_html=True)
    for hit in st.session_state.search_results:
        rel  = int(hit["score"] * 100)
        bc2  = "#4ADE80" if rel >= 75 else ("#F0C040" if rel >= 50 else "#9A8AAA")
        st.markdown(f'<div class="sr-hit">'
                    f'<div class="sr-fname">📄 {_ht.escape(hit["filename"])} &nbsp;'
                    f'<span style="background:rgba(74,222,128,.1);border:1px solid rgba(74,222,128,.22);'
                    f'color:{bc2};font-family:Space Mono,monospace;font-size:.46rem;'
                    f'padding:.04rem .3rem;border-radius:3px;">{rel}% match</span></div>'
                    f'<div class="sr-snippet">{_ht.escape(hit["snippet"])}…</div></div>',
                    unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
elif st.session_state.search_query and not st.session_state.search_results:
    st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:.6rem;color:#4A3858;'
                f'padding:.35rem .7rem;background:rgba(107,45,107,.05);border:1px solid var(--border);'
                f'border-radius:8px;margin-bottom:.6rem;">'
                f'No results for "{_ht.escape(st.session_state.search_query)}" — '
                f'upload a document first, or use Chat for live market queries.'
                f'</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# UPLOAD DRAWER (appears below top bar when toggled)
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.show_upload:
    st.markdown('<div class="upload-drawer">'
                '<div class="upload-drawer-title">◈ Upload Financial Documents — PDF · XLSX · XLS · CSV · DOCX · TXT</div>',
                unsafe_allow_html=True)
    inline_files = st.file_uploader(
        "Upload", type=["pdf","txt","xlsx","xls","csv","docx"],
        accept_multiple_files=True, label_visibility="collapsed", key="drawer_upload",
    )
    col_ing, col_cls = st.columns([3, 1])
    with col_ing:
        if inline_files and st.button("⬆  Ingest Documents (FinBERT embeddings)", use_container_width=True, key="drawer_ingest"):
            if not GROQ_API_KEY:
                st.error("Enter your Groq API key in the sidebar first.")
            else:
                try:
                    n = ingest_documents(inline_files)
                    st.success(f"✓ {n} chunks from {len(inline_files)} file(s) ingested with FinBERT · Analytics auto-generated below ↓")
                    st.session_state.show_upload = False
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    with col_cls:
        if st.button("✕ Close", use_container_width=True, key="drawer_close"):
            st.session_state.show_upload = False; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CHAT PANEL (toggled via 💬 icon in top bar) — appears at top
# v8: Mode toggle (Chat / Analyst) + Source Evidence Panel
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.show_chat:
    st.markdown('<div class="chat-panel">', unsafe_allow_html=True)

    # ── Mode toggle bar ──────────────────────────────────────────────────────
    _mode_cols = st.columns([3, 2, 5])
    with _mode_cols[0]:
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.15em;'
                    'text-transform:uppercase;color:#4A3858;padding-top:.45rem;">Mode</div>',
                    unsafe_allow_html=True)
    with _mode_cols[1]:
        _is_analyst = st.session_state.analyst_mode
        _toggle_label = "⚡ Analyst Mode ON" if _is_analyst else "💬 Chat Mode"
        _toggle_color = "#F0C040" if _is_analyst else "#C084C8"
        if st.button(_toggle_label, key="mode_toggle_btn", use_container_width=True,
                     help="Toggle between conversational Chat Mode and structured Analyst Mode"):
            st.session_state.analyst_mode = not _is_analyst
            st.rerun()
    with _mode_cols[2]:
        if _is_analyst:
            st.markdown('<div style="font-family:Space Mono,monospace;font-size:.5rem;color:#F0C040;'
                        'padding-top:.45rem;opacity:.8;">'
                        '⚡ Returns structured tables · metrics grid · risk highlights · verdict</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-family:Space Mono,monospace;font-size:.5rem;color:#9A8AAA;'
                        'padding-top:.45rem;opacity:.8;">'
                        '💬 Conversational answers with source evidence panel</div>',
                        unsafe_allow_html=True)

    st.markdown(f'<div style="height:1px;background:linear-gradient(90deg,{"rgba(240,192,64,.25)" if _is_analyst else "rgba(139,58,139,.2)"},transparent);margin:.4rem 0 .7rem;"></div>',
                unsafe_allow_html=True)

    # ── Chat title ───────────────────────────────────────────────────────────
    st.markdown(f'<div class="chat-panel-title">{"⚡ Analyst Mode — Structured Financial Intelligence" if _is_analyst else "💬 AI Assistant — Markets, Currencies & Documents"}</div>',
                unsafe_allow_html=True)

    if not st.session_state.messages:
        if _is_analyst:
            st.markdown("""
<div style="text-align:center;padding:1.5rem 1rem;">
  <div style="font-size:1.8rem;margin-bottom:.5rem;opacity:.5;">⚡</div>
  <div style="font-family:'Cormorant Garamond',serif;font-size:1.35rem;font-weight:300;
    font-style:italic;color:#F0C040;">Analyst Mode Active</div>
  <div style="font-family:'Syne',sans-serif;font-size:.76rem;color:#9A8AAA;margin-top:.4rem;line-height:1.75;max-width:420px;margin-left:auto;margin-right:auto;">
    Ask financial questions and get structured outputs:<br>
    metrics grids · margin tables · risk highlights · analyst verdict<br>
    <span style="color:#4A3858;">Works best with uploaded documents</span>
  </div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
<div style="text-align:center;padding:1.5rem 1rem;">
  <div style="font-size:1.8rem;margin-bottom:.5rem;opacity:.5;">◈</div>
  <div style="font-family:'Cormorant Garamond',serif;font-size:1.35rem;font-weight:300;
    font-style:italic;color:#4A3858;">Ready without uploads</div>
  <div style="font-family:'Syne',sans-serif;font-size:.76rem;color:#4A3858;margin-top:.4rem;line-height:1.7;">
    Ask about live stocks, gold, crypto, FX rates — no documents needed.<br>
    Upload reports via 📎 above for deep document analysis.
  </div>
</div>""", unsafe_allow_html=True)

    # ── Render existing conversation ─────────────────────────────────────────
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant" and msg.get("analyst_mode"):
                # Re-render in analyst card format
                render_analyst_output(msg["content"], msg.get("question",""))
            else:
                st.markdown(msg["content"])
            # Source evidence panel for every assistant message
            if msg["role"] == "assistant" and msg.get("sources"):
                render_source_panel(msg["sources"])

    prefill  = st.session_state.pop("_prefill", None)
    question = st.chat_input("Ask about stocks, gold, crypto, currencies, or your documents…")
    q = prefill or question

    if q:
        if not GROQ_API_KEY:
            st.error("Please enter your Groq API key in the sidebar."); st.stop()

        with st.chat_message("user"):
            st.markdown(q)
        st.session_state.messages.append({"role":"user","content":q})

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    from openai import OpenAI
                    oai = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

                    fng_live = fetch_fear_greed()
                    fng_val_live = fng_live["value"]; fng_lbl_live = fng_live["label"]
                    symbols = ["AAPL","MSFT","NVDA","TSLA"]
                    stock_lines = [f"  {sym}: ${info['price']:,.2f} ({'▲' if info['pct']>=0 else '▼'}{abs(info['pct']):.2f}%)"
                                   for sym in symbols if (info := fetch_quote(sym))]
                    comm_lines  = [f"  {name}: ${info['price']:,.{dec}f} {unit} ({'+' if info['pct']>=0 else ''}{info['pct']:.2f}%)"
                                   for sym, (name, unit, _, dec) in COMMODITY_SYMS.items() if (info := fetch_quote(sym))]
                    crypto_lines = [f"  {ticker}: ${info['price']:,.{dec}f} ({'+' if info['pct']>=0 else ''}{info['pct']:.2f}%)"
                                    for sym, (name, ticker, _, dec) in CRYPTO_SYMS.items() if (info := fetch_quote(sym))]
                    fx_syms = ("USDINR=X","USDJPY=X","USDCNY=X","EURUSD=X","GBPUSD=X")
                    fx_lines = []
                    for _fxsym in fx_syms:
                        _fxi = fetch_quote(_fxsym)
                        if _fxi:
                            _p  = _fxi["price"]; _rs = f"{_p:,.2f}" if _p >= 10 else f"{_p:.4f}"
                            _sg = "+" if _fxi["pct"] >= 0 else ""
                            fx_lines.append(f"  {ALL_FX.get(_fxsym,{}).get('label',_fxsym)}: {_rs} ({_sg}{_fxi['pct']:.3f}%)")

                    utc_now = _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
                    live_context = (
                        f"=== LIVE MARKET DATA ({utc_now}) ===\n"
                        f"STOCKS:\n{chr(10).join(stock_lines) or '  (none)'}\n"
                        f"COMMODITIES:\n{chr(10).join(comm_lines) or '  (unavailable)'}\n"
                        f"CRYPTO:\n{chr(10).join(crypto_lines) or '  (unavailable)'}\n"
                        f"CURRENCIES (vs USD):\n{chr(10).join(fx_lines) or '  (unavailable)'}\n"
                        f"MARKET MOOD: Fear & Greed = {fng_val_live} ({fng_lbl_live})"
                    ).strip()

                    # ── Retrieve from vector store ────────────────────────────
                    doc_context = ""; sources_data = []
                    if st.session_state.vectorstore:
                        vs    = st.session_state.vectorstore
                        q_emb = vs["model"].encode([q], normalize_embeddings=True).tolist()
                        res   = vs["collection"].query(query_embeddings=q_emb, n_results=6,
                                                       include=["documents","metadatas","distances"])
                        cks, mts, dts = res["documents"][0], res["metadatas"][0], res["distances"][0]
                        doc_context  = "\n---\n".join(
                            f"[Source {i+1} | {m['filename']} | chunk {m.get('chunk','?')}]\n{c}"
                            for i, (c, m) in enumerate(zip(cks, mts)))
                        sources_data = [
                            {"filename": m["filename"],
                             "score":    round(1 - d/2, 3),
                             "preview":  c[:380],
                             "meta":     m,
                             "chunk_idx": m.get("chunk", idx)}
                            for idx, (c, m, d) in enumerate(zip(cks, mts, dts))
                        ]

                    # ── Build system prompt based on mode ────────────────────
                    is_analyst = st.session_state.analyst_mode

                    if is_analyst:
                        system_prompt = (
                            "You are a senior financial analyst producing structured research output. "
                            "When answering, ALWAYS structure your response as follows:\n\n"
                            "1. **KEY METRICS** — For each financial metric found, state it clearly: "
                            "'Revenue (FY23): $X.XB', 'Net Income: $X.XB', 'Gross Margin: XX%', etc.\n"
                            "2. **GROWTH & TRENDS** — YoY or QoQ changes with percentages.\n"
                            "3. **KEY RISK FACTORS** — List 2-4 specific risks mentioned.\n"
                            "4. **GUIDANCE & OUTLOOK** — Any forward-looking statements.\n"
                            "5. **OVERALL VERDICT** — One sentence conclusion with a Rating: "
                            "Strong Buy / Buy / Hold / Sell / Strong Sell.\n\n"
                            "Be precise. Use exact numbers from the documents. "
                            "Label every figure with its period (FY23, Q3 2024, etc.). "
                            "Never fabricate numbers. If data is unavailable, state '—'."
                        )
                    else:
                        system_prompt = (
                            "You are an expert financial analyst with real-time data access. "
                            "You have live prices for stocks, gold, silver, oil, crypto, and FX rates. "
                            "Use live data for market questions. For document questions, cite specific numbers. "
                            "Be concise, precise, never fabricate numbers."
                        )

                    user_msg = (f"{live_context}\n\n=== DOCUMENT CONTEXT ===\n{doc_context}\n\nQuestion: {q}"
                                if doc_context else f"{live_context}\n\nQuestion: {q}")

                    resp = oai.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            *[{"role": m["role"], "content": m["content"]}
                              for m in st.session_state.messages[:-1]],
                            {"role": "user", "content": user_msg},
                        ],
                        temperature=0.1 if is_analyst else 0.15,
                        max_tokens=1800,
                    )
                    answer = resp.choices[0].message.content
                    tokens = resp.usage.total_tokens

                    # ── Render answer ─────────────────────────────────────────
                    if is_analyst:
                        render_analyst_output(answer, q)
                    else:
                        st.markdown(answer)

                    # ── Source evidence panel ─────────────────────────────────
                    if sources_data:
                        render_source_panel(sources_data)

                    # ── Token / model caption ─────────────────────────────────
                    mode_lbl = "⚡ Analyst Mode" if is_analyst else "💬 Chat Mode"
                    st.caption(f"{mode_lbl} · llama-3.3-70b-versatile · {tokens} tokens · FinBERT retrieval · live data injected")

                    st.session_state.messages.append({
                        "role":         "assistant",
                        "content":      answer,
                        "sources":      sources_data,
                        "analyst_mode": is_analyst,
                        "question":     q,
                    })

                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="rag-header">
  <div class="rag-kicker">Financial Intelligence Platform</div>
  <h1>Interrogate Your<br><em>Financial Documents</em></h1>
  <p>Semantic search and AI-powered analysis across Annual Reports,
     10-Ks &amp; Earnings Transcripts. Live markets &amp; crypto always on.</p>
  <div class="badge-row">
    <span class="badge v">FinBERT Embeddings</span>
    <span class="badge v">Semantic Retrieval</span>
    <span class="badge v">Llama 3.3 · 70B</span>
    <span class="badge">Groq</span>
    <span class="badge g">Live Data</span>
    <span class="badge b">PDF · Excel · CSV · DOCX</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# STAT STRIP
# ─────────────────────────────────────────────────────────────────────────────
chunks = st.session_state.chunk_count
docs   = st.session_state.uploaded_docs
msgs   = len(st.session_state.messages) // 2
embed_label = "FinBERT" if "finbert" in st.session_state.get("_embed_model_name","").lower() else "MiniLM"
st.markdown(f"""
<div class="stat-strip">
  <div class="stat-cell"><div class="stat-lbl">Embeddings</div>
    <div class="stat-val-mono">{embed_label}</div></div>
  <div class="stat-cell"><div class="stat-lbl">Chunks Indexed</div>
    <div class="stat-val {'active' if chunks else ''}">{chunks if chunks else '—'}</div></div>
  <div class="stat-cell"><div class="stat-lbl">Documents</div>
    <div class="stat-val {'active' if docs else ''}">{docs if docs else '—'}</div></div>
  <div class="stat-cell"><div class="stat-lbl">Exchanges</div>
    <div class="stat-val {'active' if msgs else ''}">{msgs if msgs else '—'}</div></div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MARKET MOOD + GLOBAL INDICES
# ─────────────────────────────────────────────────────────────────────────────
fng = _fng_pre  # already fetched above for mood button
INDEX_SYMS = {"^GSPC":{"name":"S&P 500","flag":"🇺🇸"},"^IXIC":{"name":"NASDAQ","flag":"🇺🇸"},
              "^FTSE":{"name":"FTSE 100","flag":"🇬🇧"},"^NSEI":{"name":"NIFTY 50","flag":"🇮🇳"},
              "^N225":{"name":"Nikkei","flag":"🇯🇵"},"^GDAXI":{"name":"DAX","flag":"🇩🇪"}}
idx_quotes = fetch_multi_quotes(tuple(INDEX_SYMS.keys()))
idx_chips  = ""
for sym, meta in INDEX_SYMS.items():
    info = idx_quotes.get(sym)
    if info:
        arrow    = "▲" if info["pct"] >= 0 else "▼"
        cls      = "up" if info["pct"] >= 0 else "down"
        chip_cls = "chip-up" if info["pct"] >= 0 else "chip-down"
        idx_chips += (f'<div class="mood-idx-chip {chip_cls}"><div class="mood-idx-name">{meta["flag"]} {meta["name"]}</div>'
                      f'<div class="mood-idx-val">{info["price"]:,.0f}</div>'
                      f'<div class="mood-idx-chg {cls}">{arrow} {abs(info["pct"]):.2f}%</div></div>')
mood_color = "#f87171" if fng_val<25 else ("#fb923c" if fng_val<45 else ("#facc15" if fng_val<55 else ("#86efac" if fng_val<75 else "#4ade80")))
st.markdown(f"""
<div class="mood-bar-wrap">
  <div class="mood-title">◈ Market Mood &amp; Global Indices</div>
  <div style="display:flex;align-items:center;gap:1rem;margin-bottom:.7rem;">
    <div>
      <div style="display:flex;align-items:baseline;gap:.4rem;">
        <span class="mood-index" style="color:{mood_color};">{fng_val}</span>
        <span style="font-family:'Space Mono',monospace;font-size:.62rem;letter-spacing:.1em;color:{mood_color};">{fng_label}</span>
      </div>
      <div style="font-family:'Space Mono',monospace;font-size:.5rem;color:#4A3858;margin-top:.2rem;">Crypto Fear &amp; Greed · alternative.me</div>
    </div>
    <div style="flex:1;">
      <div class="mood-track"><div class="mood-needle" style="left:{fng_val}%;"></div></div>
      <div class="mood-labels"><span>Extreme Fear</span><span>Fear</span><span>Neutral</span><span>Greed</span><span>Extreme Greed</span></div>
    </div>
  </div>
  <div class="mood-indices">{idx_chips}</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# NEWS CAROUSELS
# ─────────────────────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────────────────────
# COMMODITIES
# ─────────────────────────────────────────────────────────────────────────────
comm_quotes = fetch_multi_quotes(tuple(COMMODITY_SYMS.keys()))
comm_chips  = "".join(
    make_chip_html(sym, f"{name} · {unit}", info["price"], info["pct"], prefix="$", decimals=dec, icon=icon)
    for sym, (name, unit, icon, dec) in COMMODITY_SYMS.items() if (info := comm_quotes.get(sym))
)
if comm_chips:
    st.markdown('<div class="comm-panel"><div class="comm-title">Precious Metals &amp; Commodities</div>'
                '<div class="chips-row">'+comm_chips+'</div>'
                '<div style="font-family:Space Mono,monospace;font-size:.5rem;color:#4A3858;'
                'margin-top:.65rem;text-align:right;">Futures · Yahoo Finance · 60s cache</div></div>',
                unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CRYPTO
# ─────────────────────────────────────────────────────────────────────────────
crypto_quotes = fetch_multi_quotes(tuple(CRYPTO_SYMS.keys()))
crypto_chips  = "".join(
    make_chip_html(ticker, name, info["price"], info["pct"], prefix="$", decimals=dec, icon=icon)
    for sym, (name, ticker, icon, dec) in CRYPTO_SYMS.items() if (info := crypto_quotes.get(sym))
)
if crypto_chips:
    st.markdown('<div class="crypto-panel"><div class="crypto-title">Crypto Markets</div>'
                '<div class="chips-row">'+crypto_chips+'</div>'
                '<div style="font-family:Space Mono,monospace;font-size:.5rem;color:#4A3858;'
                'margin-top:.65rem;text-align:right;">Spot · Yahoo Finance · 60s cache</div></div>',
                unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# LIVE STOCK CHART
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div style="background:#0D0B12;border:1px solid rgba(139,58,139,.22);'
            'border-radius:12px;padding:1.2rem 1.4rem .5rem;margin-bottom:1.4rem;">',
            unsafe_allow_html=True)
st.markdown('<div style="font-family:\'Cormorant Garamond\',serif;font-size:1.1rem;font-weight:300;'
            'color:#EDE8F5;margin-bottom:.8rem;display:flex;align-items:center;gap:.5rem;">'
            '<span style="display:inline-block;width:3px;height:1.1rem;'
            'background:linear-gradient(180deg,#6B2D6B,#C084C8);border-radius:2px;"></span>'
            'Live Stock Chart</div>', unsafe_allow_html=True)
col_sym, col_rng = st.columns([4, 1])
with col_sym:
    symbols = st.multiselect("symbols",
        options=["AAPL","MSFT","NVDA","GOOGL","AMZN","TSLA","META","TSM","SAP","BABA","SONY","NVO",
                 "RELIANCE.NS","TCS.NS","INFY.NS","WIPRO.NS"],
        default=["AAPL","MSFT","NVDA","TSLA"], label_visibility="collapsed")
with col_rng:
    rng = st.selectbox("range", ["1D","5D","1M","3M","6M","1Y"], index=2, label_visibility="collapsed")
period_map   = {"1D":"1d","5D":"5d","1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y"}
interval_map = {"1D":"5m","5D":"30m","1M":"1d","3M":"1d","6M":"1d","1Y":"1wk"}
if symbols:
    sq = fetch_multi_quotes(tuple(symbols))
    cps = []
    for sym in symbols:
        info = sq.get(sym)
        if info:
            arr = "▲" if info["pct"] >= 0 else "▼"
            cc  = "#4ade80" if info["pct"] >= 0 else "#f87171"
            cps.append(f'<div style="display:flex;flex-direction:column;align-items:center;'
                       f'background:#120E1A;border:1px solid rgba(139,58,139,.22);border-radius:8px;'
                       f'padding:.45rem .75rem;min-width:80px;font-family:Space Mono,monospace;">'
                       f'<span style="font-size:.62rem;color:#C084C8;font-weight:700;">{sym}</span>'
                       f'<span style="font-size:.74rem;color:#EDE8F5;margin-top:.1rem;">${info["price"]:,.2f}</span>'
                       f'<span style="font-size:.58rem;color:{cc};">{arr} {abs(info["pct"]):.2f}%</span></div>')
    if cps:
        st.markdown('<div style="display:flex;gap:.55rem;flex-wrap:wrap;margin-bottom:.8rem;">'
                    +"".join(cps)+"</div>", unsafe_allow_html=True)
    chart = pd.DataFrame()
    for sym in symbols:
        s = fetch_yahoo_series(sym, period_map[rng], interval_map[rng])
        if s is not None and not s.empty: chart[sym] = s
    if not chart.empty:
        normed = (chart.dropna(how="all").ffill() / chart.dropna(how="all").ffill().iloc[0] - 1) * 100
        st.line_chart(normed, height=230, use_container_width=True)
        st.caption(f"% return from period start · {rng} · Yahoo Finance")
    else:
        st.warning("Chart data unavailable — try again in a moment.")
else:
    st.info("Select at least one symbol above.")
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CURRENCY PANEL
# ─────────────────────────────────────────────────────────────────────────────
fx_options     = {f"{m['flag']} {m['label']} · {m['name']}": sym for sym, m in ALL_FX.items()}
default_labels = [k for k, v in fx_options.items()
                  if v in ("USDINR=X","USDJPY=X","USDCNY=X","EURUSD=X","GBPUSD=X","USDCHF=X")]
st.markdown('<div class="fx-panel"><div class="fx-panel-title">Currencies vs USD</div>',
            unsafe_allow_html=True)
fx_r1, fx_r2 = st.columns([5, 1])
with fx_r1:
    selected_labels = st.multiselect("currencies", options=list(fx_options.keys()),
        default=default_labels, label_visibility="collapsed", key="fx_select")
with fx_r2:
    fx_rng = st.selectbox("fx_range", ["1M","3M","6M","1Y"], index=0,
                          label_visibility="collapsed", key="fx_rng")
selected_syms = [fx_options[lbl] for lbl in selected_labels]
st.session_state["fx_select_syms"] = selected_syms
fx_period   = {"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y"}
fx_interval = {"1M":"1d","3M":"1d","6M":"1d","1Y":"1wk"}
if selected_syms:
    fx_chart = pd.DataFrame()
    for sym in selected_syms:
        meta = ALL_FX[sym]; s = fetch_yahoo_series(sym, fx_period[fx_rng], fx_interval[fx_rng])
        if s is not None and not s.empty:
            if meta["invert"]: s = 1.0 / s
            s = (s / s.iloc[0] - 1) * 100; s.name = meta["flag"]+" "+meta["label"]
            fx_chart[s.name] = s
    if not fx_chart.empty:
        st.line_chart(fx_chart.dropna(how="all").ffill(), height=220, use_container_width=True)
        st.caption(f"% change from {fx_rng} start · Rising = USD strengthening · Yahoo Finance")
    fx_quotes = fetch_multi_quotes(tuple(selected_syms))
    fx_chips  = []
    for sym in selected_syms:
        meta = ALL_FX[sym]; info = fx_quotes.get(sym)
        if info:
            rate     = info["price"]; pct = info["pct"]
            rs       = f"{rate:,.2f}" if rate >= 10 else f"{rate:.4f}"
            arr      = "▲" if pct > 0.005 else ("▼" if pct < -0.005 else "●")
            cls      = "up" if pct > 0.005 else ("down" if pct < -0.005 else "flat")
            chip_cls = "chip-up" if pct > 0.005 else ("chip-down" if pct < -0.005 else "chip-flat")
            fx_chips.append(f'<div class="price-chip {chip_cls}"><div class="pc-sym">{meta["flag"]} {meta["label"]}</div>'
                            f'<div class="pc-name">{meta["name"]}</div>'
                            f'<div class="pc-val">{rs}</div>'
                            f'<div class="pc-chg {cls}">{arr} {abs(pct):.3f}%</div></div>')
    if fx_chips:
        now_ist = _dt.datetime.utcnow() + _dt.timedelta(hours=5, minutes=30)
        st.markdown('<div class="chips-row" style="margin-top:.75rem;">'+"".join(fx_chips)
                    +f'</div><div style="font-family:Space Mono,monospace;font-size:.5rem;color:#4A3858;'
                    f'margin-top:.6rem;text-align:right;">Live · {now_ist.strftime("%H:%M")} IST · 60s cache</div>',
                    unsafe_allow_html=True)
else:
    st.info("Select at least one currency pair above.")
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# INDIA NEWS & POLICY
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.8rem;">
  <span style="display:inline-block;width:3px;height:1.4rem;
    background:linear-gradient(180deg,#6B2D6B,#C084C8);border-radius:2px;flex-shrink:0;"></span>
  <span style="font-family:'Cormorant Garamond',serif;font-size:1.35rem;font-weight:300;color:#EDE8F5;">
    India News &amp; Policy
  </span>
</div>
""", unsafe_allow_html=True)
nc1, nc2, nc3 = st.columns([3, 2, 1])
with nc1:
    sel_sources = st.multiselect("sources", options=list(NEWS_SOURCES.keys()),
        default=["📰 Economic Times","📰 Business Standard","🏛️ RBI Notifications","🏛️ Finance Ministry"],
        label_visibility="collapsed", key="news_sources")
with nc2:
    news_filter = st.selectbox("filter", ["All","Markets","Policy"], index=0,
                               label_visibility="collapsed", key="news_filter")
with nc3:
    n_per_source = st.selectbox("items", [3,5,8,10], index=0,
                                label_visibility="collapsed", key="news_n")
active_sources = [s for s in sel_sources if news_filter=="All" or NEWS_SOURCES[s]["tag"]==news_filter]
if active_sources:
    all_articles = []
    for src_name in active_sources:
        src_cfg  = NEWS_SOURCES[src_name]
        articles = fetch_rss(src_cfg["rss"], max_items=n_per_source)
        for a in articles: a["source"]=src_name; a["src_tag"]=src_cfg["tag"]
        all_articles.extend(articles)
    if all_articles:
        def render_card(a):
            tc = "#C084C8" if a["src_tag"]=="Policy" else "#4ade80"
            tb = "rgba(192,132,200,.1)" if a["src_tag"]=="Policy" else "rgba(74,222,128,.08)"
            tbd = "rgba(192,132,200,.3)" if a["src_tag"]=="Policy" else "rgba(74,222,128,.25)"
            ss  = a["source"].replace("📰 ","").replace("🏛️ ","")
            return (f'<div style="background:#0D0B12;border:1px solid rgba(139,58,139,.22);'
                    f'border-radius:10px;padding:.8rem 1rem;margin-bottom:.6rem;border-left:3px solid {tc};">'
                    f'<div style="display:flex;align-items:center;gap:.4rem;margin-bottom:.4rem;flex-wrap:wrap;">'
                    f'<span style="background:{tb};border:1px solid {tbd};color:{tc};'
                    f'font-family:\'Space Mono\',monospace;font-size:.52rem;letter-spacing:.1em;'
                    f'padding:.1rem .4rem;border-radius:3px;text-transform:uppercase;">{a["src_tag"]}</span>'
                    f'<span style="font-family:\'Space Mono\',monospace;font-size:.52rem;color:#4A3858;">{ss}</span>'
                    f'<span style="font-family:\'Space Mono\',monospace;font-size:.5rem;color:#4A3858;margin-left:auto;">{a["date"]}</span></div>'
                    f'<a href="{a.get("link","#")}" target="_blank" style="text-decoration:none;">'
                    f'<div style="font-family:\'Syne\',sans-serif;font-size:.82rem;font-weight:500;'
                    f'color:#EDE8F5;line-height:1.45;margin-bottom:.35rem;">{a["title"]}</div></a>'
                    f'<div style="font-family:\'Syne\',sans-serif;font-size:.72rem;color:#4A3858;'
                    f'line-height:1.5;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">'
                    f'{a.get("summary","")}</div></div>')
        col_l, col_r = st.columns(2)
        with col_l: st.markdown("".join(render_card(a) for a in all_articles[0::2]), unsafe_allow_html=True)
        with col_r: st.markdown("".join(render_card(a) for a in all_articles[1::2]), unsafe_allow_html=True)
        now_ist_n = _dt.datetime.utcnow() + _dt.timedelta(hours=5, minutes=30)
        st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:.5rem;color:#4A3858;'
                    f'text-align:right;margin-top:.2rem;">Fetched {now_ist_n.strftime("%H:%M")} IST · '
                    f'{len(all_articles)} articles · 10min cache</div>', unsafe_allow_html=True)
    else:
        st.info("No articles loaded — try refreshing or selecting different sources.")
else:
    st.info("Select at least one source above.")

st.markdown("<hr style='border-color:rgba(139,58,139,.15);margin:1.4rem 0;'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ③ INLINE ANALYTICS — appears BELOW market content after document upload
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.show_analytics and st.session_state.auto_generated:
    n_metrics = len(st.session_state.auto_metrics)
    st.markdown(
        f'<div class="analytics-banner">'
        f'<div class="ab-icon">🧠</div>'
        f'<div>'
        f'<div class="ab-title">FinBERT Analytics Ready — {n_metrics} metric{"s" if n_metrics!=1 else ""} auto-extracted</div>'
        f'<div class="ab-sub">Finance-specific embeddings (yiyanghkust/finbert-pretrain) · '
        f'Hybrid BM25 + Dense retrieval · Sector benchmarks</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )
    render_inline_analytics(
        vectorstore   = st.session_state.get("vectorstore"),
        groq_api_key  = GROQ_API_KEY,
        doc_full_text = st.session_state.get("doc_full_text",""),
        auto_metrics  = st.session_state.get("auto_metrics", []),
    )

elif st.session_state.file_names and not st.session_state.show_analytics:
    # Show a minimal nudge if docs loaded but analytics hidden
    st.markdown(
        '<div style="text-align:center;padding:.8rem;background:rgba(74,222,128,.04);'
        'border:1px solid rgba(74,222,128,.12);border-radius:10px;margin-bottom:1rem;">'
        '<span style="font-family:Space Mono,monospace;font-size:.6rem;color:#4A3858;">'
        '📊 Document analytics ready — click <strong style="color:#86efac;">View Analytics</strong> in the top bar</span>'
        '</div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# PORTFOLIO PANEL  (v7) — slides open when 💼 clicked
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.show_portfolio:
    if not _PORTFOLIO_READY:
        st.error(
            "Portfolio module requires extra packages. Install them with:\n\n"
            "```\npip install yfinance plotly scipy numpy\n```\n\n"
            "Then restart Streamlit."
        )
    else:
        # ── Inline CSS for portfolio panel ─────────────────────────────────
        st.markdown("""
<style>
/* ── PORTFOLIO PANEL ── */
.pfol-panel{background:var(--card);border:1px solid rgba(192,132,200,.3);
  border-radius:16px;padding:1.2rem 1.4rem;margin-bottom:1.2rem}
.pfol-stat-row{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;
  background:rgba(107,45,107,.2);border-radius:10px;overflow:hidden;
  border:1px solid rgba(107,45,107,.2);margin-bottom:1rem}
.pfol-stat{background:#0D0B12;padding:.7rem .9rem}
.pfol-stat-lbl{font-family:'Space Mono',monospace;font-size:.48rem;letter-spacing:.18em;
  text-transform:uppercase;color:#4A3858;margin-bottom:.25rem}
.pfol-stat-val{font-family:'Cormorant Garamond',serif;font-size:1.5rem;font-weight:300;color:#EDE8F5;line-height:1}
.pfol-stat-val.pos{color:#4ade80}.pfol-stat-val.neg{color:#f87171}
.hcard{background:#120E1A;border:1px solid rgba(139,58,139,.22);border-radius:12px;
  padding:.8rem 1rem;margin-bottom:.5rem}
.fund-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:.5rem;margin:.6rem 0}
.fund-cell{background:#120E1A;border:1px solid rgba(139,58,139,.18);border-radius:8px;padding:.5rem .7rem}
.fund-lbl{font-family:'Space Mono',monospace;font-size:.46rem;letter-spacing:.15em;text-transform:uppercase;color:#4A3858;margin-bottom:.2rem}
.fund-val{font-family:'Space Mono',monospace;font-size:.7rem;color:#EDE8F5}
.signal-badge{display:inline-flex;align-items:center;gap:.4rem;font-family:'Space Mono',monospace;
  font-size:.6rem;letter-spacing:.08em;text-transform:uppercase;padding:.25rem .6rem;border-radius:6px;font-weight:700}
.ai-report{background:#120E1A;border:1px solid rgba(139,58,139,.25);border-left:3px solid #C084C8;
  border-radius:0 10px 10px 0;padding:1rem 1.2rem;font-size:.86rem;color:#9A8AAA;line-height:1.9}
.ai-report strong{color:#EDE8F5}
</style>
        """, unsafe_allow_html=True)

        # ── Panel header ────────────────────────────────────────────────────
        st.markdown("""
<div style="background:linear-gradient(135deg,rgba(107,45,107,.2) 0%,rgba(13,11,18,.97) 100%);
  border:1px solid rgba(192,132,200,.35);border-radius:16px;padding:1rem 1.4rem .8rem;
  margin-bottom:.8rem;">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.5rem;">
    <div>
      <div style="font-family:'Space Mono',monospace;font-size:.52rem;letter-spacing:.22em;
        text-transform:uppercase;color:#C084C8;margin-bottom:.3rem;">v7 · New Feature</div>
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.6rem;font-weight:300;color:#EDE8F5;">
        Portfolio &amp; <em style="font-style:italic;">Stock Analysis</em>
      </div>
      <div style="font-family:'Syne',sans-serif;font-size:.75rem;color:#9A8AAA;margin-top:.25rem;">
        Build your portfolio · AI stock deep-dives · Candlestick + RSI + MACD charts · Signal scoring
      </div>
    </div>
    <div style="display:flex;gap:.4rem;flex-wrap:wrap;">
      <span style="font-family:'Space Mono',monospace;font-size:.52rem;padding:.2rem .5rem;
        background:rgba(74,222,128,.08);border:1px solid rgba(74,222,128,.22);color:#86efac;border-radius:4px;">yfinance</span>
      <span style="font-family:'Space Mono',monospace;font-size:.52rem;padding:.2rem .5rem;
        background:rgba(192,132,200,.08);border:1px solid rgba(192,132,200,.22);color:#C084C8;border-radius:4px;">Plotly</span>
      <span style="font-family:'Space Mono',monospace;font-size:.52rem;padding:.2rem .5rem;
        background:rgba(240,192,64,.08);border:1px solid rgba(240,192,64,.22);color:#F0C040;border-radius:4px;">Llama 3.3-70B</span>
    </div>
  </div>
</div>
        """, unsafe_allow_html=True)

        # ── Tab navigation ──────────────────────────────────────────────────
        pfol_tabs = st.tabs(["💼 My Portfolio", "🔎 Stock Deep-Dive", "📈 Performance", "🤖 AI Report", "⚙️ Manage Holdings"])

        # ─── helpers ─────────────────────────────────────────────────────────
        CHART_BG="#07060C"; CHART_CARD="#0D0B12"; CHART_GRID="rgba(139,58,139,.12)"
        CHART_TEXT="#EDE8F5"; CHART_DIM="#9A8AAA"; CHART_ACC="#C084C8"
        CHART_GREEN="#4ADE80"; CHART_RED="#F87171"; CHART_GOLD="#F0C040"
        _BASE_LAYOUT=dict(paper_bgcolor=CHART_BG,plot_bgcolor=CHART_CARD,
            font=dict(family="Space Mono, monospace",color=CHART_TEXT,size=10),
            margin=dict(l=30,r=20,t=36,b=30),
            xaxis=dict(gridcolor=CHART_GRID,zeroline=False,showgrid=True),
            yaxis=dict(gridcolor=CHART_GRID,zeroline=False,showgrid=True),
            hovermode="x unified",
            legend=dict(bgcolor="rgba(0,0,0,0)",bordercolor=CHART_GRID,borderwidth=1))

        # ── GLOBAL STOCK UNIVERSE ─────────────────────────────────────────────
        POPULAR_STOCKS={
            "🇺🇸 US Mega Cap": [
                "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","BRK-B","JPM","V",
                "UNH","XOM","LLY","JNJ","AVGO","MA","PG","HD","MRK","CVX",
            ],
            "🇺🇸 US Mid Cap / Growth": [
                "PLTR","SNOW","COIN","HOOD","RBLX","LYFT","UBER","ABNB","DASH","DKNG",
                "SOFI","AFRM","RIVN","LCID","SMCI","ARM","CRWD","ZS","PANW","NET",
            ],
            "🇮🇳 India NSE — Blue Chip": [
                "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
                "WIPRO.NS","HINDUNILVR.NS","BAJFINANCE.NS","AXISBANK.NS","LT.NS",
                "TATAMOTORS.NS","SUNPHARMA.NS","KOTAKBANK.NS","ONGC.NS","SBIN.NS",
            ],
            "🇮🇳 India NSE — Mid Cap": [
                "ADANIENT.NS","ADANIPORTS.NS","ZOMATO.NS","PAYTM.NS","NYKAA.NS",
                "DELHIVERY.NS","POLICYBZR.NS","IRCTC.NS","DIXON.NS","TATAPOWER.NS",
                "PIDILITIND.NS","MUTHOOTFIN.NS","COFORGE.NS","PERSISTENT.NS","LTIM.NS",
            ],
            "🇨🇳 China / HK": [
                "BABA","JD","BIDU","NIO","PDD","9988.HK","700.HK","9618.HK",
                "1810.HK","3690.HK","2318.HK","0388.HK","0941.HK","TCEHY","XPEV",
            ],
            "🇯🇵 Japan (TSE)": [
                "7203.T","6758.T","9984.T","8306.T","6861.T","9432.T","8058.T",
                "SONY","TM","HMC","FANUY","MUFG","NTT","FUJIY","NTDOY",
            ],
            "🇰🇷 South Korea (KRX)": [
                "005930.KS","000660.KS","005380.KS","035420.KS","051910.KS",
                "006400.KS","000270.KS","068270.KS","207940.KS","035720.KS",
            ],
            "🇬🇧 United Kingdom (LSE)": [
                "AZN.L","SHEL.L","HSBA.L","BP.L","GSK.L","DGE.L","RIO.L",
                "ULVR.L","LLOY.L","VOD.L","BT-A.L","BARC.L","BATS.L","REL.L",
            ],
            "🇩🇪 Germany (XETRA)": [
                "SAP.DE","SIE.DE","ALV.DE","MBG.DE","BMW.DE","VOW3.DE","BAS.DE",
                "BAYN.DE","MUV2.DE","ADS.DE","DTE.DE","DBK.DE","RWE.DE","HEN3.DE",
            ],
            "🇫🇷 France (Euronext)": [
                "MC.PA","OR.PA","SAN.PA","TTE.PA","BNP.PA","AIR.PA","SU.PA",
                "DG.PA","CAP.PA","KER.PA","ACA.PA","GLE.PA","SAF.PA","TEP.PA",
            ],
            "🇨🇭 Switzerland (SIX)": [
                "NESN.SW","NOVN.SW","ROG.SW","ABBN.SW","ZURN.SW","UBSG.SW",
                "CSGN.SW","SREN.SW","LONN.SW","GIVN.SW","SLHN.SW","PGHN.SW",
            ],
            "🇳🇱 Netherlands": [
                "ASML","ASML.AS","HEIA.AS","REN.AS","INGA.AS","NN.AS","AKZA.AS",
                "PHIA.AS","WKL.AS","AD.AS","ABN.AS","DSM.AS","KPN.AS","MT.AS",
            ],
            "🇸🇪 Nordics (Sweden/Norway)": [
                "ERIC-B.ST","VOLV-B.ST","ATCO-A.ST","SEB-A.ST","SHB-A.ST",
                "NHY.OL","DNB.OL","EQNR.OL","MOWI.OL","ORK.OL",
            ],
            "🇦🇺 Australia (ASX)": [
                "BHP.AX","CBA.AX","CSL.AX","NAB.AX","WBC.AX","ANZ.AX",
                "MQG.AX","WES.AX","FMG.AX","RIO.AX","TLS.AX","WOW.AX","GMG.AX",
            ],
            "🇨🇦 Canada (TSX)": [
                "SHOP","RY","TD","BNS","BMO","CNR","ENB","SU","ABX","BCE",
                "MFC","POW","TRI","CP","AEM",
            ],
            "🇧🇷 Brazil (B3)": [
                "VALE","PBR","ITUB","BBD","BRKM5.SA","PETR4.SA","BBAS3.SA",
                "WEGE3.SA","MGLU3.SA","SUZB3.SA","RENT3.SA","JBSS3.SA",
            ],
            "🇸🇬 Singapore (SGX)": [
                "D05.SI","O39.SI","U11.SI","Z74.SI","C6L.SI","G13.SI",
                "BN4.SI","U96.SI","F34.SI","C38U.SI","A17U.SI","ME8U.SI",
            ],
            "🌍 Emerging Markets": [
                "TSM","VALE","PBR","GOLD","NEM","FCX","SCCO","MT","BTG","KGC",
                "ITUB","BBD","ERJ","VIV","GFI",
            ],
            "📈 US Sector ETFs": [
                "XLK","XLF","XLE","XLV","XLI","XLY","XLP","XLB","XLRE","XLU",
                "XLC","GLD","SLV","USO","TLT",
            ],
            "📈 Global / Broad ETFs": [
                "SPY","QQQ","VTI","IWM","DIA","EEM","EFA","VEA","VWO","ARKK",
                "IEMG","ACWI","VT","BNDX","AGG",
            ],
            "💎 Semiconductor & AI": [
                "NVDA","AMD","INTC","TSM","ASML","AMAT","LRCX","KLAC","MU","MRVL",
                "QCOM","AVGO","TXN","ADI","MCHP",
            ],
            "🏦 Global Banks": [
                "JPM","BAC","WFC","C","GS","MS","HSBC","BCS","CS","DB",
                "BNP.PA","SAN","BBVA","ITUB","RY",
            ],
        }

        # ── Global ticker search helper ────────────────────────────────────────
        @st.cache_data(ttl=120, show_spinner=False)
        def _search_ticker(query: str) -> list[dict]:
            """Search Yahoo Finance for tickers matching a query string."""
            if not query or len(query) < 2:
                return []
            try:
                url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&newsCount=0&enableFuzzyQuery=true&quotesCount=10"
                r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=6)
                data = r.json()
                results = []
                for q in data.get("quotes", [])[:12]:
                    sym   = q.get("symbol","")
                    name  = q.get("longname") or q.get("shortname") or sym
                    exch  = q.get("exchDisp","")
                    qtype = q.get("quoteType","")
                    if sym and qtype in ("EQUITY","ETF","MUTUALFUND","INDEX","CURRENCY","CRYPTOCURRENCY"):
                        results.append({"symbol":sym,"name":name[:45],"exchange":exch,"type":qtype})
                return results
            except:
                return []

        @st.cache_data(ttl=300, show_spinner=False)
        def _get_stock(ticker):
            try:
                t=yf.Ticker(ticker); info=t.info or {}
                hist=t.history(period="1y",auto_adjust=True)
                cur=info.get("currentPrice") or info.get("regularMarketPrice") or (hist["Close"].iloc[-1] if not hist.empty else 0)
                return {"ticker":ticker,"name":info.get("longName") or info.get("shortName") or ticker,
                    "sector":info.get("sector","—"),"industry":info.get("industry","—"),
                    "exchange":info.get("exchange","—"),"currency":info.get("currency","USD"),
                    "market_cap":info.get("marketCap"),"pe_ratio":info.get("trailingPE") or info.get("forwardPE"),
                    "forward_pe":info.get("forwardPE"),"pb_ratio":info.get("priceToBook"),
                    "roe":info.get("returnOnEquity"),"roa":info.get("returnOnAssets"),
                    "gross_margin":info.get("grossMargins"),"operating_margin":info.get("operatingMargins"),
                    "profit_margin":info.get("profitMargins"),"revenue":info.get("totalRevenue"),
                    "revenue_growth":info.get("revenueGrowth"),"earnings_growth":info.get("earningsGrowth"),
                    "debt_to_equity":info.get("debtToEquity"),"current_ratio":info.get("currentRatio"),
                    "free_cash_flow":info.get("freeCashflow"),"dividend_yield":info.get("dividendYield"),
                    "beta":info.get("beta"),"52w_high":info.get("fiftyTwoWeekHigh"),
                    "52w_low":info.get("fiftyTwoWeekLow"),"target_price":info.get("targetMeanPrice"),
                    "analyst_rating":info.get("recommendationKey","").replace("_"," ").title(),
                    "analyst_count":info.get("numberOfAnalystOpinions"),
                    "current_price":cur,"prev_close":info.get("previousClose"),
                    "description":(info.get("longBusinessSummary") or "")[:400],"hist":hist,
                    "error":None}
            except Exception as e:
                return {"ticker":ticker,"name":ticker,"hist":None,"error":str(e),"current_price":0}

        @st.cache_data(ttl=300, show_spinner=False)
        def _get_hist_multi(tickers_tuple, period="1y"):
            try:
                raw=yf.download(list(tickers_tuple),period=period,auto_adjust=True,progress=False,group_by="ticker")
                result={}
                for t in tickers_tuple:
                    try: result[t]=(raw["Close"] if len(tickers_tuple)==1 else raw[t]["Close"]).dropna()
                    except: pass
                return result
            except: return {}

        def _calc_tech(hist):
            if hist is None or hist.empty or len(hist)<20: return {}
            close=hist["Close"]
            sma20=close.rolling(20).mean().iloc[-1]
            sma50=close.rolling(50).mean().iloc[-1] if len(close)>=50 else None
            sma200=close.rolling(200).mean().iloc[-1] if len(close)>=200 else None
            delta=close.diff(); gain=delta.clip(lower=0).rolling(14).mean()
            loss=(-delta.clip(upper=0)).rolling(14).mean()
            rsi=(100-100/(1+gain/(loss+1e-9))).iloc[-1]
            ema12=close.ewm(span=12).mean(); ema26=close.ewm(span=26).mean()
            macd=(ema12-ema26).iloc[-1]; sig_line=(ema12-ema26).ewm(span=9).mean().iloc[-1]
            bb_mid=close.rolling(20).mean(); bb_std=close.rolling(20).std()
            bb_up=(bb_mid+2*bb_std).iloc[-1]; bb_lo=(bb_mid-2*bb_std).iloc[-1]
            rets=close.pct_change().dropna(); ann_vol=rets.std()*np.sqrt(252)*100
            ret_1d=(close.iloc[-1]/close.iloc[-2]-1)*100 if len(close)>=2 else 0
            ret_1w=(close.iloc[-1]/close.iloc[-5]-1)*100 if len(close)>=5 else 0
            ret_1m=(close.iloc[-1]/close.iloc[-21]-1)*100 if len(close)>=21 else 0
            ret_3m=(close.iloc[-1]/close.iloc[-63]-1)*100 if len(close)>=63 else 0
            ret_1y=(close.iloc[-1]/close.iloc[0]-1)*100
            sharpe=(ret_1y-5.25)/(ann_vol+1e-9)
            curr=close.iloc[-1]
            trend="Strong Bullish" if (sma50 and curr>sma50) else ("Bullish" if curr>sma20 else "Bearish")
            rsi_sig="Overbought" if rsi>70 else ("Oversold" if rsi<30 else "Neutral")
            return dict(current=curr,sma20=sma20,sma50=sma50,sma200=sma200,rsi=rsi,rsi_signal=rsi_sig,
                macd=macd,macd_signal=sig_line,bb_upper=bb_up,bb_lower=bb_lo,
                ann_vol=ann_vol,sharpe=sharpe,ret_1d=ret_1d,ret_1w=ret_1w,ret_1m=ret_1m,
                ret_3m=ret_3m,ret_1y=ret_1y,trend=trend)

        def _signal(info, tech):
            score=0; signals=[]
            pe=info.get("pe_ratio")
            if pe and pe<20: score+=1; signals.append(("P/E < 20","+","Value"))
            elif pe and pe>40: score-=1; signals.append(("P/E > 40","−","Overvalued"))
            roe=info.get("roe")
            if roe and roe>0.15: score+=1; signals.append(("ROE > 15%","+","Quality"))
            if info.get("profit_margin") and info["profit_margin"]>0.15: score+=1; signals.append(("Net Margin > 15%","+","Quality"))
            if info.get("revenue_growth") and info["revenue_growth"]>0.10: score+=1; signals.append(("Rev Growth > 10%","+","Growth"))
            if info.get("debt_to_equity") and info["debt_to_equity"]>200: score-=1; signals.append(("High D/E","−","Risk"))
            rsi=tech.get("rsi")
            if rsi:
                if rsi<30: score+=2; signals.append(("RSI Oversold","+","Technical"))
                elif rsi>70: score-=2; signals.append(("RSI Overbought","−","Technical"))
            macd=tech.get("macd"); msig=tech.get("macd_signal")
            if macd and msig:
                if macd>msig: score+=1; signals.append(("MACD Bullish","+","Technical"))
                else: score-=1; signals.append(("MACD Bearish","−","Technical"))
            sma50=tech.get("sma50"); curr=tech.get("current")
            if sma50 and curr:
                if curr>sma50: score+=1; signals.append(("Above SMA50","+","Trend"))
                else: score-=1; signals.append(("Below SMA50","−","Trend"))
            rat=info.get("analyst_rating","").lower()
            if "buy" in rat or "outperform" in rat: score+=1; signals.append(("Analyst Buy","+","Consensus"))
            elif "sell" in rat or "underperform" in rat: score-=1; signals.append(("Analyst Sell","−","Consensus"))
            score=max(-6,min(6,score))
            if score>=3: v,c="Strong Buy","#4ade80"
            elif score>=1: v,c="Buy","#86efac"
            elif score>=-1: v,c="Hold","#F0C040"
            elif score>=-3: v,c="Sell","#fb923c"
            else: v,c="Strong Sell","#f87171"
            return {"score":score,"verdict":v,"color":c,"signals":signals}

        def _fc(val,unit="USD"):
            if val is None: return "—"
            if unit=="USD":
                if abs(val)>=1e12: return f"${val/1e12:.2f}T"
                if abs(val)>=1e9:  return f"${val/1e9:.2f}B"
                if abs(val)>=1e6:  return f"${val/1e6:.1f}M"
                if abs(val)>=1e3:  return f"${val/1e3:.1f}K"
                return f"${val:,.2f}"
            if unit=="%": return f"{val*100:.1f}%" if abs(val)<10 else f"{val:.1f}%"
            if unit=="x": return f"{val:.2f}x"
            return f"{val:,.2f}"

        def _pfol_metrics():
            holdings=st.session_state.portfolio_holdings
            cache=st.session_state.portfolio_prices_cache
            total_v=0; total_c=0; positions=[]
            for ticker,h in holdings.items():
                info=cache.get(ticker,{}); price=info.get("current_price") or 0
                shares=h.get("shares",0); cost=h.get("avg_cost",0)
                mv=price*shares; cb=cost*shares; pnl=mv-cb
                pnl_pct=(pnl/cb*100) if cb else 0
                total_v+=mv; total_c+=cb
                positions.append(dict(ticker=ticker,name=(info.get("name",ticker) or ticker)[:22],
                    shares=shares,avg_cost=cost,current_price=price,market_value=mv,
                    cost_basis=cb,pnl=pnl,pnl_pct=pnl_pct,weight=0,
                    beta=info.get("beta") or 1.0,sector=info.get("sector","—")))
            for p in positions:
                p["weight"]=(p["market_value"]/total_v*100) if total_v else 0
            total_pnl=total_v-total_c
            return dict(total_value=total_v,total_cost=total_c,total_pnl=total_pnl,
                total_pnl_pct=(total_pnl/total_c*100 if total_c else 0),positions=positions,
                weighted_beta=sum(p["beta"]*p["weight"]/100 for p in positions) if positions else 1.0,
                num_positions=len(positions))

        # Chart builders
        def _chart_candle(info, ticker):
            h=info.get("hist")
            if h is None or h.empty: return go.Figure()
            df=h.tail(90)
            fig=make_subplots(rows=2,cols=1,shared_xaxes=True,row_heights=[0.72,0.28],vertical_spacing=0.02)
            fig.add_trace(go.Candlestick(x=df.index,open=df["Open"],high=df["High"],
                low=df["Low"],close=df["Close"],name="Price",
                increasing_line_color=CHART_GREEN,decreasing_line_color=CHART_RED,
                increasing_fillcolor=CHART_GREEN,decreasing_fillcolor=CHART_RED),row=1,col=1)
            for period,color in [(20,CHART_ACC),(50,CHART_GOLD)]:
                if len(df)>=period:
                    sma=df["Close"].rolling(period).mean()
                    fig.add_trace(go.Scatter(x=df.index,y=sma,name=f"SMA{period}",
                        line=dict(color=color,width=1,dash="dot"),opacity=0.8),row=1,col=1)
            if "Volume" in df.columns:
                vc=[CHART_GREEN if df["Close"].iloc[i]>=df["Open"].iloc[i] else CHART_RED for i in range(len(df))]
                fig.add_trace(go.Bar(x=df.index,y=df["Volume"],name="Volume",
                    marker_color=vc,opacity=0.5),row=2,col=1)
            fig.update_layout(**_BASE_LAYOUT,title=dict(text=f"{ticker} — 90-Day Candlestick",
                font=dict(size=12,color=CHART_TEXT)),height=380)
            fig.update_xaxes(rangeslider_visible=False)
            return fig

        def _chart_rsi(info, ticker):
            h=info.get("hist")
            if h is None or h.empty: return go.Figure()
            close=h["Close"].tail(90)
            delta=close.diff(); gain=delta.clip(lower=0).rolling(14).mean()
            loss=(-delta.clip(upper=0)).rolling(14).mean()
            rsi_s=(100-100/(1+gain/(loss+1e-9))).dropna()
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=rsi_s.index,y=rsi_s,name="RSI(14)",
                line=dict(color=CHART_ACC,width=1.5)))
            fig.add_hline(y=70,line_dash="dot",line_color=CHART_RED,
                annotation_text="Overbought 70",annotation_font_color=CHART_RED)
            fig.add_hline(y=30,line_dash="dot",line_color=CHART_GREEN,
                annotation_text="Oversold 30",annotation_font_color=CHART_GREEN)
            fig.add_hrect(y0=70,y1=100,fillcolor=CHART_RED,opacity=0.05,line_width=0)
            fig.add_hrect(y0=0,y1=30,fillcolor=CHART_GREEN,opacity=0.05,line_width=0)
            fig.update_layout(**_BASE_LAYOUT,title=dict(text="RSI (14)",
                font=dict(size=11,color=CHART_TEXT)),height=220,yaxis=dict(range=[0,100],gridcolor=CHART_GRID))
            return fig

        def _chart_macd(info, ticker):
            h=info.get("hist")
            if h is None or h.empty: return go.Figure()
            close=h["Close"].tail(120)
            ema12=close.ewm(span=12).mean(); ema26=close.ewm(span=26).mean()
            macd_l=ema12-ema26; sig=macd_l.ewm(span=9).mean(); hb=macd_l-sig
            vc=[CHART_GREEN if v>=0 else CHART_RED for v in hb]
            fig=make_subplots(rows=1,cols=1)
            fig.add_trace(go.Bar(x=close.index,y=hb,name="Histogram",marker_color=vc,opacity=0.6))
            fig.add_trace(go.Scatter(x=close.index,y=macd_l,name="MACD",line=dict(color=CHART_ACC,width=1.5)))
            fig.add_trace(go.Scatter(x=close.index,y=sig,name="Signal",line=dict(color=CHART_GOLD,width=1,dash="dot")))
            fig.update_layout(**_BASE_LAYOUT,title=dict(text="MACD (12,26,9)",
                font=dict(size=11,color=CHART_TEXT)),height=200)
            return fig

        def _chart_donut(positions):
            if not positions: return go.Figure()
            labels=[p["ticker"] for p in positions]; values=[p["market_value"] for p in positions]
            colors=px.colors.qualitative.Prism
            fig=go.Figure(go.Pie(labels=labels,values=values,hole=0.58,textinfo="label+percent",
                textfont=dict(size=9,color=CHART_TEXT),
                marker=dict(colors=colors[:len(labels)],line=dict(color=CHART_BG,width=2)),
                hovertemplate="<b>%{label}</b><br>%{value:$,.0f} (%{percent})<extra></extra>"))
            fig.update_layout(**_BASE_LAYOUT,title=dict(text="Portfolio Allocation",
                font=dict(size=11,color=CHART_TEXT)),height=280,showlegend=False,
                annotations=[dict(text="Allocation",x=0.5,y=0.5,showarrow=False,
                    font=dict(size=9,color=CHART_DIM))])
            return fig

        def _chart_pnl(positions):
            if not positions: return go.Figure()
            sorted_p=sorted(positions,key=lambda x:x["pnl_pct"])
            tickers=[p["ticker"] for p in sorted_p]; pnls=[p["pnl_pct"] for p in sorted_p]
            colors=[CHART_GREEN if v>=0 else CHART_RED for v in pnls]
            fig=go.Figure(go.Bar(x=tickers,y=pnls,marker_color=colors,
                text=[f"{v:+.1f}%" for v in pnls],textposition="outside",
                textfont=dict(size=9,color=CHART_TEXT)))
            fig.update_layout(**_BASE_LAYOUT,title=dict(text="P&L % by Position",
                font=dict(size=11,color=CHART_TEXT)),height=280,yaxis_ticksuffix="%")
            fig.add_hline(y=0,line_color="rgba(255,255,255,.2)",line_width=1)
            return fig

        def _chart_perf(tickers_tuple, period="1y"):
            hd=_get_hist_multi(tickers_tuple, period)
            fig=go.Figure()
            pal=[CHART_ACC,CHART_GREEN,CHART_GOLD,"#60a5fa","#fb923c","#f472b6","#34d399","#a78bfa"]
            for i,(tk,h) in enumerate(hd.items()):
                if h is None or h.empty: continue
                normed=(h/h.iloc[0]-1)*100
                fig.add_trace(go.Scatter(x=normed.index,y=normed,name=tk,
                    line=dict(color=pal[i%len(pal)],width=1.5),
                    hovertemplate=f"<b>{tk}</b>: %{{y:.1f}}%<extra></extra>"))
            fig.add_hline(y=0,line_color="rgba(255,255,255,.15)",line_dash="dot")
            fig.update_layout(**_BASE_LAYOUT,title=dict(text=f"Normalised Performance ({period})",
                font=dict(size=11,color=CHART_TEXT)),height=320,yaxis_ticksuffix="%")
            return fig

        # ── TAB 0: MY PORTFOLIO ────────────────────────────────────────────
        with pfol_tabs[0]:
            holdings=st.session_state.portfolio_holdings
            if not holdings:
                st.markdown("""
<div style="text-align:center;padding:3rem 1rem;">
  <div style="font-size:2.5rem;margin-bottom:.7rem;opacity:.3;">💼</div>
  <div style="font-family:'Cormorant Garamond',serif;font-size:1.5rem;font-weight:300;
    font-style:italic;color:#4A3858;">No holdings yet</div>
  <div style="font-family:'Syne',sans-serif;font-size:.78rem;color:#4A3858;margin-top:.5rem;line-height:1.8;">
    Go to <strong style="color:#C084C8;">⚙️ Manage Holdings</strong> to add stocks<br>
    or use <strong style="color:#C084C8;">🔎 Stock Deep-Dive</strong> to analyse any stock
  </div>
</div>""", unsafe_allow_html=True)
            else:
                with st.spinner("Fetching live prices…"):
                    for tk in holdings:
                        if tk not in st.session_state.portfolio_prices_cache:
                            st.session_state.portfolio_prices_cache[tk]=_get_stock(tk)
                m=_pfol_metrics()
                pnl_cls="pos" if m["total_pnl"]>=0 else "neg"
                pnl_sgn="+" if m["total_pnl"]>=0 else ""
                st.markdown(f"""
<div class="pfol-stat-row">
  <div class="pfol-stat"><div class="pfol-stat-lbl">Portfolio Value</div>
    <div class="pfol-stat-val">{_fc(m["total_value"])}</div></div>
  <div class="pfol-stat"><div class="pfol-stat-lbl">Total Cost</div>
    <div class="pfol-stat-val">{_fc(m["total_cost"])}</div></div>
  <div class="pfol-stat"><div class="pfol-stat-lbl">Total P&amp;L</div>
    <div class="pfol-stat-val {pnl_cls}">{pnl_sgn}{_fc(m["total_pnl"])}</div></div>
  <div class="pfol-stat"><div class="pfol-stat-lbl">Return %</div>
    <div class="pfol-stat-val {pnl_cls}">{pnl_sgn}{m["total_pnl_pct"]:.2f}%</div></div>
</div>""", unsafe_allow_html=True)
                bc1,bc2,bc3=st.columns(3)
                bc1.metric("Portfolio Beta",f"{m['weighted_beta']:.2f}")
                bc2.metric("Positions",m["num_positions"])
                bc3.metric("Return",f"{m['total_pnl_pct']:.1f}%",delta=f"{m['total_pnl_pct']:.1f}%")
                if len(m["positions"])>=2:
                    dc1,dc2=st.columns(2)
                    with dc1: st.plotly_chart(_chart_donut(m["positions"]),use_container_width=True,config={"displayModeBar":False})
                    with dc2: st.plotly_chart(_chart_pnl(m["positions"]),use_container_width=True,config={"displayModeBar":False})
                # Holdings table
                st.markdown('<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.18em;text-transform:uppercase;color:#C084C8;margin:.7rem 0 .4rem;">Position Details</div>',unsafe_allow_html=True)
                rows=[{"Ticker":p["ticker"],"Name":p["name"],"Shares":p["shares"],
                    "Avg Cost":f'${p["avg_cost"]:.2f}',"Price":f'${p["current_price"]:.2f}',
                    "Value":_fc(p["market_value"]),"P&L %":f'{p["pnl_pct"]:+.1f}%',
                    "P&L $":_fc(p["pnl"]),"Weight":f'{p["weight"]:.1f}%',"Sector":p["sector"]}
                    for p in sorted(m["positions"],key=lambda x:x["market_value"],reverse=True)]
                if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

        # ── TAB 1: STOCK DEEP-DIVE ─────────────────────────────────────────
        with pfol_tabs[1]:
            st.markdown("""
<div style="background:linear-gradient(90deg,rgba(107,45,107,.12),rgba(13,11,18,.0));
  border-left:3px solid #C084C8;padding:.5rem .9rem;border-radius:0 8px 8px 0;margin-bottom:.8rem;">
  <div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.18em;
    text-transform:uppercase;color:#C084C8;">🌍 Global Stock Search — Any Exchange, Any Market</div>
  <div style="font-family:Syne,sans-serif;font-size:.72rem;color:#4A3858;margin-top:.2rem;">
    Search by company name or ticker · NYSE · NASDAQ · NSE · BSE · LSE · TSE · HKEX · SGX · ASX · Euronext · and more
  </div>
</div>""", unsafe_allow_html=True)

            # ── Live global search bar ────────────────────────────────────────
            gsrch_col, ggo_col = st.columns([5, 1])
            with gsrch_col:
                global_search = st.text_input(
                    "search",
                    placeholder="Search any stock: 'Apple', 'Reliance', 'TSMC', 'HDFC', 'Toyota', 'SAP'…",
                    label_visibility="collapsed",
                    key="global_search_input")
            with ggo_col:
                do_search = st.button("🔍 Search", key="global_search_btn", use_container_width=True)

            # Show live search results
            if global_search and len(global_search) >= 2:
                with st.spinner(f"Searching global markets for '{global_search}'…"):
                    search_results = _search_ticker(global_search.strip())
                if search_results:
                    st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:.5rem;'
                                f'letter-spacing:.15em;text-transform:uppercase;color:#4A3858;margin:.4rem 0 .3rem;">'
                                f'{len(search_results)} results</div>', unsafe_allow_html=True)
                    # Render result chips
                    sr_cols = st.columns(min(4, len(search_results)))
                    for sr_i, result in enumerate(search_results):
                        type_color = {"EQUITY":"#C084C8","ETF":"#4ade80","INDEX":"#F0C040",
                                      "CRYPTOCURRENCY":"#fb923c","MUTUALFUND":"#60a5fa"}.get(result["type"],"#9A8AAA")
                        with sr_cols[sr_i % 4]:
                            st.markdown(f"""
<div style="background:#120E1A;border:1px solid rgba(139,58,139,.25);border-radius:10px;
  padding:.55rem .75rem;cursor:pointer;transition:border-color .2s;margin-bottom:.3rem;">
  <div style="font-family:Space Mono,monospace;font-size:.62rem;font-weight:700;color:#C084C8;">{result['symbol']}</div>
  <div style="font-size:.68rem;color:#9A8AAA;margin:.1rem 0;line-height:1.3;">{result['name']}</div>
  <div style="display:flex;gap:.3rem;margin-top:.3rem;">
    <span style="font-family:Space Mono,monospace;font-size:.44rem;padding:.1rem .3rem;
      border-radius:3px;background:rgba(107,45,107,.15);color:#4A3858;">{result['exchange']}</span>
    <span style="font-family:Space Mono,monospace;font-size:.44rem;padding:.1rem .3rem;
      border-radius:3px;background:{type_color}18;color:{type_color};">{result['type']}</span>
  </div>
</div>""", unsafe_allow_html=True)
                            if st.button(f"Analyse {result['symbol']}", key=f"sr_go_{result['symbol']}_{sr_i}",
                                         use_container_width=True):
                                st.session_state["_dive_val"] = result["symbol"]
                                st.rerun()
                else:
                    st.caption("No results found. Try a different name or ticker suffix (e.g. .NS, .L, .T, .HK)")

            st.markdown('<hr style="border-color:rgba(139,58,139,.1);margin:.6rem 0;">', unsafe_allow_html=True)

            # ── Manual ticker entry ───────────────────────────────────────────
            st.markdown('<div style="font-family:Space Mono,monospace;font-size:.5rem;letter-spacing:.15em;'
                        'text-transform:uppercase;color:#4A3858;margin-bottom:.35rem;">Or enter ticker directly</div>',
                        unsafe_allow_html=True)
            dinp_col, dbtn_col = st.columns([5, 1])
            with dinp_col:
                dive_ticker = st.text_input("ticker",
                    placeholder="AAPL · INFY.NS · 700.HK · AZN.L · SAP.DE · 7203.T · BHP.AX · SHOP.TO",
                    label_visibility="collapsed", key="dive_ticker_input")
            with dbtn_col:
                run_dive = st.button("Analyse →", key="run_dive_btn", use_container_width=True)

            # ── Exchange suffix guide ─────────────────────────────────────────
            with st.expander("📖 Exchange Suffix Guide — How to type global tickers"):
                suffix_data = [
                    ("🇮🇳 India NSE",".NS","RELIANCE.NS, INFY.NS, TCS.NS"),
                    ("🇮🇳 India BSE",".BO","500325.BO, 500209.BO"),
                    ("🇬🇧 London LSE",".L","AZN.L, SHEL.L, HSBA.L"),
                    ("🇩🇪 Germany XETRA",".DE","SAP.DE, SIE.DE, BMW.DE"),
                    ("🇫🇷 France Euronext",".PA","MC.PA, OR.PA, TTE.PA"),
                    ("🇯🇵 Japan TSE",".T","7203.T, 6758.T, 9984.T"),
                    ("🇭🇰 Hong Kong HKEX",".HK","700.HK, 9988.HK, 1810.HK"),
                    ("🇦🇺 Australia ASX",".AX","BHP.AX, CBA.AX, CSL.AX"),
                    ("🇨🇦 Canada TSX",".TO","SHOP.TO, RY.TO, TD.TO"),
                    ("🇸🇬 Singapore SGX",".SI","D05.SI, O39.SI, Z74.SI"),
                    ("🇮🇹 Italy Euronext",".MI","ENI.MI, ISP.MI, ENEL.MI"),
                    ("🇪🇸 Spain BME",".MC","SAN.MC, BBVA.MC, ITX.MC"),
                    ("🇳🇱 Netherlands AEX",".AS","ASML.AS, HEIA.AS, PHIA.AS"),
                    ("🇸🇪 Sweden Nasdaq",".ST","ERIC-B.ST, VOLV-B.ST"),
                    ("🇳🇴 Norway Oslo",".OL","NHY.OL, DNB.OL, EQNR.OL"),
                    ("🇰🇷 South Korea KRX",".KS","005930.KS, 000660.KS"),
                    ("🇹🇼 Taiwan TWSE",".TW","2330.TW, 2317.TW"),
                    ("🇿🇦 South Africa JSE",".JO","NPN.JO, SOL.JO"),
                    ("🇧🇷 Brazil B3",".SA","PETR4.SA, VALE3.SA"),
                    ("🇺🇸 NYSE/NASDAQ","(none)","AAPL, TSLA, JPM, NVDA"),
                ]
                sc1, sc2 = st.columns(2)
                for i, (market, suffix, examples) in enumerate(suffix_data):
                    target = sc1 if i % 2 == 0 else sc2
                    with target:
                        st.markdown(f'<div style="display:flex;gap:.5rem;align-items:baseline;'
                                    f'font-family:Space Mono,monospace;font-size:.58rem;padding:.2rem 0;'
                                    f'border-bottom:1px solid rgba(139,58,139,.07);">'
                                    f'<span style="color:#C084C8;font-weight:700;min-width:28px;">{suffix}</span>'
                                    f'<span style="color:#9A8AAA;">{market}</span></div>'
                                    f'<div style="font-family:Space Mono,monospace;font-size:.46rem;'
                                    f'color:#4A3858;padding:.1rem 0 .3rem .5rem;">{examples}</div>',
                                    unsafe_allow_html=True)

            # ── World market quick-picks ─────────────────────────────────────
            st.markdown('<div style="font-family:Space Mono,monospace;font-size:.5rem;letter-spacing:.15em;'
                        'text-transform:uppercase;color:#4A3858;margin:.6rem 0 .3rem;">Quick-Pick by Market</div>',
                        unsafe_allow_html=True)
            for cat, tickers_list in POPULAR_STOCKS.items():
                with st.expander(cat):
                    qcols = st.columns(5 if len(tickers_list) >= 5 else len(tickers_list))
                    for idx_q, tk in enumerate(tickers_list):
                        with qcols[idx_q % 5]:
                            if st.button(tk, key=f"qp_{tk}", use_container_width=True):
                                st.session_state["_dive_val"] = tk; st.rerun()

            if "_dive_val" in st.session_state:
                dive_ticker=st.session_state.pop("_dive_val"); run_dive=True

            if dive_ticker:
                ticker_clean=dive_ticker.upper().strip()
                with st.spinner(f"📡 Loading {ticker_clean} — price, fundamentals, 1-year history…"):
                    info=_get_stock(ticker_clean)
                    st.session_state.portfolio_prices_cache[ticker_clean]=info

                if info.get("error"):
                    st.error(f"Could not fetch {ticker_clean}: {info['error']}")
                else:
                    tech=_calc_tech(info.get("hist"))
                    sig=_signal(info,tech)
                    cur=info.get("current_price") or 0
                    prev=info.get("prev_close") or cur
                    chg_pct=(cur-prev)/prev*100 if prev else 0
                    chg_cls="up" if chg_pct>=0 else "down"
                    sc=sig["color"]

                    # ── Header card ─────────────────────────────────────────
                    st.markdown(f"""
<div style="background:#120E1A;border:1px solid rgba(192,132,200,.3);border-radius:14px;
  padding:1rem 1.3rem;margin-bottom:.9rem;">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:.5rem;">
    <div>
      <div style="font-family:Space Mono,monospace;font-size:.75rem;font-weight:700;color:#C084C8;letter-spacing:.06em;">{ticker_clean}</div>
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.5rem;font-weight:300;color:#EDE8F5;margin:.1rem 0;">{info.get("name","")}</div>
      <div style="font-family:Space Mono,monospace;font-size:.55rem;color:#4A3858;">{info.get("sector","—")} · {(info.get("industry","—") or "—")[:35]} · {info.get("exchange","—")}</div>
    </div>
    <div style="text-align:right;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:2.2rem;font-weight:300;color:#EDE8F5;">{info.get("currency","$")} {cur:,.2f}</div>
      <div style="font-size:.62rem;color:{"#4ade80" if chg_pct>=0 else "#f87171"};">{"▲" if chg_pct>=0 else "▼"} {abs(chg_pct):.2f}% today</div>
      <div style="margin-top:.3rem;">
        <span class="signal-badge" style="background:{sc}22;border:1px solid {sc}55;color:{sc};">{sig["verdict"]} ({sig["score"]:+d})</span>
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

                    # ── Fundamentals grid ────────────────────────────────────
                    def _fc2(label,val):
                        return (f'<div class="fund-cell"><div class="fund-lbl">{label}</div>'
                                f'<div class="fund-val">{val}</div></div>')
                    pe_v=f'{info["pe_ratio"]:.1f}x' if info.get("pe_ratio") else "—"
                    fpe_v=f'{info["forward_pe"]:.1f}x' if info.get("forward_pe") else "—"
                    pb_v=f'{info["pb_ratio"]:.2f}x' if info.get("pb_ratio") else "—"
                    dy_v=f'{info["dividend_yield"]*100:.2f}%' if info.get("dividend_yield") else "—"
                    bet_v=f'{info["beta"]:.2f}' if info.get("beta") else "—"
                    roe_v=f'{info["roe"]*100:.1f}%' if info.get("roe") else "—"
                    roa_v=f'{info["roa"]*100:.1f}%' if info.get("roa") else "—"
                    gm_v=f'{info["gross_margin"]*100:.1f}%' if info.get("gross_margin") else "—"
                    nm_v=f'{info["profit_margin"]*100:.1f}%' if info.get("profit_margin") else "—"
                    rg_v=f'{info["revenue_growth"]*100:.1f}%' if info.get("revenue_growth") else "—"
                    eg_v=f'{info["earnings_growth"]*100:.1f}%' if info.get("earnings_growth") else "—"
                    tp_v=f'${info["target_price"]:.2f}' if info.get("target_price") else "—"
                    upside_v=(f'{(info["target_price"]/cur-1)*100:+.1f}%' if info.get("target_price") and cur else "—")
                    d2e_v=f'{info["debt_to_equity"]:.0f}%' if info.get("debt_to_equity") else "—"
                    cr_v=f'{info["current_ratio"]:.2f}' if info.get("current_ratio") else "—"
                    ar_v=info.get("analyst_rating") or "—"
                    mc_v=_fc(info.get("market_cap"))
                    st.markdown(f"""
<div class="fund-grid">
  {_fc2("Market Cap",mc_v)}{_fc2("P/E (TTM)",pe_v)}{_fc2("Fwd P/E",fpe_v)}
  {_fc2("P/B Ratio",pb_v)}{_fc2("Dividend Yield",dy_v)}{_fc2("Beta",bet_v)}
  {_fc2("ROE",roe_v)}{_fc2("ROA",roa_v)}{_fc2("Gross Margin",gm_v)}
  {_fc2("Net Margin",nm_v)}{_fc2("Rev Growth",rg_v)}{_fc2("EPS Growth",eg_v)}
  {_fc2("Analyst Target",tp_v)}{_fc2("Upside to Target",upside_v)}{_fc2("Analyst Rating",ar_v)}
  {_fc2("Debt/Equity",d2e_v)}{_fc2("Current Ratio",cr_v)}{_fc2("Free Cash Flow",_fc(info.get("free_cash_flow")))}
</div>""", unsafe_allow_html=True)

                    # ── 52-week range ────────────────────────────────────────
                    w52h=info.get("52w_high") or 0; w52l=info.get("52w_low") or 0
                    if w52h and w52l and cur:
                        pir=(cur-w52l)/(w52h-w52l+1e-9)*100
                        st.markdown(f"""
<div style="background:#120E1A;border:1px solid rgba(139,58,139,.18);border-radius:8px;padding:.65rem .9rem;margin-bottom:.6rem;">
  <div style="font-family:Space Mono,monospace;font-size:.5rem;letter-spacing:.15em;text-transform:uppercase;color:#4A3858;margin-bottom:.5rem;">52-Week Range</div>
  <div style="display:flex;align-items:center;gap:.7rem;">
    <span style="font-family:Space Mono,monospace;font-size:.6rem;color:#f87171;">${w52l:.2f}</span>
    <div style="flex:1;height:6px;background:rgba(139,58,139,.2);border-radius:3px;position:relative;">
      <div style="position:absolute;left:{pir:.0f}%;top:-5px;width:16px;height:16px;border-radius:50%;
        background:#C084C8;transform:translateX(-50%);border:2px solid #EDE8F5;box-shadow:0 0 8px rgba(192,132,200,.6);"></div>
    </div>
    <span style="font-family:Space Mono,monospace;font-size:.6rem;color:#4ade80;">${w52h:.2f}</span>
  </div>
  <div style="text-align:center;font-family:Space Mono,monospace;font-size:.52rem;color:#C084C8;margin-top:.4rem;">
    Current: ${cur:.2f} — {pir:.0f}% of range
  </div>
</div>""", unsafe_allow_html=True)

                    # ── Signal breakdown ──────────────────────────────────────
                    with st.expander("📡 Signal Breakdown"):
                        for sn,sd,sc_cat in sig["signals"]:
                            sc2=CHART_GREEN if sd=="+" else CHART_RED
                            st.markdown(f'<div style="display:flex;gap:.5rem;align-items:center;margin-bottom:.25rem;font-family:Space Mono,monospace;font-size:.6rem;">'
                                f'<span style="color:{sc2};font-weight:700;">{sd}</span>'
                                f'<span style="color:#EDE8F5;">{sn}</span>'
                                f'<span style="color:#4A3858;margin-left:auto;">{sc_cat}</span></div>',unsafe_allow_html=True)

                    # ── Technical section ─────────────────────────────────────
                    st.markdown("<hr style='border-color:rgba(139,58,139,.12);margin:.7rem 0;'>",unsafe_allow_html=True)
                    st.markdown('<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.18em;text-transform:uppercase;color:#C084C8;margin-bottom:.5rem;">Technical Analysis</div>',unsafe_allow_html=True)
                    if tech:
                        rc=st.columns(5)
                        for ci,(lbl,val) in enumerate([("1D",tech.get("ret_1d",0)),("1W",tech.get("ret_1w",0)),
                                ("1M",tech.get("ret_1m",0)),("3M",tech.get("ret_3m",0)),("1Y",tech.get("ret_1y",0))]):
                            rc[ci].metric(f"{lbl} Return",f"{val:+.2f}%")
                        tc=st.columns(4)
                        tc[0].metric("RSI (14)",f'{tech.get("rsi",0):.1f}')
                        tc[1].metric("RSI Signal",tech.get("rsi_signal","—"))
                        tc[2].metric("Ann. Volatility",f'{tech.get("ann_vol",0):.1f}%')
                        tc[3].metric("Sharpe Ratio",f'{tech.get("sharpe",0):.2f}')

                    # Charts
                    st.plotly_chart(_chart_candle(info,ticker_clean),use_container_width=True,config={"displayModeBar":False})
                    ch1,ch2=st.columns(2)
                    with ch1: st.plotly_chart(_chart_rsi(info,ticker_clean),use_container_width=True,config={"displayModeBar":False})
                    with ch2: st.plotly_chart(_chart_macd(info,ticker_clean),use_container_width=True,config={"displayModeBar":False})

                    if info.get("description"):
                        with st.expander("📋 Business Description"):
                            st.markdown(f'<div style="font-size:.8rem;color:#9A8AAA;line-height:1.8;">{info["description"]}…</div>',unsafe_allow_html=True)

                    # Add to portfolio
                    st.markdown("<hr style='border-color:rgba(139,58,139,.1);margin:.6rem 0;'>",unsafe_allow_html=True)
                    st.markdown('<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.18em;text-transform:uppercase;color:#C084C8;margin-bottom:.4rem;">Add to Portfolio</div>',unsafe_allow_html=True)
                    ac1,ac2,ac3=st.columns([2,2,1])
                    with ac1: shares_add=st.number_input("Shares",min_value=0.001,value=1.0,step=1.0,key=f"sa_{ticker_clean}")
                    with ac2: cost_add=st.number_input("Avg Cost ($)",min_value=0.01,value=float(cur) if cur else 1.0,step=0.01,key=f"ca_{ticker_clean}")
                    with ac3:
                        if st.button("➕ Add",use_container_width=True,key=f"add_{ticker_clean}"):
                            st.session_state.portfolio_holdings[ticker_clean]={"shares":shares_add,"avg_cost":cost_add,"name":info.get("name",ticker_clean)}
                            st.success(f"✓ {ticker_clean} added!"); st.rerun()

        # ── TAB 2: PERFORMANCE ─────────────────────────────────────────────
        with pfol_tabs[2]:
            all_tickers=list(st.session_state.portfolio_holdings.keys())+st.session_state.portfolio_watchlist
            if not all_tickers:
                st.info("Add holdings in ⚙️ Manage Holdings or search stocks in 🔎 Stock Deep-Dive.")
            else:
                st.markdown('<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.18em;text-transform:uppercase;color:#C084C8;margin-bottom:.6rem;">Normalised Performance vs Benchmarks</div>',unsafe_allow_html=True)
                pc1,pc2=st.columns([3,2])
                with pc1: bench=st.multiselect("Benchmarks",["SPY","QQQ","^NSEI","GLD","TLT"],default=["SPY"],key="bench_sel")
                with pc2: perf_period=st.selectbox("Period",["1mo","3mo","6mo","1y","2y"],index=3,key="perf_per")
                all_compare=tuple(set(all_tickers+bench))
                with st.spinner("Loading historical prices…"):
                    fig_perf=_chart_perf(all_compare,perf_period)
                st.plotly_chart(fig_perf,use_container_width=True,config={"displayModeBar":False})
                # Return summary table
                with st.spinner("Computing returns…"):
                    hd=_get_hist_multi(tuple(all_tickers),perf_period)
                ret_rows=[]
                for tk2,h2 in hd.items():
                    if h2 is None or h2.empty: continue
                    r1m=(h2.iloc[-1]/h2.iloc[-min(21,len(h2))]-1)*100
                    r3m=(h2.iloc[-1]/h2.iloc[-min(63,len(h2))]-1)*100
                    rall=(h2.iloc[-1]/h2.iloc[0]-1)*100
                    v2=h2.pct_change().dropna().std()*np.sqrt(252)*100
                    ret_rows.append({"Ticker":tk2,"1M Return":f"{r1m:+.2f}%","3M Return":f"{r3m:+.2f}%",
                        f"Total ({perf_period})":f"{rall:+.2f}%","Ann. Volatility":f"{v2:.1f}%"})
                if ret_rows: st.dataframe(pd.DataFrame(ret_rows),use_container_width=True,hide_index=True)

        # ── TAB 3: AI REPORT ──────────────────────────────────────────────
        with pfol_tabs[3]:
            st.markdown('<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.18em;text-transform:uppercase;color:#C084C8;margin-bottom:.6rem;">AI-Generated Portfolio Analysis Report</div>',unsafe_allow_html=True)
            if not GROQ_API_KEY:
                st.info("Enter Groq API key in sidebar to generate AI reports.")
            elif not st.session_state.portfolio_holdings:
                st.info("Add at least one holding in ⚙️ Manage Holdings first.")
            else:
                for tk3 in st.session_state.portfolio_holdings:
                    if tk3 not in st.session_state.portfolio_prices_cache:
                        st.session_state.portfolio_prices_cache[tk3]=_get_stock(tk3)
                m3=_pfol_metrics()
                ai_type=st.radio("Report type",[
                    "📊 Full Portfolio Analysis","⚠️ Risk Assessment",
                    "🎯 Rebalancing Suggestions","💡 Opportunity Scan"],
                    horizontal=True,key="ai_rpt_type")

                gen_btn=st.button("🤖 Generate AI Report",key="gen_report_btn",use_container_width=True)
                regen_btn=st.button("🔄 Regenerate",key="regen_btn") if st.session_state.portfolio_ai_report else False

                if st.session_state.portfolio_ai_report and not regen_btn:
                    st.markdown(f'<div class="ai-report">{st.session_state.portfolio_ai_report}</div>',unsafe_allow_html=True)
                elif gen_btn or regen_btn:
                    with st.spinner("Analysing portfolio with Llama 3.3-70B…"):
                        try:
                            from openai import OpenAI as _OAI2
                            _oai2=_OAI2(api_key=GROQ_API_KEY,base_url="https://api.groq.com/openai/v1")
                            pos_sum="\n".join(
                                f"  {p['ticker']} ({p['name'][:20]}): {p['shares']} shares @ ${p['avg_cost']:.2f} | "
                                f"Current ${p['current_price']:.2f} | P&L {p['pnl_pct']:+.1f}% | "
                                f"Weight {p['weight']:.1f}% | Sector {p['sector']}"
                                for p in m3["positions"])
                            fund_sum=""
                            for tk4 in st.session_state.portfolio_holdings:
                                i4=st.session_state.portfolio_prices_cache.get(tk4,{})
                                t4=_calc_tech(i4.get("hist")); s4=_signal(i4,t4)
                                roe4=f"{i4['roe']*100:.1f}%" if i4.get("roe") else "N/A"
                                mg4=f"{i4['profit_margin']*100:.1f}%" if i4.get("profit_margin") else "N/A"
                                fund_sum+=(f"\n{tk4}: P/E={i4.get('pe_ratio','—')}, "
                                    f"ROE={roe4}, Margin={mg4}, "
                                    f"Beta={i4.get('beta','—')}, Signal={s4['verdict']}, "
                                    f"Analyst={i4.get('analyst_rating','—')}")
                            prompts={
                                "📊 Full Portfolio Analysis":(
                                    f"Senior portfolio manager. Analyse:\n\nHOLDINGS:\n{pos_sum}\n\n"
                                    f"FUNDAMENTALS:{fund_sum}\n\nPortfolio Value: {_fc(m3['total_value'])} | "
                                    f"Return: {m3['total_pnl_pct']:+.2f}% | Beta: {m3['weighted_beta']:.2f}\n\n"
                                    f"Write 300-word analysis: composition quality, top/bottom performers, "
                                    f"risks, overall health rating (1-10), 3 specific recommendations. Cite numbers."),
                                "⚠️ Risk Assessment":(
                                    f"Risk officer. Holdings:\n{pos_sum}\nFundamentals:{fund_sum}\n"
                                    f"Beta: {m3['weighted_beta']:.2f}\n\n280-word risk report: "
                                    f"market risk, concentration risk, sector/correlation risk, "
                                    f"individual stock risks, hedging suggestions."),
                                "🎯 Rebalancing Suggestions":(
                                    f"Portfolio strategist. Holdings:\n{pos_sum}\nFundamentals:{fund_sum}\n\n"
                                    f"280-word rebalancing plan: overweight/underweight positions, "
                                    f"specific trades, sector gaps, tax-loss harvesting, target allocations."),
                                "💡 Opportunity Scan":(
                                    f"Growth analyst. Holdings:\n{pos_sum}\nFundamentals:{fund_sum}\n\n"
                                    f"280-word opportunity scan: existing positions with upside, "
                                    f"3-4 new stocks to add, underperformers to cut, "
                                    f"under-exposed themes, one high-conviction trade."),
                            }
                            resp4=_oai2.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[
                                    {"role":"system","content":"Expert portfolio manager and equity analyst. Be concise, data-driven, professional."},
                                    {"role":"user","content":prompts[ai_type]}],
                                temperature=0.2,max_tokens=800)
                            rpt=resp4.choices[0].message.content
                            st.session_state.portfolio_ai_report=rpt.replace("\n","<br>")
                            st.markdown(f'<div class="ai-report">{st.session_state.portfolio_ai_report}</div>',unsafe_allow_html=True)
                            st.caption(f"Generated by Llama 3.3-70B · {resp4.usage.total_tokens} tokens")
                        except Exception as e5:
                            st.error(f"AI Report error: {e5}")

        # ── TAB 4: MANAGE HOLDINGS ────────────────────────────────────────
        with pfol_tabs[4]:
            st.markdown('<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.18em;text-transform:uppercase;color:#C084C8;margin-bottom:.6rem;">Build Your Global Portfolio</div>',unsafe_allow_html=True)

            # Global search to add holding
            with st.expander("🔍 Search & Add from Any Global Exchange", expanded=not bool(st.session_state.portfolio_holdings)):
                st.markdown('<div style="font-family:Space Mono,monospace;font-size:.5rem;color:#4A3858;margin-bottom:.5rem;">'
                            'Search by company name or ticker from NYSE · NASDAQ · NSE · LSE · TSE · HKEX · ASX · Euronext · and 60+ more</div>',
                            unsafe_allow_html=True)
                mgsrch_col, mggo_col = st.columns([5,1])
                with mgsrch_col:
                    mg_search = st.text_input("search_add", placeholder="e.g. Reliance, Toyota, ASML, HDFC Bank, Samsung…",
                                              label_visibility="collapsed", key="mg_search_input")
                with mggo_col:
                    mg_do_search = st.button("Search", key="mg_search_btn", use_container_width=True)

                if mg_search and len(mg_search) >= 2:
                    with st.spinner("Searching…"):
                        mg_results = _search_ticker(mg_search.strip())
                    if mg_results:
                        for mg_r in mg_results[:8]:
                            type_c = {"EQUITY":"#C084C8","ETF":"#4ade80","INDEX":"#F0C040",
                                      "CRYPTOCURRENCY":"#fb923c"}.get(mg_r["type"],"#9A8AAA")
                            rr1,rr2,rr3,rr4,rr5 = st.columns([1.8,2.5,1.2,1.2,1])
                            rr1.markdown(f'<div style="font-family:Space Mono,monospace;font-size:.65rem;'
                                         f'font-weight:700;color:{type_c};padding-top:.45rem;">{mg_r["symbol"]}</div>',
                                         unsafe_allow_html=True)
                            rr2.markdown(f'<div style="font-size:.7rem;color:#9A8AAA;padding-top:.45rem;">'
                                         f'{mg_r["name"]} <span style="color:#4A3858;font-size:.55rem;">·{mg_r["exchange"]}</span></div>',
                                         unsafe_allow_html=True)
                            mg_sh = rr3.number_input("Sh", value=10.0, min_value=0.001, step=1.0,
                                                      key=f"mg_sh_{mg_r['symbol']}", label_visibility="collapsed")
                            mg_co = rr4.number_input("Cost", value=100.0, min_value=0.01, step=0.01,
                                                      key=f"mg_co_{mg_r['symbol']}", label_visibility="collapsed")
                            if rr5.button("＋", key=f"mg_add_{mg_r['symbol']}", use_container_width=True):
                                tk_add = mg_r["symbol"]
                                st.session_state.portfolio_holdings[tk_add] = {
                                    "shares": mg_sh, "avg_cost": mg_co, "name": mg_r["name"]}
                                if tk_add in st.session_state.portfolio_prices_cache:
                                    del st.session_state.portfolio_prices_cache[tk_add]
                                st.success(f"✓ Added {tk_add}"); st.rerun()
                    else:
                        st.caption("No results. Try a full company name or add exchange suffix (e.g. .NS .L .T .HK .DE).")

                # Direct ticker add
                st.markdown('<div style="font-family:Space Mono,monospace;font-size:.48rem;color:#4A3858;margin:.5rem 0 .3rem;">Or add directly by ticker:</div>',unsafe_allow_html=True)
                mg1, mg2, mg3, mg4 = st.columns([2, 1.5, 1.5, 1])
                with mg1: new_tk = st.text_input("Ticker", placeholder="AAPL · RELIANCE.NS · 700.HK · AZN.L", key="new_tk_input").upper().strip()
                with mg2: new_sh = st.number_input("Shares", min_value=0.001, value=10.0, step=1.0, key="new_sh")
                with mg3: new_co = st.number_input("Avg Cost", min_value=0.01, value=100.0, step=0.01, key="new_co")
                with mg4:
                    if st.button("Add", key="add_h_btn", use_container_width=True):
                        if new_tk:
                            st.session_state.portfolio_holdings[new_tk] = {"shares": new_sh, "avg_cost": new_co, "name": new_tk}
                            if new_tk in st.session_state.portfolio_prices_cache:
                                del st.session_state.portfolio_prices_cache[new_tk]
                            st.success(f"✓ Added {new_tk}"); st.rerun()
                        else: st.error("Enter a ticker symbol.")

            # Edit / remove existing holdings
            holdings_now = st.session_state.portfolio_holdings
            if holdings_now:
                st.markdown('<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.18em;text-transform:uppercase;color:#C084C8;margin:.6rem 0 .3rem;">Current Holdings</div>',unsafe_allow_html=True)
                for tk5, h5 in list(holdings_now.items()):
                    ec1, ec2, ec3, ec4, ec5 = st.columns([2, 1.5, 1.5, 1.5, 1])
                    _h_info = st.session_state.portfolio_prices_cache.get(tk5, {})
                    _h_name = (_h_info.get("name") or h5.get("name") or tk5)[:20]
                    ec1.markdown(f'<div style="font-family:Space Mono,monospace;font-size:.68rem;'
                                 f'color:#C084C8;padding-top:.55rem;font-weight:700;">{tk5}</div>'
                                 f'<div style="font-family:Syne,sans-serif;font-size:.6rem;color:#4A3858;">{_h_name}</div>',
                                 unsafe_allow_html=True)
                    ns5 = ec2.number_input("Sh", value=float(h5["shares"]), min_value=0.001, step=1.0,
                                           key=f"es_{tk5}", label_visibility="collapsed")
                    nc5 = ec3.number_input("Co", value=float(h5["avg_cost"]), min_value=0.01, step=0.01,
                                           key=f"ec_{tk5}", label_visibility="collapsed")
                    if ec4.button("Update", key=f"upd_{tk5}", use_container_width=True):
                        st.session_state.portfolio_holdings[tk5]["shares"] = ns5
                        st.session_state.portfolio_holdings[tk5]["avg_cost"] = nc5
                        if tk5 in st.session_state.portfolio_prices_cache:
                            del st.session_state.portfolio_prices_cache[tk5]
                        st.success(f"✓ Updated {tk5}"); st.rerun()
                    if ec5.button("🗑", key=f"del_{tk5}", use_container_width=True):
                        del st.session_state.portfolio_holdings[tk5]
                        if tk5 in st.session_state.portfolio_prices_cache:
                            del st.session_state.portfolio_prices_cache[tk5]
                        st.rerun()

            # Watchlist
            st.markdown("<hr style='border-color:rgba(139,58,139,.1);margin:.7rem 0;'>",unsafe_allow_html=True)
            st.markdown('<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.18em;text-transform:uppercase;color:#C084C8;margin-bottom:.35rem;">Watchlist</div>',unsafe_allow_html=True)
            wlc1, wlc2 = st.columns([5, 1])
            with wlc1:
                wl_tk = st.text_input("Watch", placeholder="Any ticker from any exchange…",
                                       label_visibility="collapsed", key="wl_inp").upper().strip()
            with wlc2:
                if st.button("Watch", key="wl_add", use_container_width=True):
                    if wl_tk and wl_tk not in st.session_state.portfolio_watchlist:
                        st.session_state.portfolio_watchlist.append(wl_tk); st.rerun()
            if st.session_state.portfolio_watchlist:
                wl_chips = " ".join(f'<span style="background:rgba(107,45,107,.15);border:1px solid rgba(139,58,139,.3);'
                                    f'font-family:Space Mono,monospace;font-size:.6rem;padding:.2rem .5rem;border-radius:4px;'
                                    f'color:#C084C8;">{t}</span>' for t in st.session_state.portfolio_watchlist)
                st.markdown(f'<div style="display:flex;gap:.3rem;flex-wrap:wrap;margin-bottom:.4rem;">{wl_chips}</div>',
                            unsafe_allow_html=True)
                if st.button("Clear Watchlist", key="wl_clear"):
                    st.session_state.portfolio_watchlist = []; st.rerun()

            st.markdown("<hr style='border-color:rgba(139,58,139,.08);margin:.7rem 0;'>",unsafe_allow_html=True)
            if st.button("🗑 Reset Entire Portfolio", key="reset_pfol", use_container_width=True):
                st.session_state.portfolio_holdings = {}
                st.session_state.portfolio_prices_cache = {}
                st.session_state.portfolio_watchlist = []
                st.session_state.portfolio_ai_report = ""
                st.rerun()

    st.markdown("<hr style='border-color:rgba(139,58,139,.1);margin:.6rem 0 1.2rem;'>",unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vfooter">
  <div class="vfooter-text">
    Built by Yash Chaudhary &nbsp;·&nbsp; Financial RAG Assistant v11 &nbsp;·&nbsp;
    Llama 3.3 × Groq × ChromaDB × FinBERT × yfinance · 60+ global exchanges
  </div>
</div>
""", unsafe_allow_html=True)
