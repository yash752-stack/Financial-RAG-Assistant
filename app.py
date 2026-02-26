from __future__ import annotations
"""
app.py  —  Financial RAG Assistant  v5
New features:
  ① Global search bar above all market indicators (sticky)
  ② Multi-format upload: PDF · XLSX · XLS · CSV · DOCX · TXT
  ③ Analytics auto-generated immediately after ingest
  ④ Doc vs Market comparison tab in Analytics Dashboard
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
    ("doc_full_text",   ""),
    ("auto_metrics",    []),       # v5: populated right after ingest
    ("auto_generated",  False),    # v5: banner flag
    ("search_query",    ""),       # v5: global search bar state
    ("search_results",  []),       # v5: search hits to display
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
# DESIGN SYSTEM  (Royal Velvet & Black)
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
.mood-idx-chip{display:flex;flex-direction:column;background:var(--card-2);
  border:1px solid var(--border);border-radius:8px;padding:.4rem .8rem;
  font-family:'Space Mono',monospace;min-width:90px}
.mood-idx-name{font-size:.52rem;color:var(--text-ghost);letter-spacing:.1em}
.mood-idx-val{font-size:.72rem;color:var(--text);margin-top:.1rem}
.mood-idx-chg.up{font-size:.56rem;color:#4ade80}
.mood-idx-chg.down{font-size:.56rem;color:#f87171}

/* ── PRICE CHIP ── */
.price-chip{display:flex;flex-direction:column;background:var(--card-2);
  border:1px solid var(--border);border-radius:10px;padding:.75rem 1rem;
  min-width:120px;font-family:'Space Mono',monospace;transition:border-color .2s}
.price-chip:hover{border-color:var(--border-l)}
.pc-sym{font-size:.6rem;color:var(--accent);font-weight:700;letter-spacing:.08em;white-space:nowrap}
.pc-name{font-size:.5rem;color:var(--text-ghost);margin-bottom:.2rem}
.pc-val{font-family:'Cormorant Garamond',serif;font-size:1.5rem;font-weight:300;
  color:var(--text);line-height:1}
.pc-chg.up{font-size:.58rem;color:#4ade80;margin-top:.1rem}
.pc-chg.down{font-size:.58rem;color:#f87171;margin-top:.1rem}
.pc-chg.flat{font-size:.58rem;color:var(--text-ghost);margin-top:.1rem}
.chips-row{display:flex;gap:.6rem;flex-wrap:wrap}

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
.upload-drawer{background:linear-gradient(135deg,rgba(107,45,107,.18) 0%,rgba(13,11,18,.95) 100%);
  border:1px solid rgba(139,58,139,.45);border-radius:12px;padding:1rem 1.1rem .7rem;margin-bottom:.6rem}
.upload-drawer-title{font-family:'Space Mono',monospace;font-size:.62rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--velvet-gl);margin-bottom:.6rem}
.src-card{background:var(--card);border:1px solid var(--border);border-left:3px solid var(--velvet-gl);
  border-radius:0 8px 8px 0;padding:.7rem .9rem;margin:.4rem 0;font-size:.82rem}
.src-name{font-family:'Space Mono',monospace;font-size:.7rem;color:var(--accent);margin-bottom:.15rem}
.src-score{font-family:'Space Mono',monospace;font-size:.62rem;color:var(--text-ghost)}
.src-preview{color:var(--text-dim);line-height:1.55;margin-top:.2rem}
.vfooter{text-align:center;padding:1.8rem 0 .5rem;position:relative;margin-top:2.5rem}
.vfooter::before{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);
  width:180px;height:1px;background:linear-gradient(90deg,transparent,rgba(107,45,107,.5),transparent)}
.vfooter-text{font-family:'Space Mono',monospace;font-size:.56rem;
  letter-spacing:.2em;text-transform:uppercase;color:var(--text-ghost)}

/* ════════════════════════════════════════════
   v5  NEW STYLES
   ════════════════════════════════════════════ */

/* ① Global search bar */
.gsearch-wrap{
  position:sticky;top:0;z-index:1000;
  background:linear-gradient(180deg,rgba(7,6,12,.97) 82%,transparent);
  backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  padding:.55rem 0 .3rem;margin-bottom:.9rem;
}
/* search result cards */
.sr-wrap{background:var(--card);border:1px solid var(--border);
  border-radius:10px;padding:.75rem 1rem;margin-bottom:.9rem}
.sr-title{font-family:'Space Mono',monospace;font-size:.52rem;letter-spacing:.18em;
  text-transform:uppercase;color:var(--accent);margin-bottom:.6rem}
.sr-hit{background:var(--card-2);border:1px solid var(--border);
  border-left:3px solid var(--accent);border-radius:0 8px 8px 0;
  padding:.55rem .9rem;margin-bottom:.4rem}
.sr-fname{font-family:'Space Mono',monospace;font-size:.56rem;color:var(--accent);margin-bottom:.18rem}
.sr-snippet{font-size:.79rem;color:var(--text-dim);line-height:1.55}

/* ③ Auto-analytics success banner */
.analytics-banner{
  background:linear-gradient(135deg,rgba(74,222,128,.07) 0%,rgba(107,45,107,.10) 100%);
  border:1px solid rgba(74,222,128,.22);border-radius:10px;
  padding:.7rem 1.1rem;margin-bottom:1rem;
  display:flex;align-items:flex-start;gap:.75rem;
}
.ab-icon{font-size:1.4rem;flex-shrink:0;line-height:1.2}
.ab-title{font-family:'Syne',sans-serif;font-size:.84rem;font-weight:600;color:#86efac;margin-bottom:.1rem}
.ab-sub{font-family:'Space Mono',monospace;font-size:.52rem;color:var(--text-ghost)}

/* ④ Comparison table */
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
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS ENGINE  (taxonomy, metrics, hybrid retriever, templates, eval)
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
# ④  DOC vs MARKET COMPARISON  (new Analytics sub-tab)
# ─────────────────────────────────────────────────────────────────────────────

# S&P 500 sector benchmark medians (2024 TTM, approximate)
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

def render_comparison_tab(metrics: list[dict], groq_api_key: str) -> None:
    if not metrics:
        st.markdown('<div style="text-align:center;padding:3rem 2rem;">'
                    '<div style="font-size:2.5rem;margin-bottom:1rem;opacity:.4;">📊</div>'
                    '<div style="font-family:\'Cormorant Garamond\',serif;font-size:1.5rem;'
                    'font-weight:300;font-style:italic;color:#4A3858;">'
                    'Upload &amp; ingest documents first — analytics auto-generate on ingest</div>'
                    '</div>', unsafe_allow_html=True)
        return

    def section_hdr(title: str, grad: str = "linear-gradient(180deg,#6B2D6B,#C084C8)") -> str:
        return (f'<div style="font-family:\'Cormorant Garamond\',serif;font-size:1.15rem;'
                f'font-weight:300;color:#EDE8F5;margin:.9rem 0 .5rem;'
                f'display:flex;align-items:center;gap:.5rem;">'
                f'<span style="display:inline-block;width:3px;height:1rem;'
                f'background:{grad};border-radius:2px;"></span>{title}</div>')

    # ── Section A: Margin comparison vs sector ──────────────────────────────
    st.markdown(section_hdr("Document Margins vs Sector Benchmarks"), unsafe_allow_html=True)

    pct_m = {m["label"]: m["value"] for m in metrics if m["unit"] == "%"}
    sectors = ["S&P 500 Avg","Technology","Financials","Energy","Healthcare",
               "Industrials","Consumer Discretionary","Consumer Staples"]
    sector_sel = st.selectbox("Compare against sector", sectors, index=0, key="cmp_sector")

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
        st.info("No comparable margin metrics found in this document (gross margin / net margin / operating margin / ROE / ROA).")

    st.markdown("<hr style='border-color:rgba(139,58,139,.12);margin:1.1rem 0;'>",
                unsafe_allow_html=True)

    # ── Section B: Live index snapshot ─────────────────────────────────────
    st.markdown(section_hdr("Live Market Context"), unsafe_allow_html=True)

    IDX_COMP = {"^GSPC":"S&P 500","^IXIC":"NASDAQ","^NSEI":"NIFTY 50","^N225":"Nikkei 225"}
    COMM_COMP = {"GC=F":("Gold","$/oz",2),"CL=F":("Crude Oil","$/bbl",2),"SI=F":("Silver","$/oz",3)}

    idx_q  = fetch_multi_quotes(tuple(IDX_COMP.keys()))
    comm_q = fetch_multi_quotes(tuple(COMM_COMP.keys()))

    ca, cb = st.columns(2)
    with ca:
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:.5rem;letter-spacing:.18em;'
                    'text-transform:uppercase;color:#4A3858;margin-bottom:.45rem;">Global Indices</div>',
                    unsafe_allow_html=True)
        chips = ""
        for sym, name in IDX_COMP.items():
            info = idx_q.get(sym)
            if info:
                arr = "▲" if info["pct"] >= 0 else "▼"
                cls = "up" if info["pct"] >= 0 else "down"
                chips += (f'<div class="mood-idx-chip" style="min-width:110px;">'
                          f'<div class="mood-idx-name">{name}</div>'
                          f'<div class="mood-idx-val">{info["price"]:,.0f}</div>'
                          f'<div class="mood-idx-chg {cls}">{arr} {abs(info["pct"]):.2f}%</div></div>')
        if chips:
            st.markdown(f'<div style="display:flex;gap:.6rem;flex-wrap:wrap;">{chips}</div>',
                        unsafe_allow_html=True)
    with cb:
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:.5rem;letter-spacing:.18em;'
                    'text-transform:uppercase;color:#4A3858;margin-bottom:.45rem;">Commodities</div>',
                    unsafe_allow_html=True)
        chips_c = ""
        for sym, (name, unit, dec) in COMM_COMP.items():
            info = comm_q.get(sym)
            if info:
                arr = "▲" if info["pct"] >= 0 else "▼"
                cls = "up" if info["pct"] >= 0 else "down"
                chips_c += (f'<div class="mood-idx-chip" style="min-width:110px;">'
                             f'<div class="mood-idx-name">{name}</div>'
                             f'<div class="mood-idx-val">${info["price"]:,.{dec}f}</div>'
                             f'<div class="mood-idx-chg {cls}">{arr} {abs(info["pct"]):.2f}%</div></div>')
        if chips_c:
            st.markdown(f'<div style="display:flex;gap:.6rem;flex-wrap:wrap;">{chips_c}</div>',
                        unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(139,58,139,.12);margin:1.1rem 0;'>",
                unsafe_allow_html=True)

    # ── Section C: Sector ETF performance ──────────────────────────────────
    st.markdown(section_hdr("Sector Performance (SPDR ETFs)",
                             "linear-gradient(180deg,#F0C040,#C084C8)"), unsafe_allow_html=True)
    etf_q = fetch_multi_quotes(tuple(SECTOR_ETFS.keys()))
    etf_rows = []
    for sym, name in SECTOR_ETFS.items():
        info = etf_q.get(sym)
        if info:
            etf_rows.append({"Sector":name,"ETF":sym,
                              "Price":f'${info["price"]:.2f}',
                              "1D Change":f'{info["pct"]:+.2f}%',
                              "_pct":info["pct"]})
    if etf_rows:
        df_etf = pd.DataFrame(etf_rows).sort_values("_pct", ascending=False).drop(columns=["_pct"])
        st.dataframe(df_etf, use_container_width=True, hide_index=True)

    st.markdown("<hr style='border-color:rgba(139,58,139,.12);margin:1.1rem 0;'>",
                unsafe_allow_html=True)

    # ── Section D: AI positioning commentary ───────────────────────────────
    st.markdown(section_hdr("AI Market Positioning Commentary",
                             "linear-gradient(180deg,#fb923c,#C084C8)"), unsafe_allow_html=True)

    if not groq_api_key:
        st.info("Enter Groq API key in the sidebar to generate AI commentary.")
    else:
        msummary = "; ".join(f"{m['label']}: {fmt_val(m['value'],m['unit'])}" for m in metrics[:12])
        isummary = "; ".join(f"{name}: {idx_q[s]['price']:,.0f} ({idx_q[s]['pct']:+.2f}%)"
                             for s, name in IDX_COMP.items() if s in idx_q)
        ssummary = "; ".join(f"{SECTOR_ETFS[s]}: {etf_q[s]['pct']:+.2f}%"
                             for s in SECTOR_ETFS if s in etf_q)

        if st.button("🤖  Generate Market Positioning Analysis", key="gen_cmp"):
            with st.spinner("Analysing document metrics against live market conditions…"):
                try:
                    from openai import OpenAI
                    oai = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
                    prompt = (
                        f"You are a senior equity analyst. Analyse the following:\n\n"
                        f"DOCUMENT METRICS: {msummary}\n\n"
                        f"LIVE MARKET DATA:\n"
                        f"- Global Indices: {isummary}\n"
                        f"- Sector ETF Performance Today: {ssummary}\n\n"
                        f"Write a 200-250 word analyst-style commentary covering:\n"
                        f"1. How this company's margins/ratios compare to the current market environment\n"
                        f"2. Whether valuation/performance is attractive given current macro backdrop\n"
                        f"3. Key sector tailwinds or headwinds visible in today's market data\n"
                        f"4. Positioning recommendation: Overweight / Neutral / Underweight — with brief rationale\n\n"
                        f"Be specific, cite numbers, be direct and concise."
                    )
                    resp = oai.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role":"system","content":"You are a senior equity analyst. Be concise, data-driven, and direct."},
                            {"role":"user","content":prompt},
                        ],
                        temperature=0.2, max_tokens=600,
                    )
                    commentary = resp.choices[0].message.content
                    st.markdown(
                        f'<div style="background:{VELVET["card2"]};border:1px solid rgba(139,58,139,.25);'
                        f'border-left:3px solid #C084C8;border-radius:0 10px 10px 0;'
                        f'padding:1rem 1.2rem;font-size:.88rem;color:#9A8AAA;line-height:1.8;">'
                        f'{commentary.replace(chr(10),"<br>")}</div>',
                        unsafe_allow_html=True,
                    )
                except Exception as e:
                    st.error(f"Error: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# FULL ANALYTICS TAB (all sub-tabs)
# ─────────────────────────────────────────────────────────────────────────────
def render_analytics_tab(vectorstore, groq_api_key, doc_full_text="", auto_metrics=None):
    if not vectorstore and not doc_full_text:
        st.markdown('<div style="text-align:center;padding:3rem 2rem;">'
                    '<div style="font-size:2.5rem;margin-bottom:1rem;opacity:.4;">📊</div>'
                    '<div style="font-family:\'Cormorant Garamond\',serif;font-size:1.5rem;'
                    'font-weight:300;font-style:italic;color:#4A3858;">'
                    'Upload documents to unlock analytics</div>'
                    '<div style="font-family:Syne,sans-serif;font-size:.8rem;color:#4A3858;'
                    'margin-top:.6rem;">Auto-extract metrics · Compare vs market · Templates · Benchmark</div>'
                    '</div>', unsafe_allow_html=True)
        return

    sub_tabs = st.tabs(["📊 Metrics Dashboard","📈 Doc vs Market","📋 Templates","🔍 Hybrid Search","🧪 Eval Benchmark"])

    # ── 0: Metrics ───────────────────────────────────────────────────────────
    with sub_tabs[0]:
        metrics = auto_metrics if auto_metrics else []
        if not metrics and doc_full_text:
            with st.spinner("Extracting metrics…"):
                metrics = extract_metrics(doc_full_text)
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:.54rem;letter-spacing:.18em;'
                    'text-transform:uppercase;color:#C084C8;margin-bottom:.8rem;">'
                    'Auto-Extracted Financial Metrics</div>', unsafe_allow_html=True)
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

    # ── 1: Doc vs Market (NEW) ───────────────────────────────────────────────
    with sub_tabs[1]:
        render_comparison_tab(auto_metrics or [], groq_api_key)

    # ── 2: Templates ─────────────────────────────────────────────────────────
    with sub_tabs[2]:
        cats = sorted({v["category"] for v in TEMPLATES.values()})
        chosen_cat = st.selectbox("Filter by category", ["All"]+cats, label_visibility="collapsed")
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
                    if st.button("Run Analysis →", key=f"tpl_{tn[:20]}", use_container_width=True):
                        st.session_state["_prefill"] = tm["prompt"]
                        st.success(f"✓ '{tn}' sent to chat ↓")

    # ── 3: Hybrid Search ─────────────────────────────────────────────────────
    with sub_tabs[3]:
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:.54rem;letter-spacing:.18em;'
                    'text-transform:uppercase;color:#C084C8;margin-bottom:.8rem;">'
                    'Hybrid BM25 + Dense Retrieval with Cross-Encoder Re-ranking</div>', unsafe_allow_html=True)
        hs_q = st.text_input("Search", placeholder="e.g. free cash flow capital expenditure 2023",
                             label_visibility="collapsed")
        c1, c2, c3 = st.columns(3)
        with c1: bw = st.slider("BM25 weight", 0.0, 1.0, 0.35, 0.05)
        with c2: tn = st.slider("Results", 3, 10, 5)
        with c3: uce = st.checkbox("Cross-encoder re-rank", value=True)
        tf = st.multiselect("Taxonomy filter", list(TAXONOMY.keys()), default=[], label_visibility="collapsed")
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
                        hits = HybridRetriever(cks, emb).retrieve(hs_q, qe, n=tn, bw=bw, rerank=uce)
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

    # ── 4: Eval Benchmark ────────────────────────────────────────────────────
    with sub_tabs[4]:
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:.54rem;letter-spacing:.18em;'
                    'text-transform:uppercase;color:#C084C8;margin-bottom:.8rem;">'
                    'FinanceBench-Style QA Accuracy Evaluation</div>', unsafe_allow_html=True)
        if st.button("▶  Run Benchmark"):
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
                with st.expander("📋 Full answers"):
                    for r in er:
                        st.markdown(f'<div style="background:{VELVET["card2"]};border:1px solid rgba(139,58,139,.2);'
                                    f'border-radius:8px;padding:.7rem .9rem;margin-bottom:.5rem;">'
                                    f'<div style="font-family:Space Mono,monospace;font-size:.58rem;'
                                    f'color:#C084C8;margin-bottom:.3rem;">{r["question"]}</div>'
                                    f'<div style="font-size:.8rem;color:#9A8AAA;">{r["answer"][:500]}</div>'
                                    f'<div style="font-family:Space Mono,monospace;font-size:.52rem;'
                                    f'color:#4A3858;margin-top:.3rem;">score:{r["score"]["score_pct"]}%</div>'
                                    f'</div>', unsafe_allow_html=True)

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
    arrow = "▲" if pct > 0.005 else ("▼" if pct < -0.005 else "●")
    cls   = "up" if pct > 0.005 else ("down" if pct < -0.005 else "flat")
    ih    = f'<span style="font-size:1rem;margin-right:.2rem;">{icon}</span>' if icon else ""
    return (f'<div class="price-chip"><div class="pc-sym">{ih}{sym}</div>'
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
# ② UNIVERSAL FILE TEXT EXTRACTOR  — PDF / XLSX / XLS / CSV / DOCX / TXT
# ─────────────────────────────────────────────────────────────────────────────
def extract_text_from_file(f) -> str:
    """Extract plain text from any supported file type."""
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

    # TXT / plain fallback
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return raw.decode(enc)
        except: pass
    return raw.decode("utf-8", errors="ignore")

# ─────────────────────────────────────────────────────────────────────────────
# ③ INGEST — multi-format + auto analytics on completion
# ─────────────────────────────────────────────────────────────────────────────
def ingest_documents(files):
    from chromadb import EphemeralClient
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    @st.cache_resource
    def load_model():
        return SentenceTransformer("all-MiniLM-L6-v2")

    model  = load_model()
    client = EphemeralClient(settings=Settings(anonymized_telemetry=False))
    try:   client.delete_collection("financials")
    except: pass
    col = client.create_collection("financials", metadata={"hnsw:space":"cosine"})

    all_chunks, all_ids, all_meta, fnames, full_texts = [], [], [], [], []
    prog = st.progress(0, text="Reading files…")

    for i, f in enumerate(files):
        text   = extract_text_from_file(f)   # ← universal extractor
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
        with st.spinner(f"Embedding {len(all_chunks)} chunks…"):
            embs = model.encode(all_chunks, normalize_embeddings=True).tolist()
            col.add(documents=all_chunks, embeddings=embs, ids=all_ids, metadatas=all_meta)

    combined_text = " ".join(full_texts)

    # ③  AUTO-GENERATE ANALYTICS immediately after embedding
    with st.spinner("Auto-generating analytics…"):
        auto_metrics = extract_metrics(combined_text)

    st.session_state.vectorstore    = {"collection":col,"model":model}
    st.session_state.uploaded_docs  = len(files)
    st.session_state.chunk_count    = len(all_chunks)
    st.session_state.file_names     = fnames
    st.session_state.doc_full_text  = combined_text
    st.session_state.auto_metrics   = auto_metrics
    st.session_state.auto_generated = True

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
        Financial Intelligence · v5
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
                      "doc_full_text","auto_metrics","auto_generated","search_query","search_results"]:
                st.session_state[k] = (None if k=="vectorstore" else
                                       [] if k in ["file_names","auto_metrics","search_results"] else
                                       0  if k in ["uploaded_docs","chunk_count"] else
                                       False if k=="auto_generated" else "")
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN TABS
# ─────────────────────────────────────────────────────────────────────────────
_main_tabs = st.tabs(["📈 Markets & Chat", "📊 Analytics Dashboard"])
with _main_tabs[0]:
    pass  # content below is at module level

# ─────────────────────────────────────────────────────────────────────────────
# ①  GLOBAL SEARCH BAR  — sticky, positioned ABOVE all market indicators
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="gsearch-wrap">', unsafe_allow_html=True)

_gs_col, _gc_col = st.columns([15, 1], gap="small")
with _gs_col:
    _raw_q = st.text_input(
        "global_search",
        value=st.session_state.search_query,
        placeholder="🔍  Search across your documents — try 'revenue 2023', 'risk factors', 'gross margin'…",
        label_visibility="collapsed",
        key="g_search_input",
    )
with _gc_col:
    if st.button("✕", key="g_clear", help="Clear search"):
        st.session_state.search_query = ""
        st.session_state.search_results = []
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# Run search when query changes
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
                hits.append({"filename":meta["filename"],
                              "score":round(1 - dist/2, 3),
                              "snippet":chunk[:300]})
        except: pass
    st.session_state.search_results = hits

# Display search results inline
if st.session_state.search_query and st.session_state.search_results:
    st.markdown(f'<div class="sr-wrap"><div class="sr-title">'
                f'◈ {len(st.session_state.search_results)} results for '
                f'"{_ht.escape(st.session_state.search_query)}"</div>',
                unsafe_allow_html=True)
    for hit in st.session_state.search_results:
        rel = int(hit["score"] * 100)
        bc2 = "#4ADE80" if rel >= 75 else ("#F0C040" if rel >= 50 else "#9A8AAA")
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
                f'padding:.4rem .7rem;background:rgba(107,45,107,.05);border:1px solid var(--border);'
                f'border-radius:8px;margin-bottom:.7rem;">'
                f'No document results for "{_ht.escape(st.session_state.search_query)}" — '
                f'upload documents to search them, or use the chat below for live market queries.'
                f'</div>', unsafe_allow_html=True)

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
    <span class="badge v">Semantic Retrieval</span>
    <span class="badge v">Source-backed Answers</span>
    <span class="badge v">Llama 3.3 · 70B</span>
    <span class="badge">Groq</span>
    <span class="badge g">Live Data</span>
    <span class="badge b">PDF · Excel · CSV · DOCX</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ③ AUTO-ANALYTICS BANNER (shown after ingest)
if st.session_state.auto_generated:
    n = len(st.session_state.auto_metrics)
    st.markdown(
        f'<div class="analytics-banner">'
        f'<div class="ab-icon">✅</div>'
        f'<div>'
        f'<div class="ab-title">Analytics auto-generated — {n} metric{"s" if n!=1 else ""} extracted</div>'
        f'<div class="ab-sub">Switch to 📊 Analytics Dashboard → Metrics Dashboard to view · '
        f'Compare vs market in Doc vs Market tab</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# STAT STRIP
# ─────────────────────────────────────────────────────────────────────────────
chunks = st.session_state.chunk_count
docs   = st.session_state.uploaded_docs
msgs   = len(st.session_state.messages) // 2
st.markdown(f"""
<div class="stat-strip">
  <div class="stat-cell"><div class="stat-lbl">Model</div>
    <div class="stat-val-mono">Llama 3.3 · 70B</div></div>
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
fng = fetch_fear_greed(); fng_val = fng["value"]; fng_label = fng["label"]
INDEX_SYMS = {"^GSPC":{"name":"S&P 500","flag":"🇺🇸"},"^IXIC":{"name":"NASDAQ","flag":"🇺🇸"},
              "^FTSE":{"name":"FTSE 100","flag":"🇬🇧"},"^NSEI":{"name":"NIFTY 50","flag":"🇮🇳"},
              "^N225":{"name":"Nikkei","flag":"🇯🇵"},"^GDAXI":{"name":"DAX","flag":"🇩🇪"}}
idx_quotes = fetch_multi_quotes(tuple(INDEX_SYMS.keys()))
idx_chips  = ""
for sym, meta in INDEX_SYMS.items():
    info = idx_quotes.get(sym)
    if info:
        arrow = "▲" if info["pct"] >= 0 else "▼"
        cls   = "up" if info["pct"] >= 0 else "down"
        idx_chips += (f'<div class="mood-idx-chip"><div class="mood-idx-name">{meta["flag"]} {meta["name"]}</div>'
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
            rate = info["price"]; pct = info["pct"]
            rs   = f"{rate:,.2f}" if rate >= 10 else f"{rate:.4f}"
            arr  = "▲" if pct > 0.005 else ("▼" if pct < -0.005 else "●")
            cls  = "up" if pct > 0.005 else ("down" if pct < -0.005 else "flat")
            fx_chips.append(f'<div class="price-chip"><div class="pc-sym">{meta["flag"]} {meta["label"]}</div>'
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
# CHAT SECTION
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="font-family:'Cormorant Garamond',serif;font-size:1.35rem;font-weight:300;
  color:#EDE8F5;margin:.5rem 0 .8rem;">
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
        Use <strong>＋</strong> to upload PDFs, Excel, CSV or DOCX for deep document analysis.
      </div>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander(f"↳ {len(msg['sources'])} source(s)"):
                for src in msg["sources"]:
                    st.markdown(f'<div class="src-card"><div class="src-name">📄 {src["filename"]}</div>'
                                f'<div class="src-score">relevance: {src["score"]}</div>'
                                f'<div class="src-preview">{src["preview"]}…</div></div>',
                                unsafe_allow_html=True)

# ② UPLOAD DRAWER  — now accepts PDF · XLSX · XLS · CSV · DOCX · TXT
if st.session_state.show_upload:
    st.markdown('<div class="upload-drawer">'
                '<div class="upload-drawer-title">◈ Upload Financial Documents</div>'
                '<div style="font-family:Space Mono,monospace;font-size:.52rem;color:#4A3858;margin-bottom:.6rem;">'
                'Supported: PDF · XLSX · XLS · CSV · DOCX · TXT</div>',
                unsafe_allow_html=True)
    inline_files = st.file_uploader(
        "Upload", type=["pdf","txt","xlsx","xls","csv","docx"],
        accept_multiple_files=True, label_visibility="collapsed", key="drawer_upload",
    )
    col_ing, col_cls = st.columns([3, 1])
    with col_ing:
        if inline_files and st.button("⬆  Ingest Documents", use_container_width=True, key="drawer_ingest"):
            if not GROQ_API_KEY:
                st.error("Enter your Groq API key in the sidebar first.")
            else:
                try:
                    n = ingest_documents(inline_files)
                    st.success(f"✓ {n} chunks from {len(inline_files)} file(s) · "
                               f"Analytics auto-generated — switch to 📊 Analytics tab")
                    st.session_state.show_upload = False
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    with col_cls:
        if st.button("✕ Close", use_container_width=True, key="drawer_close"):
            st.session_state.show_upload = False; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

bar_col1, bar_col2 = st.columns([1, 16], gap="small")
with bar_col1:
    if st.button("＋", key="plus_btn", use_container_width=True,
                 help="Upload PDF · Excel · CSV · DOCX · TXT"):
        st.session_state.show_upload = not st.session_state.show_upload; st.rerun()
with bar_col2:
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

                stock_lines = [f"  {sym}: ${info['price']:,.2f} ({'▲' if info['pct']>=0 else '▼'}{abs(info['pct']):.2f}%)"
                               for sym in symbols if (info := fetch_quote(sym))]
                comm_lines  = [f"  {name}: ${info['price']:,.{dec}f} {unit} ({'+' if info['pct']>=0 else ''}{info['pct']:.2f}%)"
                               for sym, (name, unit, _, dec) in COMMODITY_SYMS.items() if (info := fetch_quote(sym))]
                crypto_lines = [f"  {ticker}: ${info['price']:,.{dec}f} ({'+' if info['pct']>=0 else ''}{info['pct']:.2f}%)"
                                for sym, (name, ticker, _, dec) in CRYPTO_SYMS.items() if (info := fetch_quote(sym))]
                fx_lines = []
                for _fxsym in st.session_state.get("fx_select_syms", ("USDINR=X","USDJPY=X","USDCNY=X")):
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
                    f"MARKET MOOD: Fear & Greed = {fng_val} ({fng_label})"
                ).strip()

                doc_context = ""; sources_data = []
                if st.session_state.vectorstore:
                    vs    = st.session_state.vectorstore
                    q_emb = vs["model"].encode([q], normalize_embeddings=True).tolist()
                    res   = vs["collection"].query(query_embeddings=q_emb, n_results=5,
                                                   include=["documents","metadatas","distances"])
                    cks, mts, dts = res["documents"][0], res["metadatas"][0], res["distances"][0]
                    doc_context  = "\n---\n".join(f"[{m['filename']}]\n{c}" for c, m in zip(cks, mts))
                    sources_data = [{"filename":m["filename"],"score":round(1-d/2,3),"preview":c[:220]}
                                    for c, m, d in zip(cks, mts, dts)]

                user_msg = (f"{live_context}\n\n=== DOCUMENT CONTEXT ===\n{doc_context}\n\nQuestion: {q}"
                            if doc_context else f"{live_context}\n\nQuestion: {q}")

                resp = oai.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role":"system","content":(
                            "You are an expert financial analyst with real-time data access. "
                            "You have live prices for stocks, gold, silver, oil, crypto, and FX rates. "
                            "Use live data for market questions. For document questions, cite specific numbers. "
                            "Be concise, precise, never fabricate numbers.")},
                        *[{"role":m["role"],"content":m["content"]} for m in st.session_state.messages[:-1]],
                        {"role":"user","content":user_msg},
                    ],
                    temperature=0.15, max_tokens=1500,
                )
                answer = resp.choices[0].message.content
                tokens = resp.usage.total_tokens
                st.markdown(answer)

                if sources_data:
                    with st.expander(f"↳ {len(sources_data)} document source(s)"):
                        for src in sources_data:
                            st.markdown(f'<div class="src-card"><div class="src-name">📄 {src["filename"]}</div>'
                                        f'<div class="src-score">relevance: {src["score"]}</div>'
                                        f'<div class="src-preview">{src["preview"]}…</div></div>',
                                        unsafe_allow_html=True)
                st.caption(f"llama-3.3-70b-versatile · {tokens} tokens · live data injected")
                st.session_state.messages.append({"role":"assistant","content":answer,"sources":sources_data})
            except Exception as e:
                st.error(f"Error: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS TAB
# ─────────────────────────────────────────────────────────────────────────────
with _main_tabs[1]:
    render_analytics_tab(
        vectorstore   = st.session_state.get("vectorstore"),
        groq_api_key  = GROQ_API_KEY,
        doc_full_text = st.session_state.get("doc_full_text",""),
        auto_metrics  = st.session_state.get("auto_metrics", []),
    )

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vfooter">
  <div class="vfooter-text">
    Built by Yash Chaudhary &nbsp;·&nbsp; Financial RAG Assistant v5 &nbsp;·&nbsp;
    Llama 3.3 × Groq × ChromaDB
  </div>
</div>
""", unsafe_allow_html=True)
