from __future__ import annotations
"""
app.py — Financial RAG Assistant v5
Royal Velvet & Black Theme | All 8 feature sets + UI/UX overhaul
"""

import os
import re
import json
import math
import datetime as _dt
import threading as _threading
import time as _time
import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Financial RAG Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Syne:wght@400;500;600;700&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

:root {
  --black:      #07060C;
  --card:       #0D0B12;
  --card2:      #120E1A;
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
  --blue:       #60A5FA;
}

#MainMenu,footer,header,[data-testid="stToolbar"],
[data-testid="stDecoration"],.stDeployButton{display:none!important}

*,*::before,*::after{box-sizing:border-box}
html,body,[class*="css"]{font-family:'Syne',sans-serif!important;color:var(--text)!important}

.stApp,[data-testid="stAppViewContainer"]{
  background:
    radial-gradient(ellipse 110% 55% at 0% 0%,rgba(107,45,107,.20) 0%,transparent 55%),
    radial-gradient(ellipse  80% 50% at 100% 100%,rgba(107,45,107,.14) 0%,transparent 55%),
    var(--black)!important;
}
[data-testid="stMain"],[data-testid="block-container"]{
  background:transparent!important;padding-top:0!important;max-width:1180px!important;
}
[data-testid="stSidebar"]{
  background:var(--panel)!important;
  border-right:1px solid var(--border-l)!important;
  box-shadow:4px 0 40px rgba(107,45,107,.08)!important;
}
[data-testid="stSidebar"]>div{padding:1.2rem 1.0rem!important}

h1,h2,h3,h4{font-family:'Cormorant Garamond',serif!important;color:var(--text)!important}
code,pre{font-family:'Space Mono',monospace!important}

[data-testid="stMetric"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:8px!important;padding:.9rem 1rem!important}
[data-testid="stMetricLabel"] p{font-family:'Space Mono',monospace!important;font-size:.58rem!important;color:var(--text-ghost)!important;text-transform:uppercase!important;letter-spacing:.18em!important}
[data-testid="stMetricValue"]{font-family:'Cormorant Garamond',serif!important;font-size:1.7rem!important;font-weight:300!important;color:var(--accent)!important}

.stButton>button{background:transparent!important;border:1px solid var(--border)!important;border-radius:6px!important;color:var(--text-dim)!important;font-family:'Syne',sans-serif!important;font-size:.8rem!important;transition:all .22s ease!important;text-align:left!important}
.stButton>button:hover{background:rgba(107,45,107,.14)!important;border-color:var(--velvet-gl)!important;color:var(--accent)!important;box-shadow:0 0 18px rgba(107,45,107,.22)!important;transform:translateY(-1px)!important}

.stTextInput input,.stTextArea textarea{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:8px!important;color:var(--text)!important}
[data-testid="stChatInput"]{background:var(--card2)!important;border:1px solid var(--border-l)!important;border-radius:14px!important;box-shadow:0 0 30px rgba(107,45,107,.12)!important}
[data-testid="stChatInput"] textarea{background:transparent!important;border:none!important;color:var(--text)!important}
[data-testid="stChatInput"]:focus-within{border-color:rgba(139,58,139,.7)!important}
[data-testid="stChatMessage"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:12px!important;padding:.8rem 1rem!important;margin-bottom:.5rem!important}
[data-testid="stFileUploader"]{background:rgba(107,45,107,.05)!important;border:1.5px dashed rgba(139,58,139,.4)!important;border-radius:10px!important}
[data-testid="stExpander"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:8px!important}
[data-testid="stAlert"]{background:rgba(107,45,107,.1)!important;border:1px solid var(--border-l)!important;border-radius:8px!important}
div[data-testid="stSuccess"]{background:rgba(74,222,128,.07)!important}
div[data-testid="stError"]{background:rgba(248,113,113,.07)!important}
.stProgress>div>div{background:linear-gradient(90deg,var(--velvet),var(--accent))!important}
[data-testid="stMultiSelect"]>div{background:var(--card)!important;border-color:var(--border)!important;border-radius:8px!important}
.stMultiSelect span[data-baseweb="tag"]{background:rgba(107,45,107,.3)!important;border:1px solid var(--velvet-gl)!important;color:var(--lilac)!important;border-radius:999px!important}
[data-testid="stSelectbox"]>div>div{background:var(--card)!important;border-color:var(--border)!important;border-radius:8px!important}
[data-testid="stTabs"] [data-baseweb="tab-list"]{background:var(--card)!important;border-radius:10px!important;padding:.2rem!important;border:1px solid var(--border)!important}
[data-testid="stTabs"] [data-baseweb="tab"]{color:var(--text-ghost)!important;font-family:'Space Mono',monospace!important;font-size:.65rem!important;letter-spacing:.1em!important}
[data-testid="stTabs"] [aria-selected="true"]{background:rgba(107,45,107,.25)!important;color:var(--accent)!important;border-radius:8px!important}
hr{border-color:var(--border)!important}
::-webkit-scrollbar{width:3px}
::-webkit-scrollbar-thumb{background:rgba(107,45,107,.35);border-radius:2px}

[data-testid="collapsedControl"]{background:rgba(107,45,107,.18)!important;border:1px solid rgba(139,58,139,.45)!important;border-radius:8px!important;color:#C084C8!important}
[data-testid="collapsedControl"]:hover{background:rgba(107,45,107,.35)!important}

/* ── STICKY CHAT BAR ── */
.sticky-chat-wrap{
  position:sticky;top:0;z-index:100;
  background:linear-gradient(180deg,rgba(7,6,12,.98) 80%,transparent);
  padding:.6rem 0 .4rem;
  margin:0 0 .8rem;
}

/* ── SECTION PANELS ── */
.v-panel{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.1rem 1.4rem;margin-bottom:1.2rem;position:relative;overflow:hidden}
.v-panel-title{font-family:'Cormorant Garamond',serif;font-size:1.1rem;font-weight:300;color:var(--text);margin-bottom:.8rem;display:flex;align-items:center;gap:.5rem}
.v-panel-title::before{content:'';display:inline-block;width:3px;height:1.1rem;background:linear-gradient(180deg,var(--velvet),var(--accent));border-radius:2px}

/* ── HERO ── */
.rag-header{position:relative;padding:1.6rem 2rem;background:linear-gradient(135deg,rgba(107,45,107,.22) 0%,rgba(13,11,18,.98) 55%,rgba(107,45,107,.12) 100%);border:1px solid rgba(255,255,255,.08);border-radius:18px;box-shadow:0 8px 40px rgba(0,0,0,.4);margin-bottom:1rem;overflow:hidden}
.rag-header::before{content:'';position:absolute;top:-80px;right:-80px;width:280px;height:280px;border-radius:50%;background:radial-gradient(circle,rgba(107,45,107,.25) 0%,transparent 70%);pointer-events:none}
.rag-header::after{content:'';position:absolute;bottom:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent 0%,rgba(107,45,107,.6) 30%,rgba(192,132,200,.8) 50%,rgba(107,45,107,.6) 70%,transparent 100%)}
.rag-kicker{font-family:'Space Mono',monospace;font-size:.58rem;letter-spacing:.28em;color:var(--velvet-gl);text-transform:uppercase;margin-bottom:.6rem;display:flex;align-items:center;gap:.5rem}
.rag-kicker::before{content:'';display:inline-block;width:16px;height:1px;background:var(--velvet-gl);opacity:.6}
.rag-header h1{font-family:'Cormorant Garamond',serif!important;font-size:2.6rem!important;font-weight:300!important;line-height:1.05!important;color:var(--text)!important;margin:0 0 .15rem!important;letter-spacing:-.02em!important}
.rag-header h1 em{font-style:italic;background:linear-gradient(135deg,var(--velvet-gl) 0%,var(--accent) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.rag-header p{font-size:.84rem;color:var(--text-dim);margin:.5rem 0 0!important;max-width:460px}
.badge-row{display:flex;gap:.35rem;margin-top:.75rem;flex-wrap:wrap}
.badge{font-family:'Space Mono',monospace;font-size:.58rem;letter-spacing:.06em;padding:.18rem .5rem;border-radius:999px;border:1px solid var(--border);color:var(--text-ghost);background:rgba(255,255,255,.04)}
.badge.v{border-color:rgba(139,58,139,.5);color:var(--accent);background:rgba(107,45,107,.12)}
.badge.g{border-color:rgba(74,222,128,.3);color:#86efac;background:rgba(74,222,128,.07)}

/* ── STAT STRIP ── */
.stat-strip{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:rgba(107,45,107,.22);border-radius:10px;overflow:hidden;border:1px solid rgba(107,45,107,.22);margin-bottom:1rem}
.stat-cell{background:var(--card);padding:.85rem 1rem;position:relative;transition:background .25s}
.stat-cell:hover{background:var(--card2)}
.stat-cell::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--velvet),var(--accent));opacity:0;transition:opacity .25s}
.stat-cell:hover::before{opacity:1}
.stat-lbl{font-family:'Space Mono',monospace;font-size:.5rem;letter-spacing:.2em;text-transform:uppercase;color:var(--text-ghost);margin-bottom:.35rem}
.stat-val{font-family:'Cormorant Garamond',serif;font-size:1.55rem;font-weight:300;color:var(--text);line-height:1}
.stat-val.active{color:var(--accent)}
.stat-val-mono{font-family:'Space Mono',monospace;font-size:.62rem;color:var(--accent);line-height:1.4}

/* ── PRICE CHIP ── */
.price-chip{display:flex;flex-direction:column;background:var(--card2);border:1px solid var(--border);border-radius:10px;padding:.7rem .9rem;min-width:110px;font-family:'Space Mono',monospace;transition:border-color .2s}
.price-chip:hover{border-color:var(--border-l)}
.pc-sym{font-size:.58rem;color:var(--accent);font-weight:700;letter-spacing:.06em;white-space:nowrap}
.pc-name{font-size:.48rem;color:var(--text-ghost);margin-bottom:.15rem}
.pc-val{font-family:'Cormorant Garamond',serif;font-size:1.45rem;font-weight:300;color:var(--text);line-height:1}
.pc-chg.up{font-size:.56rem;color:#4ade80;margin-top:.08rem}
.pc-chg.down{font-size:.56rem;color:#f87171;margin-top:.08rem}
.pc-chg.flat{font-size:.56rem;color:var(--text-ghost);margin-top:.08rem}
.chips-row{display:flex;gap:.5rem;flex-wrap:wrap}

/* ── MOOD BAR ── */
.mood-bar-wrap{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:.9rem 1.2rem;margin-bottom:1rem}
.mood-title{font-family:'Space Mono',monospace;font-size:.56rem;letter-spacing:.2em;text-transform:uppercase;color:var(--velvet-gl);margin-bottom:.6rem}
.mood-track{height:5px;border-radius:3px;background:linear-gradient(90deg,#f87171 0%,#fb923c 25%,#facc15 50%,#86efac 75%,#4ade80 100%);position:relative;margin-bottom:.45rem}
.mood-needle{position:absolute;top:-5px;width:15px;height:15px;border-radius:50%;border:2px solid #fff;background:var(--accent);transform:translateX(-50%);box-shadow:0 0 8px rgba(192,132,200,.6)}
.mood-labels{display:flex;justify-content:space-between;font-family:'Space Mono',monospace;font-size:.46rem;color:var(--text-ghost)}
.mood-index{font-family:'Cormorant Garamond',serif;font-size:1.9rem;font-weight:300}
.mood-indices{display:flex;gap:.8rem;margin-top:.7rem;flex-wrap:wrap}
.mood-idx-chip{display:flex;flex-direction:column;background:var(--card2);border:1px solid var(--border);border-radius:8px;padding:.4rem .75rem;font-family:'Space Mono',monospace;min-width:85px}
.mood-idx-name{font-size:.5rem;color:var(--text-ghost);letter-spacing:.08em}
.mood-idx-val{font-size:.68rem;color:var(--text);margin-top:.08rem}
.mood-idx-chg.up{font-size:.54rem;color:#4ade80}
.mood-idx-chg.down{font-size:.54rem;color:#f87171}

/* ── FX / COMM / CRYPTO PANELS ── */
.fx-panel,.comm-panel,.crypto-panel{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1rem 1.2rem .85rem;margin-bottom:1rem}

/* ── SIDEBAR LABELS ── */
.sb-lbl{font-family:'Space Mono',monospace;font-size:.52rem;letter-spacing:.2em;text-transform:uppercase;color:var(--velvet-gl);padding:1rem 0 .4rem;border-top:1px solid var(--border);margin-top:.4rem}
.key-ok{display:flex;align-items:center;gap:.45rem;background:rgba(74,222,128,.07);border:1px solid rgba(74,222,128,.2);color:#86efac;padding:.35rem .65rem;border-radius:6px;font-family:'Space Mono',monospace;font-size:.58rem}
.key-dot{width:5px;height:5px;border-radius:50%;background:#4ade80;box-shadow:0 0 6px #4ade80;animation:blink 2s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
.doc-pill{display:flex;align-items:center;justify-content:space-between;gap:.4rem;background:rgba(107,45,107,.1);border:1px solid var(--border);padding:.3rem .6rem;border-radius:4px;margin-bottom:.25rem;font-family:'Space Mono',monospace;font-size:.56rem;color:var(--text-dim);cursor:pointer;transition:all .18s}
.doc-pill:hover{border-color:var(--velvet-gl);color:var(--accent)}
.doc-dot{width:4px;height:4px;border-radius:50%;background:var(--velvet-gl);flex-shrink:0}
.doc-pill.active-doc{border-color:var(--accent);color:var(--accent);background:rgba(192,132,200,.1)}

/* ── CHAT SECTION ── */
.empty{text-align:center;padding:3rem 2rem}
.empty-orb{width:90px;height:90px;border-radius:50%;background:radial-gradient(circle,rgba(107,45,107,.28) 0%,transparent 70%);border:1px solid var(--border);margin:0 auto 1.2rem;display:flex;align-items:center;justify-content:center;font-size:1.8rem;color:var(--velvet-gl)}
.empty-title{font-family:'Cormorant Garamond',serif;font-size:1.6rem;font-weight:300;font-style:italic;color:var(--text-ghost);margin-bottom:.45rem}
.empty-sub{font-size:.78rem;color:var(--text-ghost);max-width:290px;margin:0 auto;line-height:1.8;opacity:.7}

/* ── UPLOAD DRAWER ── */
.upload-drawer{background:linear-gradient(135deg,rgba(107,45,107,.18) 0%,rgba(13,11,18,.95) 100%);border:1px solid rgba(139,58,139,.45);border-radius:12px;padding:.9rem 1rem .65rem;margin-bottom:.5rem}
.upload-drawer-title{font-family:'Space Mono',monospace;font-size:.6rem;letter-spacing:.14em;text-transform:uppercase;color:var(--velvet-gl);margin-bottom:.55rem}

/* ── SOURCE CARDS ── */
.src-card{background:var(--card);border:1px solid var(--border);border-left:3px solid var(--velvet-gl);border-radius:0 8px 8px 0;padding:.65rem .85rem;margin:.35rem 0;font-size:.82rem}
.src-name{font-family:'Space Mono',monospace;font-size:.68rem;color:var(--accent);margin-bottom:.12rem}
.src-score{font-family:'Space Mono',monospace;font-size:.6rem;color:var(--text-ghost)}
.src-bar{height:3px;border-radius:2px;margin:.2rem 0 .3rem;transition:width .5s}
.src-preview{color:var(--text-dim);line-height:1.5;margin-top:.18rem;font-size:.8rem}

/* ── QUICK NAV BUTTONS ── */
.qnav-row{display:flex;gap:.4rem;flex-wrap:wrap;margin:.5rem 0}
.qnav-btn{font-family:'Space Mono',monospace;font-size:.56rem;letter-spacing:.08em;padding:.28rem .7rem;border:1px solid rgba(139,58,139,.35);border-radius:999px;background:rgba(107,45,107,.1);color:var(--text-dim);cursor:pointer;transition:all .18s;white-space:nowrap}
.qnav-btn:hover{border-color:var(--accent);color:var(--accent);background:rgba(192,132,200,.12)}

/* ── ANALYTICS CARDS ── */
.m-card{background:var(--card2);border:1px solid var(--border);border-radius:10px;padding:.75rem .9rem;position:relative}
.m-card-lbl{font-family:'Space Mono',monospace;font-size:.5rem;letter-spacing:.14em;text-transform:uppercase;color:var(--text-ghost);margin-bottom:.3rem}
.m-card-val{font-family:'Cormorant Garamond',serif;font-size:1.55rem;font-weight:300;color:var(--text);line-height:1}
.m-card-cat{font-family:'Space Mono',monospace;font-size:.44rem;text-transform:uppercase;letter-spacing:.1em;margin-top:.25rem}
.tpl-card{background:var(--card2);border:1px solid rgba(139,58,139,.22);border-radius:10px;padding:.75rem .85rem .6rem;transition:all .2s}
.tpl-card:hover{border-color:var(--velvet-gl);box-shadow:0 0 20px rgba(107,45,107,.15)}

/* ── FOOTER ── */
.vfooter{text-align:center;padding:1.5rem 0 .4rem;position:relative;margin-top:2rem}
.vfooter::before{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);width:160px;height:1px;background:linear-gradient(90deg,transparent,rgba(107,45,107,.5),transparent)}
.vfooter-text{font-family:'Space Mono',monospace;font-size:.52rem;letter-spacing:.18em;text-transform:uppercase;color:var(--text-ghost)}

/* ── CHANGE 2: Sticky chat icon bar at very top of page ── */
.chat-fab-bar{
  position:sticky;top:0;z-index:999;
  display:flex;align-items:center;gap:.7rem;
  padding:.4rem 1.1rem;
  background:linear-gradient(180deg,rgba(7,6,12,.97) 0%,rgba(7,6,12,.92) 82%,transparent 100%);
  backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  border-bottom:1px solid rgba(139,58,139,.2);
  margin:0 -1.5rem .5rem;
}
.chat-fab-icon{
  width:30px;height:30px;border-radius:50%;flex-shrink:0;
  background:linear-gradient(135deg,rgba(107,45,107,.6),rgba(192,132,200,.3));
  border:1px solid rgba(192,132,200,.5);
  display:flex;align-items:center;justify-content:center;
  font-size:.95rem;
  box-shadow:0 0 12px rgba(107,45,107,.4);
  cursor:pointer;transition:transform .2s,box-shadow .2s;
}
.chat-fab-icon:hover{transform:scale(1.1);box-shadow:0 0 20px rgba(107,45,107,.6);}
.chat-fab-label{font-family:'Space Mono',monospace;font-size:.56rem;letter-spacing:.18em;text-transform:uppercase;color:var(--velvet-gl);}
.chat-fab-sep{width:1px;height:14px;background:rgba(139,58,139,.3);flex-shrink:0;}
.chat-fab-model{font-family:'Space Mono',monospace;font-size:.5rem;color:rgba(192,132,200,.7);}
.chat-fab-status{font-family:'Space Mono',monospace;font-size:.48rem;color:var(--text-ghost);margin-left:auto;}
.chat-fab-live{width:5px;height:5px;border-radius:50%;background:#4ade80;box-shadow:0 0 5px #4ade80;flex-shrink:0;animation:fab-blink 2.5s infinite;}
@keyframes fab-blink{0%,100%{opacity:1;transform:scale(1);}50%{opacity:.4;transform:scale(.8);}}
/* FinBERT badge */
.badge.fb{border-color:rgba(240,192,64,.5)!important;color:var(--gold)!important;background:rgba(240,192,64,.08)!important;}

/* ── CHANGE 3: Inline analytics panel below chat ── */
.analytics-inline{
  background:linear-gradient(135deg,rgba(107,45,107,.10) 0%,rgba(13,11,18,.98) 100%);
  border:1px solid rgba(139,58,139,.32);
  border-top:2px solid var(--accent);
  border-radius:14px;
  padding:1.2rem 1.4rem 1rem;
  margin-top:1.8rem;margin-bottom:1rem;
}
.analytics-inline-title{
  font-family:'Cormorant Garamond',serif;font-size:1.3rem;font-weight:300;
  color:var(--text);display:flex;align-items:center;gap:.5rem;margin-bottom:.9rem;
}
.analytics-inline-title::before{
  content:'';display:inline-block;width:3px;height:1.3rem;
  background:linear-gradient(180deg,var(--velvet),var(--accent));border-radius:2px;
}
.src-rel-bar{height:3px;border-radius:2px;margin:.2rem 0 .3rem;}

/* ── RESPONSIVE ── */
@media(max-width:1024px){[data-testid="block-container"]{padding:0 1rem!important}.stat-strip{grid-template-columns:repeat(3,1fr)!important}}
@media(max-width:767px){[data-testid="block-container"]{padding:0 .5rem!important;max-width:100%!important}.stat-strip{grid-template-columns:repeat(2,1fr)!important}.rag-header h1{font-size:2rem!important}}
@media(max-width:479px){.stat-strip{grid-template-columns:repeat(1,1fr)!important}.rag-header h1{font-size:1.6rem!important}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULTS = {
    "messages":        [],
    "vectorstore":     None,
    "uploaded_docs":   0,
    "chunk_count":     0,
    "file_names":      [],
    "show_upload":     False,
    "doc_full_text":   "",
    "show_analytics":  False,      # Change 3: inline analytics below chat
    "active_doc":      None,       # which doc is active in viewer
    "show_chat":       True,       # hide/show chat toggle
    "active_model":    "llama-3.3-70b-versatile",
    "output_mode":     "Narrative",
    "retrieval_stats": [],
    "doc_text_map":    {},         # {filename: full text}
    "file_tags":       {},
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# FINANCIAL TAXONOMY
# ─────────────────────────────────────────────────────────────────────────────
TAXONOMY: dict[str, list[str]] = {
    "Income Statement":  ["revenue","net revenue","gross profit","operating income","ebit","ebitda","net income","net profit","earnings","eps","diluted eps","cogs","r&d","sg&a","tax","interest expense"],
    "Balance Sheet":     ["total assets","total liabilities","shareholders equity","book value","cash","receivables","inventory","goodwill","long-term debt","retained earnings","current liabilities"],
    "Cash Flow":         ["operating cash flow","free cash flow","fcf","capital expenditure","capex","investing activities","financing activities","dividends","buyback","depreciation","amortization"],
    "Ratios & Valuation":["p/e ratio","p/b ratio","roe","return on equity","roa","return on assets","debt to equity","current ratio","quick ratio","gross margin","net margin","operating margin","ev/ebitda"],
    "Growth & Guidance": ["year over year","yoy","quarter over quarter","qoq","guidance","outlook","forecast","projection","growth rate","cagr"],
    "Risk Factors":      ["risk","uncertainty","competition","regulatory","litigation","geopolitical","supply chain","inflation","interest rate risk","cyber"],
}

def tag_chunk(text: str) -> list[str]:
    tl = text.lower()
    return [cat for cat, kws in TAXONOMY.items() if any(kw in tl for kw in kws)]

CATEGORY_COLORS = {
    "Income Statement":  "#C084C8",
    "Balance Sheet":     "#60a5fa",
    "Cash Flow":         "#4ade80",
    "Ratios":            "#F0C040",
    "Per Share":         "#fb923c",
    "Growth":            "#34d399",
    "Risk Factors":      "#f87171",
    "Other":             "#9A8AAA",
}

# ─────────────────────────────────────────────────────────────────────────────
# MODEL REGISTRY
# ─────────────────────────────────────────────────────────────────────────────
MODEL_REGISTRY: dict = {
    "llama-3.3-70b-versatile": {
        "label":"Llama 3.3 70B","provider":"groq","ctx":128000,
        "cost":"Free","speed":"⚡ Fast","quality":"★★★★",
        "base_url":"https://api.groq.com/openai/v1",
    },
    "llama-3.1-8b-instant": {
        "label":"Llama 3.1 8B","provider":"groq","ctx":131072,
        "cost":"Free","speed":"⚡⚡ Ultra","quality":"★★★",
        "base_url":"https://api.groq.com/openai/v1",
    },
    "mixtral-8x7b-32768": {
        "label":"Mixtral 8×7B","provider":"groq","ctx":32768,
        "cost":"Free","speed":"⚡ Fast","quality":"★★★★",
        "base_url":"https://api.groq.com/openai/v1",
    },
    "gpt-4o": {
        "label":"GPT-4o","provider":"openai","ctx":128000,
        "cost":"$2.5/1M","speed":"🐢 Moderate","quality":"★★★★★",
        "base_url":"https://api.openai.com/v1",
    },
    "gpt-4o-mini": {
        "label":"GPT-4o Mini","provider":"openai","ctx":128000,
        "cost":"$0.15/1M","speed":"⚡ Fast","quality":"★★★★",
        "base_url":"https://api.openai.com/v1",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# METRIC EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────
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
]
_SCALE = {"billion":1e9,"b":1e9,"million":1e6,"m":1e6,None:1.0,"":1.0}

def extract_metrics(full_text: str) -> list[dict]:
    tl, results, seen = full_text.lower(), [], set()
    for label, unit, pattern in _METRIC_PATTERNS:
        for m in re.finditer(pattern, tl, re.IGNORECASE):
            raw_num = m.group(1).replace(",","")
            scale_k = (m.group(2) or "").lower() if m.lastindex and m.lastindex >= 2 else ""
            scale   = _SCALE.get(scale_k, 1.0)
            try: val = float(raw_num) * scale
            except: continue
            if label in seen: continue
            seen.add(label)
            ll = label.lower()
            if any(k in ll for k in ["eps","diluted","basic"]): cat = "Per Share"
            elif any(k in ll for k in ["margin","roe","roa","ratio","debt"]): cat = "Ratios"
            elif any(k in ll for k in ["cash flow","capex"]): cat = "Cash Flow"
            elif any(k in ll for k in ["revenue","income","profit","ebitda"]): cat = "Income Statement"
            else: cat = "Other"
            results.append({"label":label,"value":val,"unit":unit,"raw":m.group(0).strip()[:120],"category":cat})
    return results

def fmt_metric(val: float, unit: str) -> str:
    if unit == "USD":
        if val >= 1e9: return f"${val/1e9:.2f}B"
        if val >= 1e6: return f"${val/1e6:.1f}M"
        if val >= 1e3: return f"${val/1e3:.1f}K"
        return f"${val:.2f}"
    if unit == "%": return f"{val:.1f}%"
    if unit == "x": return f"{val:.2f}x"
    return f"{val:,.2f}"

# ─────────────────────────────────────────────────────────────────────────────
# HYBRID RETRIEVER
# ─────────────────────────────────────────────────────────────────────────────
def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())

class HybridRetriever:
    def __init__(self, chunks, embeddings):
        self.chunks, self.embeddings, self._bm25, self._ce = chunks, embeddings, None, None
        try:
            from rank_bm25 import BM25Okapi
            self._bm25 = BM25Okapi([_tokenize(c) for c in chunks])
        except: pass

    def _cos(self, a, b):
        dot=sum(x*y for x,y in zip(a,b)); na=math.sqrt(sum(x*x for x in a)); nb=math.sqrt(sum(x*x for x in b))
        return dot/(na*nb+1e-9)

    def retrieve(self, query, q_emb, n=5, bm25_weight=0.35, rerank=True, rerank_top=16):
        N = len(self.chunks)
        dense = [self._cos(q_emb, e) for e in self.embeddings]
        if self._bm25:
            raw = self._bm25.get_scores(_tokenize(query))
            bmax = max(raw) or 1.0
            bm25n = [s/bmax for s in raw]
        else:
            bm25n = [0.0]*N
        alpha = bm25_weight
        hybrid = [(1-alpha)*d + alpha*b for d,b in zip(dense, bm25n)]
        ranked = sorted(range(N), key=lambda i: hybrid[i], reverse=True)
        cands  = ranked[:max(rerank_top, n)]
        if rerank:
            try:
                from sentence_transformers import CrossEncoder
                if not self._ce:
                    self._ce = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-2-v2")
                pairs = [(query, self.chunks[i]) for i in cands]
                scores= self._ce.predict(pairs).tolist()
                cands = sorted(cands, key=lambda i: scores[cands.index(i)], reverse=True)
            except: pass
        return [{"idx":i,"chunk":self.chunks[i],"score":hybrid[i],"bm25":bm25n[i],"dense":dense[i]} for i in cands[:n]]

# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATES
# ─────────────────────────────────────────────────────────────────────────────
TEMPLATES = {
    "Revenue Summary":         {"icon":"💰","cat":"Income Statement","prompt":"Extract and summarise revenue figures: total revenue, segment breakdown, YoY growth, and guidance. Present as a structured table."},
    "Profitability Deep-Dive": {"icon":"📊","cat":"Income Statement","prompt":"Analyse gross profit & margin, operating income & margin, EBITDA, net income & net margin. Compare to prior year. Flag one-time items."},
    "EPS Analysis":            {"icon":"📈","cat":"Per Share","prompt":"What is basic and diluted EPS? How did it change YoY and QoQ? What drove the change — revenue, costs, buybacks, or tax?"},
    "Balance Sheet Snapshot":  {"icon":"🏦","cat":"Balance Sheet","prompt":"Summarise total assets, liabilities, shareholders equity, cash, and debt. Calculate debt-to-equity and book value per share."},
    "Liquidity Assessment":    {"icon":"💧","cat":"Balance Sheet","prompt":"Assess liquidity: current ratio, quick ratio, cash position, short-term debt. Is there a liquidity risk?"},
    "Free Cash Flow Analysis": {"icon":"🌊","cat":"Cash Flow","prompt":"Break down operating cash flow, CapEx, and free cash flow. Compare FCF to net income. What is the FCF conversion rate?"},
    "Capital Allocation":      {"icon":"🎯","cat":"Cash Flow","prompt":"How is capital being deployed? Dividends, buybacks, M&A, R&D, debt repayment. What % of FCF is returned to shareholders?"},
    "Key Ratios":              {"icon":"⚖️","cat":"Ratios","prompt":"Calculate or extract: ROE, ROA, gross/net/operating margins, debt/equity, current ratio, interest coverage. Flag any concerning values."},
    "Risk Factor Summary":     {"icon":"⚠️","cat":"Risk Factors","prompt":"List the top 5 material risks. For each: name, description, potential financial impact, and any mitigation strategies."},
    "Growth & Guidance":       {"icon":"🚀","cat":"Growth","prompt":"What is the growth trajectory? Extract 3-year revenue CAGR, management guidance, key growth drivers and headwinds."},
    "Competitive Position":    {"icon":"🏆","cat":"Strategy","prompt":"Summarise the competitive moat, market share, key differentiators, and strategic priorities. What risks could erode this position?"},
}

# ─────────────────────────────────────────────────────────────────────────────
# EXPORT HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def export_chat_markdown(messages: list) -> str:
    lines = [f"# Financial RAG Assistant — Chat Export",
             f"*{_dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*\n"]
    for m in messages:
        role = "**You**" if m["role"]=="user" else "**Assistant**"
        lines.append(f"### {role}\n{m['content']}\n")
        if m.get("sources"):
            lines.append("**Sources:**")
            for s in m["sources"]:
                lines.append(f"- 📄 `{s['filename']}` (relevance: {s['score']}) — {s['preview'][:100]}…")
            lines.append("")
    return "\n".join(lines)

def export_chat_json(messages: list) -> str:
    return json.dumps([{"role":m["role"],"content":m["content"]} for m in messages], indent=2)

# ─────────────────────────────────────────────────────────────────────────────
# FILE EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────
def extract_text_from_file(f) -> str:
    name = f.name.lower()
    if name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(f)
        return " ".join(pg.extract_text() or "" for pg in reader.pages)
    elif name.endswith((".xlsx",".xls")):
        dfs = pd.read_excel(f, sheet_name=None)
        return "\n".join(f"[Sheet: {s}]\n{df.to_string(index=False)}" for s,df in dfs.items())
    elif name.endswith(".csv"):
        return pd.read_csv(f).to_string(index=False)
    elif name.endswith(".json"):
        import json as _j
        data = _j.load(f)
        return _j.dumps(data, indent=2)
    elif name.endswith((".htm",".html")):
        raw = f.read().decode("utf-8",errors="ignore")
        return re.sub(r"<[^>]+>"," ",raw)
    else:
        return f.read().decode("utf-8",errors="ignore")

# ─────────────────────────────────────────────────────────────────────────────
# INGEST
# ─────────────────────────────────────────────────────────────────────────────
def ingest_documents(files):
    from chromadb import EphemeralClient
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    @st.cache_resource
    def load_model():
        # ── CHANGE 1: Finance-specific FinBERT embeddings ──────────────────
        # yiyanghkust/finbert-pretrain is trained on SEC 10-K/10-Q filings,
        # earnings call transcripts and financial news.  It understands EPS,
        # EBITDA, YoY growth, debt-to-equity etc far better than MiniLM.
        # Falls back to MiniLM if FinBERT can't be loaded (e.g. no internet).
        try:
            m = SentenceTransformer("yiyanghkust/finbert-pretrain")
            m.encode(["warmup"], normalize_embeddings=True)   # validate
            return m
        except Exception:
            return SentenceTransformer("all-MiniLM-L6-v2")   # graceful fallback

    model  = load_model()
    client = EphemeralClient(settings=Settings(anonymized_telemetry=False))
    try: client.delete_collection("financials")
    except: pass
    col = client.create_collection("financials", metadata={"hnsw:space":"cosine"})

    all_chunks, all_ids, all_meta, fnames = [], [], [], []
    doc_text_map = {}
    prog = st.progress(0, text="Reading files…")

    for i, f in enumerate(files):
        try:
            text = extract_text_from_file(f)
        except Exception as exc:
            st.warning(f"⚠ Could not read {f.name}: {exc}")
            continue
        doc_text_map[f.name] = text
        auto_tags   = tag_chunk(text[:3000])
        all_tag_str = "|".join(auto_tags)
        chunks = splitter.split_text(text)
        fnames.append(f.name)
        for j, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(f"{f.name}_chunk_{j}")
            all_meta.append({"filename":f.name,"chunk":j,"tags":all_tag_str,"filetype":f.name.rsplit(".",1)[-1].lower()})
        prog.progress((i+1)/len(files), text=f"Processed {f.name}")

    prog.empty()
    if all_chunks:
        with st.spinner(f"Embedding {len(all_chunks)} chunks with FinBERT (finance-aware)…"):
            embs = model.encode(all_chunks, normalize_embeddings=True).tolist()
            col.add(documents=all_chunks, embeddings=embs, ids=all_ids, metadatas=all_meta)

    st.session_state.vectorstore    = {"collection":col,"model":model}
    st.session_state.uploaded_docs  = len(fnames)
    st.session_state.chunk_count    = len(all_chunks)
    st.session_state.file_names     = fnames
    st.session_state.doc_full_text  = " ".join(all_chunks)
    st.session_state.doc_text_map   = doc_text_map
    st.session_state.show_analytics = True   # Change 3: auto-open analytics below chat
    if fnames and not st.session_state.active_doc:
        st.session_state.active_doc = fnames[0]
    return len(all_chunks)

# ─────────────────────────────────────────────────────────────────────────────
# RATE LIMITER
# ─────────────────────────────────────────────────────────────────────────────
_HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

class _TokenBucket:
    def __init__(self, capacity=30, refill_every=60.0):
        self._cap,self._tokens,self._interval=capacity,float(capacity),refill_every/capacity
        self._lock,self._last=_threading.Lock(),_time.monotonic()
    def acquire(self, timeout=5.0):
        deadline=_time.monotonic()+timeout
        while True:
            with self._lock:
                now=_time.monotonic(); earned=(now-self._last)/self._interval
                self._tokens=min(self._cap,self._tokens+earned); self._last=now
                if self._tokens>=1.0: self._tokens-=1.0; return True
            if _time.monotonic()>=deadline: return False
            _time.sleep(0.05)

@st.cache_resource
def _get_bucket(): return _TokenBucket(30, 60.0)

def _throttled_get(url, timeout=10):
    if not _get_bucket().acquire(timeout=4.0):
        raise RuntimeError("Rate limit reached — wait a few seconds.")
    return requests.get(url, headers=_HEADERS, timeout=timeout)

# ─────────────────────────────────────────────────────────────────────────────
# DATA FETCH
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_yahoo_series(symbol, period, interval):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={period}&interval={interval}&includePrePost=false"
    try:
        r=_throttled_get(url,10); r.raise_for_status(); data=r.json()
        res=data["chart"]["result"][0]; ts=res["timestamp"]; close=res["indicators"]["quote"][0]["close"]
        idx=pd.to_datetime(ts,unit="s",utc=True).tz_convert("US/Eastern")
        return pd.Series(close,index=idx,name=symbol).dropna()
    except: return None

@st.cache_data(ttl=60)
def fetch_quote(symbol):
    url=f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=2d&interval=1d"
    try:
        r=_throttled_get(url,8); r.raise_for_status(); data=r.json()
        q=[x for x in data["chart"]["result"][0]["indicators"]["quote"][0]["close"] if x is not None]
        if not q: return None
        pct=(q[-1]-q[-2])/q[-2]*100 if len(q)>=2 else 0.0
        return {"price":q[-1],"pct":pct}
    except: return None

@st.cache_data(ttl=60)
def fetch_multi_quotes(symbols: tuple):
    return {sym:info for sym in symbols if (info:=fetch_quote(sym))}

@st.cache_data(ttl=300)
def fetch_fear_greed():
    try:
        r=_throttled_get("https://api.alternative.me/fng/?limit=1",8)
        d=r.json()["data"][0]; return {"value":int(d["value"]),"label":d["value_classification"]}
    except: return {"value":50,"label":"Neutral"}

@st.cache_data(ttl=600)
def fetch_rss_with_images(feed_url, source_name, accent, max_items=8):
    import html as _h
    FALLBACK={
        "Bloomberg":"https://assets.bbhub.io/company/sites/51/2019/08/BBG-Logo-Black.png",
        "Reuters":"https://www.reuters.com/pf/resources/images/reuters/logo-vertical-default.png",
        "CNBC":"https://www.cnbc.com/2020/07/21/cnbc-social-card-2019.jpg",
        "Federal Reserve":"https://www.federalreserve.gov/img/federal-reserve-seal.svg",
    }
    try:
        hdrs={**_HEADERS,"Accept":"application/rss+xml,application/xml,text/xml,*/*"}
        r=requests.get(feed_url,headers=hdrs,timeout=10); r.raise_for_status(); text=r.text
    except: return []
    results,items=[],re.findall(r"<item[^>]*>(.*?)</item>",text,re.DOTALL)
    if not items: items=re.findall(r"<entry[^>]*>(.*?)</entry>",text,re.DOTALL)
    for item in items[:max_items]:
        tm=re.search(r"<title[^>]*>(.*?)</title>",item,re.DOTALL|re.IGNORECASE)
        raw=tm.group(1).strip() if tm else ""
        cdata=re.match(r"<!\[CDATA\[(.*?)\]\]>",raw,re.DOTALL)
        title=_h.unescape(re.sub(r"<[^>]+>","",cdata.group(1) if cdata else raw)).strip()
        if not title or len(title)<10: continue
        lm=(re.search(r'<link[^>]*href=["\'](https?://[^"\' >]+)["\']',item,re.IGNORECASE|re.DOTALL) or
            re.search(r"<link>(.*?)</link>",item,re.DOTALL|re.IGNORECASE))
        link=(lm.group(1) or "#").strip() if lm else "#"
        if not link.startswith("http"): link="#"
        img_url=""
        mm=re.search(r'<media:(?:content|thumbnail)[^>]+url=["\'](https?://[^"\']+)["\']',item,re.IGNORECASE)
        if mm: img_url=mm.group(1)
        if not img_url:
            em=re.search(r'<enclosure[^>]+url=["\'](https?://[^"\']+(?:jpg|jpeg|png|webp))["\']',item,re.IGNORECASE)
            if em: img_url=em.group(1)
        if not img_url: img_url=FALLBACK.get(source_name,"")
        results.append({"title":title,"link":link,"source":source_name,"accent":accent,"img_url":img_url})
    return results

@st.cache_data(ttl=600)
def fetch_gnews_with_images(query, source_label, accent, max_items=6):
    import urllib.parse
    url=f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en"
    return fetch_rss_with_images(url, source_label, accent, max_items)

def make_chip_html(sym, name, price, pct, prefix="$", suffix="", decimals=2, icon=""):
    arrow="▲" if pct>0.005 else ("▼" if pct<-0.005 else "●")
    cls="up" if pct>0.005 else ("down" if pct<-0.005 else "flat")
    icon_html=f'<span style="font-size:.95rem;margin-right:.15rem;">{icon}</span>' if icon else ""
    return (f'<div class="price-chip"><div class="pc-sym">{icon_html}{sym}</div>'
            f'<div class="pc-name">{name}</div>'
            f'<div class="pc-val">{prefix}{price:,.{decimals}f}{suffix}</div>'
            f'<div class="pc-chg {cls}">{arrow} {abs(pct):.2f}%</div></div>')

# ─────────────────────────────────────────────────────────────────────────────
# NEWS FEEDS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_all_news():
    news=[]
    for url,src,color in [
        ("https://feeds.bloomberg.com/markets/news.rss","Bloomberg","#4ADE80"),
        ("https://www.cnbc.com/id/100003114/device/rss/rss.html","CNBC","#C084C8"),
        ("https://feeds.reuters.com/reuters/businessNews","Reuters","#60A5FA"),
    ]:
        news.extend(fetch_rss_with_images(url,src,color,4))
    if len(news)<6: news.extend(fetch_gnews_with_images("financial markets economy","Google News","#9CA3AF",8))
    return news[:16]

@st.cache_data(ttl=600)
def get_policy_news():
    policy=[]
    for url,src,flag,color in [
        ("https://www.federalreserve.gov/feeds/press_all.xml","Federal Reserve","🇺🇸","#60A5FA"),
        ("https://www.imf.org/en/News/rss?language=eng","IMF","🌐","#A78BFA"),
        ("https://www.rbi.org.in/scripts/rss.aspx","RBI India","🇮🇳","#FB923C"),
    ]:
        items=fetch_rss_with_images(url,src,color,3)
        for it in items: it["flag"]=flag; it["policy"]=True
        policy.extend(items)
    if len(policy)<4:
        extra=fetch_gnews_with_images("central bank monetary policy","Policy News","#A78BFA",6)
        for it in extra: it["flag"]="🏦"; it["policy"]=True
        policy.extend(extra)
    return policy[:12]

@st.cache_data(ttl=600)
def fetch_rss(url, max_items=6):
    import xml.etree.ElementTree as ET
    try:
        r=requests.get(url,headers={**_HEADERS,"Accept":"application/rss+xml,*/*"},timeout=12)
        r.raise_for_status(); root=ET.fromstring(r.content)
        results=[]
        for item in root.findall(".//item")[:max_items]:
            title=(item.findtext("title") or "").strip()
            link=(item.findtext("link") or "").strip()
            pub=(item.findtext("pubDate") or "").strip()
            desc=re.sub(r"<[^>]+"," ",(item.findtext("description") or "").strip())[:180]
            try:
                from email.utils import parsedate_to_datetime
                pub=parsedate_to_datetime(pub).strftime("%d %b, %H:%M")
            except: pub=pub[:16]
            if title: results.append({"title":title,"link":link,"date":pub,"summary":desc})
        return results
    except: return []

# ─────────────────────────────────────────────────────────────────────────────
# CAROUSEL
# ─────────────────────────────────────────────────────────────────────────────
def build_carousel_html(items, is_policy=False, height_px=380):
    accent_grad = "linear-gradient(90deg,#3B82F6,#A78BFA)" if is_policy else "linear-gradient(90deg,#6B2D6B,#C084C8)"
    title_text  = "Policy &amp; Government Decisions" if is_policy else "Financial Headlines"
    bar_c       = "#3B82F6" if is_policy else "#C084C8"
    bg_card     = "#0A0F1E" if is_policy else "#120E1A"
    bc          = "rgba(59,130,246,0.3)" if is_policy else "rgba(139,58,139,0.3)"
    slides_js   = json.dumps([
        {"title":i["title"],"link":i.get("link","#"),"source":i.get("source",""),
         "accent":i.get("accent","#C084C8"),"img":i.get("img_url",""),
         "flag":i.get("flag",""),"policy":i.get("policy",False)} for i in items])
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0D0B12;font-family:'Segoe UI',system-ui,sans-serif;color:#EDE8F5;height:{height_px}px;overflow:hidden}}
.cw{{background:#0D0B12;border:1px solid {bc};border-radius:14px;height:{height_px}px;display:flex;flex-direction:column;overflow:hidden;position:relative}}
.cw::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:{accent_grad}}}
.ch{{display:flex;align-items:center;justify-content:space-between;padding:.8rem 1rem .55rem;flex-shrink:0;border-bottom:1px solid rgba(139,58,139,.1)}}
.ct{{font-family:'Georgia',serif;font-size:.95rem;font-weight:300;color:#EDE8F5;display:flex;align-items:center;gap:.45rem}}
.ct::before{{content:'';display:inline-block;width:3px;height:.95rem;background:{accent_grad};border-radius:2px;flex-shrink:0}}
.cnav{{display:flex;align-items:center;gap:.35rem}}
.nb{{background:rgba(107,45,107,.15);border:1px solid {bc};color:{bar_c};width:24px;height:24px;border-radius:50%;cursor:pointer;font-size:.95rem;display:flex;align-items:center;justify-content:center;transition:background .2s;flex-shrink:0}}
.nb:hover{{background:rgba(107,45,107,.35)}}
.dots{{display:flex;gap:3px;align-items:center;flex-wrap:wrap;max-width:140px}}
.dot{{width:5px;height:5px;border-radius:50%;background:rgba(139,58,139,.3);border:1px solid rgba(139,58,139,.4);cursor:pointer;transition:all .2s;flex-shrink:0}}
.dot.active{{background:{bar_c};transform:scale(1.35)}}
.sa{{flex:1;position:relative;overflow:hidden}}
.sl{{position:absolute;top:0;left:0;right:0;bottom:0;display:flex;flex-direction:column;opacity:0;transform:translateX(40px);transition:opacity .4s ease,transform .4s ease;pointer-events:none}}
.sl.active{{opacity:1;transform:translateX(0);pointer-events:all}}
.sl.leaving{{opacity:0;transform:translateX(-40px)}}
.si{{width:100%;height:150px;object-fit:cover;flex-shrink:0;background:#120E1A}}
.ip{{width:100%;height:150px;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:2.2rem;background:linear-gradient(135deg,#120E1A 0%,#1a1028 100%);border-bottom:1px solid rgba(139,58,139,.12)}}
.sb{{padding:.65rem .9rem .45rem;display:flex;flex-direction:column;gap:.25rem;flex:1;background:{bg_card}}}
.ss{{font-family:'Courier New',monospace;font-size:.56rem;letter-spacing:.12em;text-transform:uppercase;display:flex;align-items:center;gap:.35rem;flex-wrap:wrap}}
.pb2{{font-size:.43rem;background:rgba(59,130,246,.15);border:1px solid rgba(59,130,246,.3);color:#93C5FD;padding:.04rem .32rem;border-radius:3px;letter-spacing:.07em;text-transform:uppercase}}
.stitle{{font-size:.85rem;font-weight:500;color:#EDE8F5;line-height:1.42;text-decoration:none;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
.stitle:hover{{color:{bar_c};text-decoration:underline;text-underline-offset:3px}}
.sm{{font-family:'Courier New',monospace;font-size:.46rem;color:#4A3858;margin-top:auto}}
.pw{{flex-shrink:0;height:2px;background:rgba(139,58,139,.1);overflow:hidden}}
.pb{{height:100%;width:0%;background:{accent_grad};border-radius:1px;transition:width 3s linear}}
.cf{{display:flex;justify-content:space-between;align-items:center;padding:.25rem .9rem;flex-shrink:0;background:rgba(0,0,0,.3)}}
.fl{{font-family:'Courier New',monospace;font-size:.42rem;color:#4A3858;letter-spacing:.07em}}
</style></head><body>
<div class="cw" id="car">
  <div class="ch"><div class="ct">{title_text}</div>
    <div class="cnav"><div class="dots" id="dots"></div>
      <button class="nb" id="prev">&#8249;</button><button class="nb" id="next">&#8250;</button>
    </div>
  </div>
  <div class="sa" id="slides"></div>
  <div class="pw"><div class="pb" id="pb"></div></div>
  <div class="cf"><div class="fl">&#9679; live · 10min refresh</div><div class="fl" id="ctr">1/1</div></div>
</div>
<script>
(function(){{
  var S={slides_js},N=S.length,cur=0,paused=false,timer=null,pbT=null;
  var se=document.getElementById('slides'),de=document.getElementById('dots'),ce=document.getElementById('ctr'),pb=document.getElementById('pb');
  S.forEach(function(s,i){{
    var sd=document.createElement('div');sd.className='sl'+(i===0?' active':'');sd.id='sl'+i;
    var img=s.img?'<img class="si" src="'+s.img+'" alt="" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'"><div class="ip" style="display:none">📰</div>':'<div class="ip">📰</div>';
    var src=s.policy?'<span style="color:'+s.accent+'">'+s.flag+' '+s.source+'</span><span class="pb2">Policy</span>':'<span style="color:'+s.accent+'">'+s.source+'</span>';
    sd.innerHTML=img+'<div class="sb"><div class="ss">'+src+'</div><a class="stitle" href="'+s.link+'" target="_blank">'+s.title+'</a><div class="sm">&#x23F1; 3s auto</div></div>';
    se.appendChild(sd);
    var dot=document.createElement('span');dot.className='dot'+(i===0?' active':'');dot.id='dot'+i;
    dot.onclick=(function(idx){{return function(){{goTo(idx)}}}})(i);de.appendChild(dot);
  }});
  function startPB(){{clearTimeout(pbT);pb.style.transition='none';pb.style.width='0%';pbT=setTimeout(function(){{pb.style.transition='width 3s linear';pb.style.width='100%'}},40)}}
  function goTo(n){{
    var p=cur;cur=((n%N)+N)%N;if(p===cur)return;
    var o=document.getElementById('sl'+p),nw=document.getElementById('sl'+cur);
    var od=document.getElementById('dot'+p),nd=document.getElementById('dot'+cur);
    if(o){{o.className='sl leaving';setTimeout(function(){{if(o)o.className='sl'}},440)}}
    if(nw)nw.className='sl active';if(od)od.className='dot';if(nd)nd.className='dot active';
    ce.textContent=(cur+1)+'/'+N;startPB();
  }}
  function next(){{goTo(cur+1)}}function prev(){{goTo(cur-1)}}
  document.getElementById('next').onclick=function(){{next();restart()}};
  document.getElementById('prev').onclick=function(){{prev();restart()}};
  function restart(){{clearInterval(timer);timer=setInterval(function(){{if(!paused)next()}},3000)}}
  document.getElementById('car').addEventListener('mouseenter',function(){{paused=true}});
  document.getElementById('car').addEventListener('mouseleave',function(){{paused=false}});
  ce.textContent='1/'+N;startPB();restart();
}})();
</script></body></html>"""

# ─────────────────────────────────────────────────────────────────────────────
# INDIA NEWS RSS
# ─────────────────────────────────────────────────────────────────────────────
NEWS_SOURCES = {
    "📰 Economic Times":   {"rss":"https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms","tag":"Markets"},
    "📰 Business Standard":{"rss":"https://www.business-standard.com/rss/home_page_top_stories.rss","tag":"Markets"},
    "📰 Mint":             {"rss":"https://www.livemint.com/rss/markets","tag":"Markets"},
    "🏛️ RBI":              {"rss":"https://www.rbi.org.in/Scripts/Notifications_Rss.aspx","tag":"Policy"},
    "🏛️ SEBI":             {"rss":"https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doGetPublicationRss=yes&rssHead=4","tag":"Policy"},
    "🏛️ Finance Ministry": {"rss":"https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3","tag":"Policy"},
}

def render_news_card(a):
    tag_c="#C084C8" if a["src_tag"]=="Policy" else "#4ade80"
    tag_bg="rgba(192,132,200,.1)" if a["src_tag"]=="Policy" else "rgba(74,222,128,.08)"
    tag_bc="rgba(192,132,200,.3)" if a["src_tag"]=="Policy" else "rgba(74,222,128,.25)"
    src=a["source"].replace("📰 ","").replace("🏛️ ","")
    return f"""<div style="background:#0D0B12;border:1px solid rgba(139,58,139,.22);border-radius:10px;
        padding:.75rem .9rem;margin-bottom:.5rem;border-left:3px solid {tag_c};">
  <div style="display:flex;align-items:center;gap:.35rem;margin-bottom:.35rem;flex-wrap:wrap;">
    <span style="background:{tag_bg};border:1px solid {tag_bc};color:{tag_c};font-family:'Space Mono',monospace;
                 font-size:.5rem;letter-spacing:.1em;padding:.08rem .35rem;border-radius:3px;text-transform:uppercase;">{a['src_tag']}</span>
    <span style="font-family:'Space Mono',monospace;font-size:.5rem;color:#4A3858;">{src}</span>
    <span style="font-family:'Space Mono',monospace;font-size:.48rem;color:#4A3858;margin-left:auto;">{a.get('date','')}</span>
  </div>
  <a href="{a.get('link','#')}" target="_blank" style="text-decoration:none;">
    <div style="font-family:'Syne',sans-serif;font-size:.8rem;font-weight:500;color:#EDE8F5;line-height:1.42;margin-bottom:.3rem;">{a['title']}</div>
  </a>
  <div style="font-size:.7rem;color:#4A3858;line-height:1.5;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;">{a.get('summary','')}</div>
</div>"""

# ─────────────────────────────────────────────────────────────────────────────
# EVAL BENCHMARK
# ─────────────────────────────────────────────────────────────────────────────
EVAL_QUESTIONS = [
    {"id":"fb_001","question":"What was total revenue?","expected_keywords":["revenue","billion","million","$"],"category":"Income Statement"},
    {"id":"fb_002","question":"What was diluted EPS?","expected_keywords":["eps","diluted","$","per share"],"category":"Per Share"},
    {"id":"fb_003","question":"What was the gross margin?","expected_keywords":["gross margin","%","percent"],"category":"Ratios"},
    {"id":"fb_004","question":"What was free cash flow?","expected_keywords":["free cash flow","operating","capex"],"category":"Cash Flow"},
    {"id":"fb_005","question":"What are the main risk factors?","expected_keywords":["risk","competition","regulatory"],"category":"Risk Factors"},
    {"id":"fb_006","question":"What is the company's revenue guidance?","expected_keywords":["guidance","outlook","forecast"],"category":"Growth"},
    {"id":"fb_007","question":"What is the debt-to-equity ratio?","expected_keywords":["debt","equity","ratio"],"category":"Ratios"},
    {"id":"fb_008","question":"How much did the company spend on R&D?","expected_keywords":["research","development","r&d"],"category":"Income Statement"},
]

def score_answer(answer, kws):
    al=answer.lower(); hits=sum(1 for k in kws if k.lower() in al)
    return {"recall":hits/len(kws),"hits":hits,"total":len(kws),"score_pct":round(hits/len(kws)*100,1)}

# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS TAB RENDERER
# ─────────────────────────────────────────────────────────────────────────────
def render_analytics_tab(vectorstore, groq_api_key, doc_full_text, active_model):
    if not vectorstore and not doc_full_text:
        st.markdown("""<div style="text-align:center;padding:3rem 2rem;">
          <div style="font-size:2.5rem;margin-bottom:1rem;opacity:.35;">📊</div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.45rem;font-weight:300;font-style:italic;color:#4A3858;">
            Upload documents to unlock analytics</div>
          <div style="font-size:.78rem;color:#4A3858;margin-top:.5rem;max-width:340px;margin-left:auto;margin-right:auto;">
            Auto-extract metrics · Trend charts · Templates · Hybrid search · Benchmarking
          </div></div>""", unsafe_allow_html=True)
        return

    sub_tabs = st.tabs(["📊 Metrics","📋 Templates","🔍 Hybrid Search","🧪 Eval","📄 Doc Viewer"])

    # ── Metrics ──────────────────────────────────────────────────────────────
    with sub_tabs[0]:
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.16em;text-transform:uppercase;color:#C084C8;margin-bottom:.7rem;">Auto-Extracted Financial Metrics</div>', unsafe_allow_html=True)
        if doc_full_text:
            with st.spinner("Extracting metrics…"):
                metrics = extract_metrics(doc_full_text)
            if metrics:
                by_cat = {}
                for m in metrics: by_cat.setdefault(m["category"],[]).append(m)
                for cat in ["Income Statement","Per Share","Cash Flow","Ratios","Other"]:
                    items = by_cat.get(cat,[])
                    if not items: continue
                    color = CATEGORY_COLORS.get(cat,"#9A8AAA")
                    st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.18em;text-transform:uppercase;color:{color};margin:.9rem 0 .45rem;padding-bottom:.25rem;border-bottom:1px solid rgba(139,58,139,.15);">{cat}</div>', unsafe_allow_html=True)
                    cols = st.columns(min(len(items),4))
                    for i, m in enumerate(items):
                        with cols[i%4]:
                            val_str = fmt_metric(m["value"],m["unit"])
                            st.markdown(f'<div class="m-card" style="border-top:2px solid {color};">'
                                f'<div class="m-card-lbl">{m["label"]}</div>'
                                f'<div class="m-card-val">{val_str}</div>'
                                f'<div class="m-card-cat" style="color:{color};">{cat}</div></div>', unsafe_allow_html=True)

                st.markdown("<hr style='border-color:rgba(139,58,139,.12);margin:.9rem 0;'>", unsafe_allow_html=True)
                usd_m=[m for m in metrics if m["unit"]=="USD" and m["value"]>0]
                pct_m=[m for m in metrics if m["unit"]=="%"]
                if usd_m:
                    st.markdown('<div style="font-family:Space Mono,monospace;font-size:.5rem;letter-spacing:.14em;text-transform:uppercase;color:#C084C8;margin:.6rem 0 .2rem;">USD Metrics ($B)</div>', unsafe_allow_html=True)
                    st.bar_chart(pd.DataFrame(usd_m).set_index("label")["value"]/1e9, height=170, use_container_width=True)
                if pct_m:
                    st.markdown('<div style="font-family:Space Mono,monospace;font-size:.5rem;letter-spacing:.14em;text-transform:uppercase;color:#F0C040;margin:.6rem 0 .2rem;">% Metrics</div>', unsafe_allow_html=True)
                    st.bar_chart(pd.DataFrame(pct_m).set_index("label")["value"], height=140, use_container_width=True)
                with st.expander("📄 Raw extraction table"):
                    st.dataframe(pd.DataFrame([{"Metric":m["label"],"Value":fmt_metric(m["value"],m["unit"]),"Unit":m["unit"],"Category":m["category"],"Raw":m["raw"]} for m in metrics]), use_container_width=True, hide_index=True)
            else:
                st.info("No metrics matched. Try the Templates tab for LLM-powered extraction.")

    # ── Templates ────────────────────────────────────────────────────────────
    with sub_tabs[1]:
        cats=sorted({v["cat"] for v in TEMPLATES.values()})
        chosen=st.selectbox("Filter",["All"]+cats, label_visibility="collapsed", key="tpl_cat")
        visible={k:v for k,v in TEMPLATES.items() if chosen=="All" or v["cat"]==chosen}
        items=list(visible.items())
        for row in range(0,len(items),3):
            cols=st.columns(3)
            for ci,(tname,tmeta) in enumerate(items[row:row+3]):
                with cols[ci]:
                    color=CATEGORY_COLORS.get(tmeta["cat"],"#9A8AAA")
                    st.markdown(f'<div class="tpl-card" style="border-top:2px solid {color};">'
                        f'<div style="font-size:1.15rem;">{tmeta["icon"]}</div>'
                        f'<div style="font-family:Syne,sans-serif;font-size:.8rem;font-weight:600;color:#EDE8F5;margin:.25rem 0 .18rem;">{tname}</div>'
                        f'<div style="font-family:Space Mono,monospace;font-size:.5rem;color:{color};text-transform:uppercase;letter-spacing:.1em;">{tmeta["cat"]}</div>'
                        f'</div>', unsafe_allow_html=True)
                    if st.button("Run Analysis →", key=f"tpl_{tname[:18]}", use_container_width=True):
                        st.session_state["_prefill"]=tmeta["prompt"]
                        st.success(f"✓ '{tname}' sent to chat ↓")
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:.48rem;color:#4A3858;margin-top:.8rem;">Templates inject the prompt into the chat — scroll to Markets & Chat tab to see the answer.</div>', unsafe_allow_html=True)

    # ── Hybrid Search ─────────────────────────────────────────────────────────
    with sub_tabs[2]:
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.16em;text-transform:uppercase;color:#C084C8;margin-bottom:.7rem;">BM25 + Dense Retrieval · Cross-Encoder Re-ranking</div>', unsafe_allow_html=True)
        hs_q=st.text_input("Search query",placeholder="e.g. free cash flow capital expenditure",label_visibility="collapsed",key="hs_q")
        c1,c2,c3=st.columns(3)
        with c1: bm25_w=st.slider("BM25 weight",0.0,1.0,.35,.05,key="bm25_w")
        with c2: top_n=st.slider("Results",3,10,5,key="hs_n")
        with c3: use_ce=st.checkbox("Cross-encoder re-rank",True,key="hs_ce")
        tax_f=st.multiselect("Taxonomy filter",list(TAXONOMY.keys()),default=[],label_visibility="collapsed",key="hs_tax")
        if hs_q and vectorstore:
            with st.spinner("Retrieving…"):
                try:
                    vs=vectorstore; model=vs["model"]; col=vs["collection"]
                    all_res=col.get(include=["documents","embeddings","metadatas"])
                    chunks,embeds,metas=all_res["documents"],all_res["embeddings"],all_res["metadatas"]
                    if tax_f:
                        fi=[i for i,c in enumerate(chunks) if any(tc in tag_chunk(c) for tc in tax_f)]
                        chunks=[chunks[i] for i in fi]; embeds=[embeds[i] for i in fi]; metas=[metas[i] for i in fi]
                    if chunks:
                        q_emb=model.encode([hs_q],normalize_embeddings=True).tolist()[0]
                        hr=HybridRetriever(chunks,embeds)
                        hits=hr.retrieve(hs_q,q_emb,n=top_n,bm25_weight=bm25_w,rerank=use_ce)
                        for rank,h in enumerate(hits,1):
                            meta=metas[h["idx"]] if h["idx"]<len(metas) else {}
                            tags=tag_chunk(h["chunk"])
                            def _tag_span(t):
                                c=CATEGORY_COLORS.get(t,"#9A8AAA")
                                return f'<span style="background:rgba(139,58,139,.12);border:1px solid rgba(139,58,139,.28);font-family:Space Mono,monospace;font-size:.47rem;padding:.08rem .3rem;border-radius:3px;color:{c};">{t}</span>'
                            tag_html=" ".join(_tag_span(t) for t in tags)
                            sc=int(h["score"]*100); bar_c="#4ade80" if sc>75 else ("#F0C040" if sc>50 else "#f87171")
                            st.markdown(f'<div style="background:#0D0B12;border:1px solid rgba(139,58,139,.22);border-left:3px solid #C084C8;border-radius:0 8px 8px 0;padding:.65rem .85rem;margin-bottom:.45rem;">'
                                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.3rem;">'
                                f'<div style="font-family:Space Mono,monospace;font-size:.56rem;color:#C084C8;">#{rank} · 📄 {meta.get("filename","—")}</div>'
                                f'<div style="font-family:Space Mono,monospace;font-size:.5rem;color:#4A3858;">hybrid:{h["score"]:.3f} dense:{h["dense"]:.3f} bm25:{h["bm25"]:.3f}</div></div>'
                                f'<div style="background:#07060C;border-radius:2px;height:3px;margin-bottom:.3rem;overflow:hidden;"><div style="height:100%;width:{sc}%;background:{bar_c};border-radius:2px;"></div></div>'
                                f'<div style="font-size:.78rem;color:#9A8AAA;line-height:1.5;">{h["chunk"][:300]}…</div>'
                                f'<div style="margin-top:.35rem;display:flex;gap:.25rem;flex-wrap:wrap;">{tag_html}</div></div>', unsafe_allow_html=True)
                    else: st.warning("No chunks match the selected taxonomy filters.")
                except Exception as e: st.error(f"Search error: {e}")
        elif hs_q: st.info("Upload and ingest documents first.")

    # ── Eval Benchmark ────────────────────────────────────────────────────────
    with sub_tabs[3]:
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.16em;text-transform:uppercase;color:#C084C8;margin-bottom:.6rem;">FinanceBench-Style QA Accuracy Evaluation</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:.78rem;color:#4A3858;margin-bottom:.9rem;line-height:1.7;">Runs 8 standard financial QA prompts and measures keyword-recall accuracy.</div>', unsafe_allow_html=True)
        if st.button("▶  Run Benchmark"):
            if not vectorstore or not groq_api_key:
                st.error("Need both documents and a Groq API key.")
            else:
                results=[]
                prog=st.progress(0,"Evaluating…")
                for i,eq in enumerate(EVAL_QUESTIONS):
                    try:
                        from openai import OpenAI
                        oai=OpenAI(api_key=groq_api_key,base_url="https://api.groq.com/openai/v1")
                        vs=vectorstore; q_emb=vs["model"].encode([eq["question"]],normalize_embeddings=True).tolist()
                        res=vs["collection"].query(query_embeddings=q_emb,n_results=4,include=["documents","metadatas","distances"])
                        ctx="\n---\n".join(res["documents"][0])
                        resp=oai.chat.completions.create(model=active_model,messages=[
                            {"role":"system","content":"Answer using only context. Be concise."},
                            {"role":"user","content":f"Context:\n{ctx}\n\nQuestion: {eq['question']}"}
                        ],temperature=0.05,max_tokens=400)
                        ans=resp.choices[0].message.content
                        sc=score_answer(ans,eq["expected_keywords"])
                        results.append({"question":eq["question"],"category":eq["category"],"answer":ans,"score":sc})
                    except Exception as exc:
                        results.append({"question":eq["question"],"category":eq["category"],"answer":f"Error: {exc}","score":{"recall":0,"hits":0,"total":0,"score_pct":0}})
                    prog.progress((i+1)/len(EVAL_QUESTIONS),f"Q{i+1}/{len(EVAL_QUESTIONS)}")
                prog.empty()
                if results:
                    avg=sum(r["score"]["score_pct"] for r in results)/len(results)
                    color="#4ade80" if avg>=70 else ("#F0C040" if avg>=40 else "#f87171")
                    st.markdown(f'<div style="background:#120E1A;border:1px solid rgba(139,58,139,.22);border-radius:10px;padding:.9rem 1.1rem;margin-bottom:.8rem;">'
                        f'<div style="font-family:Space Mono,monospace;font-size:.5rem;letter-spacing:.14em;text-transform:uppercase;color:#4A3858;">Overall Recall Score</div>'
                        f'<div style="font-family:Cormorant Garamond,serif;font-size:2rem;font-weight:300;color:{color};">{avg:.1f}%</div>'
                        f'<div style="font-family:Space Mono,monospace;font-size:.48rem;color:#4A3858;">{len(results)} questions evaluated</div></div>', unsafe_allow_html=True)
                    st.dataframe(pd.DataFrame([{"Question":r["question"][:55]+"…","Category":r["category"],"Score":f"{r['score']['score_pct']}%","Hits":f"{r['score']['hits']}/{r['score']['total']}"} for r in results]), use_container_width=True, hide_index=True)
                    with st.expander("📋 Full answers"):
                        for r in results:
                            st.markdown(f'<div style="background:#120E1A;border:1px solid rgba(139,58,139,.18);border-radius:8px;padding:.65rem .85rem;margin-bottom:.4rem;">'
                                f'<div style="font-family:Space Mono,monospace;font-size:.56rem;color:#C084C8;margin-bottom:.25rem;">{r["question"]}</div>'
                                f'<div style="font-size:.78rem;color:#9A8AAA;">{r["answer"][:450]}</div>'
                                f'<div style="font-family:Space Mono,monospace;font-size:.5rem;color:#4A3858;margin-top:.25rem;">score: {r["score"]["score_pct"]}% · {r["score"]["hits"]}/{r["score"]["total"]} keywords</div></div>', unsafe_allow_html=True)

    # ── Doc Viewer ────────────────────────────────────────────────────────────
    with sub_tabs[4]:
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.16em;text-transform:uppercase;color:#C084C8;margin-bottom:.7rem;">Document Viewer & Quick Navigation</div>', unsafe_allow_html=True)
        doc_text_map = st.session_state.get("doc_text_map",{})
        if not doc_text_map:
            st.info("No documents loaded.")
        else:
            sel_doc=st.selectbox("Select document",list(doc_text_map.keys()),label_visibility="collapsed",key="dv_sel")
            if sel_doc:
                text=doc_text_map[sel_doc]
                # Quick nav
                sections={"Summary":0,"Revenue":text.lower().find("revenue"),"Risk":text.lower().find("risk"),"Cash Flow":text.lower().find("cash flow"),"Balance Sheet":text.lower().find("balance sheet")}
                sections={k:max(0,v) for k,v in sections.items()}
                st.markdown('<div class="qnav-row">'+''.join(f'<span class="qnav-btn">⊕ {k}</span>' for k in sections)+'</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:.5rem;color:#4A3858;margin-bottom:.5rem;">{len(text):,} characters · {len(text.split()):,} words</div>', unsafe_allow_html=True)
                # Show text in scrollable area
                preview_start = 0
                show_chars = 8000
                snippet = text[preview_start:preview_start+show_chars]
                st.text_area("Document content", snippet, height=420, label_visibility="collapsed", key="dv_text")
                if len(text) > show_chars:
                    st.caption(f"Showing first {show_chars:,} of {len(text):,} characters")

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""<div style="padding:0 0 .7rem;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.35rem;font-weight:300;color:#EDE8F5;line-height:1.1;">
        RAG <em style="color:#C084C8;font-style:italic;">Assistant</em></div>
      <div style="font-family:'Space Mono',monospace;font-size:.5rem;letter-spacing:.22em;color:#4A3858;text-transform:uppercase;margin-top:.3rem;">
        Financial Intelligence · v5</div></div>""", unsafe_allow_html=True)

    # API Keys
    st.markdown('<div class="sb-lbl" style="border-top:none;padding-top:0;margin-top:0;">API Keys</div>', unsafe_allow_html=True)
    default_key=st.secrets.get("GROQ_API_KEY",os.getenv("GROQ_API_KEY","")) if hasattr(st,"secrets") else os.getenv("GROQ_API_KEY","")
    if default_key:
        GROQ_API_KEY=default_key
        st.markdown('<div class="key-ok"><div class="key-dot"></div>Groq Key Active</div>', unsafe_allow_html=True)
    else:
        GROQ_API_KEY=st.text_input("Groq API Key",type="password",placeholder="gsk_…",label_visibility="collapsed",key="groq_key")
        st.markdown("<span style='font-family:Space Mono,monospace;font-size:.5rem;color:#4A3858;'>console.groq.com → free key</span>", unsafe_allow_html=True)
        if GROQ_API_KEY: os.environ["GROQ_API_KEY"]=GROQ_API_KEY

    OPENAI_KEY=os.getenv("OPENAI_API_KEY","")
    if not OPENAI_KEY:
        OPENAI_KEY=st.text_input("OpenAI Key (optional)",type="password",placeholder="sk-…",label_visibility="collapsed",key="oai_key")
        st.markdown("<span style='font-family:Space Mono,monospace;font-size:.5rem;color:#4A3858;'>Optional · for GPT-4o models</span>", unsafe_allow_html=True)
        if OPENAI_KEY: os.environ["OPENAI_API_KEY"]=OPENAI_KEY
    else:
        st.markdown('<div class="key-ok" style="margin-top:.25rem;"><div class="key-dot"></div>OpenAI Key Active</div>', unsafe_allow_html=True)

    # Model selector
    st.markdown('<div class="sb-lbl">Model</div>', unsafe_allow_html=True)
    model_opts=list(MODEL_REGISTRY.keys())
    model_lbls=[f"{MODEL_REGISTRY[m]['label']} {MODEL_REGISTRY[m]['speed']}" for m in model_opts]
    cur_idx=model_opts.index(st.session_state.active_model) if st.session_state.active_model in model_opts else 0
    chosen_lbl=st.selectbox("model",model_lbls,index=cur_idx,label_visibility="collapsed",key="model_sel")
    chosen_model=model_opts[model_lbls.index(chosen_lbl)]
    st.session_state.active_model=chosen_model
    cfg=MODEL_REGISTRY[chosen_model]
    st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:.48rem;color:#4A3858;margin-top:.15rem;">{cfg["quality"]} · ctx {cfg["ctx"]//1000}k · {cfg["cost"]}</div>', unsafe_allow_html=True)

    # Output Mode
    st.markdown('<div class="sb-lbl">Answer Format</div>', unsafe_allow_html=True)
    out_mode=st.radio("fmt",["Narrative","Executive Summary","JSON"],
                      index=["Narrative","Executive Summary","JSON"].index(st.session_state.output_mode),
                      label_visibility="collapsed",horizontal=True,key="out_mode_r")
    st.session_state.output_mode=out_mode

    # Rate limit bar
    bucket=_get_bucket(); tl=int(bucket._tokens); pf=tl/bucket._cap
    bc2="#4ade80" if pf>0.5 else ("#f0c040" if pf>0.2 else "#f87171")
    st.markdown(f'<div style="margin:.5rem 0 .3rem;"><div style="font-family:Space Mono,monospace;font-size:.48rem;letter-spacing:.16em;color:#4A3858;text-transform:uppercase;margin-bottom:.2rem;">Market Data Rate</div>'
        f'<div style="background:#0D0B12;border:1px solid rgba(139,58,139,.2);border-radius:3px;height:3px;overflow:hidden;"><div style="height:100%;width:{int(pf*100)}%;background:{bc2};border-radius:3px;"></div></div>'
        f'<div style="font-family:Space Mono,monospace;font-size:.46rem;color:#4A3858;margin-top:.12rem;">{tl}/{bucket._cap} · resets/60s</div></div>', unsafe_allow_html=True)

    # Knowledge base — file list (clickable)
    if st.session_state.file_names:
        st.markdown('<div class="sb-lbl">Knowledge Base</div>', unsafe_allow_html=True)
        cc1,cc2=st.columns(2)
        cc1.metric("Chunks",st.session_state.chunk_count)
        cc2.metric("Docs",st.session_state.uploaded_docs)
        for fn in st.session_state.file_names:
            short=fn[:20]+"…" if len(fn)>20 else fn
            is_active=fn==st.session_state.active_doc
            pill_cls="doc-pill active-doc" if is_active else "doc-pill"
            st.markdown(f'<div class="{pill_cls}"><div class="doc-dot"></div>{short}</div>', unsafe_allow_html=True)
            if st.button("📄",key=f"sw_{fn[:12]}",help=f"Switch to {fn}"):
                st.session_state.active_doc=fn; st.rerun()

    # Quick Ask
    st.markdown('<div class="sb-lbl">Quick Ask</div>', unsafe_allow_html=True)
    for q_item in ["What is USD/INR today?","Gold price today?","Bitcoin vs Ethereum?","What was total revenue?","Main risk factors?","EPS change YoY?","Free cash flow?"]:
        if st.button(q_item,use_container_width=True,key=f"qa_{q_item[:14]}"):
            st.session_state["_prefill"]=q_item

    # Actions
    st.markdown('<div class="sb-lbl">Actions</div>', unsafe_allow_html=True)
    if st.session_state.messages:
        md_export=export_chat_markdown(st.session_state.messages)
        st.download_button("⬇ Export Chat (MD)",md_export,"chat_export.md","text/markdown",use_container_width=True,key="dl_md")
        jx_export=export_chat_json(st.session_state.messages)
        st.download_button("⬇ Export Chat (JSON)",jx_export,"chat_export.json","application/json",use_container_width=True,key="dl_json")
    if st.button("✕  Clear Conversation",use_container_width=True,key="clr_conv"):
        st.session_state.messages=[]; st.rerun()
    show_lbl="👁 Hide Chat" if st.session_state.show_chat else "👁 Show Chat"
    if st.button(show_lbl,use_container_width=True,key="toggle_chat"):
        st.session_state.show_chat=not st.session_state.show_chat; st.rerun()

    # Analytics inline toggle (only when docs loaded)
    if st.session_state.file_names:
        _a_lbl = "📊 Hide Analytics" if st.session_state.get("show_analytics") else "📊 Show Analytics"
        if st.button(_a_lbl, use_container_width=True, key="tog_analytics"):
            st.session_state["show_analytics"] = not st.session_state.get("show_analytics", False)
            st.rerun()

    # FinBERT info badge
    st.markdown(
        '<div style="background:rgba(240,192,64,.07);border:1px solid rgba(240,192,64,.22);'
        'border-radius:6px;padding:.4rem .6rem;margin:.5rem 0;">'
        '<div style="font-family:Space Mono,monospace;font-size:.48rem;letter-spacing:.1em;'
        'text-transform:uppercase;color:#F0C040;margin-bottom:.1rem;">🧠 FinBERT Embeddings</div>'
        '<div style="font-family:Syne,sans-serif;font-size:.58rem;color:#9A8AAA;line-height:1.5;">'
        'yiyanghkust/finbert-pretrain<br>'
        'Trained on SEC filings, earnings &amp; financial news</div></div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# MAIN PAGE — TAB STRUCTURE
# ─────────────────────────────────────────────────────────────────────────────
_main_tabs = st.tabs(["📈 Markets & Chat", "📊 Analytics Dashboard"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MARKETS & CHAT
# ══════════════════════════════════════════════════════════════════════════════
with _main_tabs[0]:

    # ── CHANGE 2: Sticky chat icon bar — always visible at the very top ──────
    _docs  = st.session_state.uploaded_docs
    _model = st.session_state.get("active_model","llama-3.3-70b-versatile").split("-")[0].capitalize()
    _embed = "FinBERT" if _docs else "—"
    _status = (f"{_docs} doc{'s' if _docs!=1 else ''} · {st.session_state.chunk_count} chunks indexed"
               if _docs else "No documents — ask about live markets")
    st.markdown(f"""
    <div class="chat-fab-bar">
      <div class="chat-fab-icon">💬</div>
      <span class="chat-fab-label">Chat</span>
      <div class="chat-fab-sep"></div>
      <span class="chat-fab-model">🧠 FinBERT · {_model}</span>
      <div class="chat-fab-live"></div>
      <span class="chat-fab-status">{_status} · scroll ↓ to chat</span>
    </div>""", unsafe_allow_html=True)

    # ── Hero ─────────────────────────────────────────────────────────────────
    st.markdown("""<div class="rag-header">
      <div class="rag-kicker">Financial Intelligence Platform</div>
      <h1>Interrogate Your<br><em>Financial Documents</em></h1>
      <p>Semantic search · AI-powered analysis · Live markets · Multi-format ingestion</p>
      <div class="badge-row">
        <span class="badge v">Hybrid Retrieval</span>
        <span class="badge v">Multi-Model</span>
        <span class="badge fb">🧠 FinBERT Embeddings</span>
        <span class="badge v">Cross-Encoder Rerank</span>
        <span class="badge">Groq · OpenAI</span>
        <span class="badge g">Live Data</span>
      </div></div>""", unsafe_allow_html=True)

    # ── Stat strip ───────────────────────────────────────────────────────────
    chunks=st.session_state.chunk_count; docs=st.session_state.uploaded_docs
    msgs=len(st.session_state.messages)//2; mdl=MODEL_REGISTRY[st.session_state.active_model]["label"]
    st.markdown(f"""<div class="stat-strip">
      <div class="stat-cell"><div class="stat-lbl">Model</div><div class="stat-val-mono">{mdl}</div></div>
      <div class="stat-cell"><div class="stat-lbl">Chunks</div><div class="stat-val {'active' if chunks else ''}">{chunks or '—'}</div></div>
      <div class="stat-cell"><div class="stat-lbl">Documents</div><div class="stat-val {'active' if docs else ''}">{docs or '—'}</div></div>
      <div class="stat-cell"><div class="stat-lbl">Exchanges</div><div class="stat-val {'active' if msgs else ''}">{msgs or '—'}</div></div>
      <div class="stat-cell"><div class="stat-lbl">Format</div><div class="stat-val-mono">{st.session_state.output_mode[:8]}</div></div>
    </div>""", unsafe_allow_html=True)

    # ── Market Mood ───────────────────────────────────────────────────────────
    fng=fetch_fear_greed(); fng_val=fng["value"]; fng_label=fng["label"]
    INDEX_SYMS={"^GSPC":{"name":"S&P 500","flag":"🇺🇸"},"^IXIC":{"name":"NASDAQ","flag":"🇺🇸"},"^FTSE":{"name":"FTSE","flag":"🇬🇧"},"^NSEI":{"name":"NIFTY 50","flag":"🇮🇳"},"^N225":{"name":"Nikkei","flag":"🇯🇵"},"^GDAXI":{"name":"DAX","flag":"🇩🇪"}}
    idx_q=fetch_multi_quotes(tuple(INDEX_SYMS.keys()))
    idx_chips=""
    for sym,meta in INDEX_SYMS.items():
        info=idx_q.get(sym)
        if info:
            arrow="▲" if info["pct"]>=0 else "▼"; cls="up" if info["pct"]>=0 else "down"
            idx_chips+=f'<div class="mood-idx-chip"><div class="mood-idx-name">{meta["flag"]} {meta["name"]}</div><div class="mood-idx-val">{info["price"]:,.0f}</div><div class="mood-idx-chg {cls}">{arrow} {abs(info["pct"]):.2f}%</div></div>'
    mood_color="#f87171" if fng_val<25 else ("#fb923c" if fng_val<45 else ("#facc15" if fng_val<55 else ("#86efac" if fng_val<75 else "#4ade80")))
    st.markdown(f"""<div class="mood-bar-wrap">
      <div class="mood-title">◈ Market Mood &amp; Global Indices</div>
      <div style="display:flex;align-items:center;gap:.9rem;margin-bottom:.6rem;">
        <div><div style="display:flex;align-items:baseline;gap:.35rem;">
          <span class="mood-index" style="color:{mood_color};">{fng_val}</span>
          <span style="font-family:'Space Mono',monospace;font-size:.6rem;letter-spacing:.1em;color:{mood_color};">{fng_label}</span>
        </div><div style="font-family:'Space Mono',monospace;font-size:.48rem;color:#4A3858;margin-top:.15rem;">Crypto Fear &amp; Greed</div></div>
        <div style="flex:1;"><div class="mood-track"><div class="mood-needle" style="left:{fng_val}%;"></div></div>
          <div class="mood-labels"><span>Fear</span><span>Neutral</span><span>Greed</span></div></div>
      </div><div class="mood-indices">{idx_chips}</div></div>""", unsafe_allow_html=True)

    # ── News Carousels ────────────────────────────────────────────────────────
    news_items=get_all_news(); policy_items=get_policy_news()
    car1,car2=st.columns(2)
    with car1:
        if news_items: components.html(build_carousel_html(news_items,False,390),height=390,scrolling=False)
        else: st.info("News unavailable.")
    with car2:
        if policy_items: components.html(build_carousel_html(policy_items,True,390),height=390,scrolling=False)
        else: st.info("Policy news unavailable.")

    # ── Commodities ───────────────────────────────────────────────────────────
    COMMODITY_SYMS={"GC=F":("Gold","$/oz","🪙",2),"SI=F":("Silver","$/oz","⚪",3),"CL=F":("Crude Oil","$/bbl","🛢️",2),"PL=F":("Platinum","$/oz","💎",2),"HG=F":("Copper","$/lb","🟤",3)}
    comm_q=fetch_multi_quotes(tuple(COMMODITY_SYMS.keys()))
    comm_chips="".join(make_chip_html(sym,f"{n}·{u}",info["price"],info["pct"],decimals=d,icon=ic) for sym,(n,u,ic,d) in COMMODITY_SYMS.items() if (info:=comm_q.get(sym)))
    if comm_chips:
        st.markdown(f'<div class="comm-panel"><div class="v-panel-title" style="margin-bottom:.7rem;">Precious Metals &amp; Commodities</div><div class="chips-row">{comm_chips}</div><div style="font-family:Space Mono,monospace;font-size:.48rem;color:#4A3858;margin-top:.55rem;text-align:right;">Futures · Yahoo Finance · 60s</div></div>', unsafe_allow_html=True)

    # ── Crypto ────────────────────────────────────────────────────────────────
    CRYPTO_SYMS={"BTC-USD":("Bitcoin","BTC","₿",2),"ETH-USD":("Ethereum","ETH","Ξ",2),"BNB-USD":("BNB","BNB","🔶",2),"SOL-USD":("Solana","SOL","◎",2),"XRP-USD":("XRP","XRP","✕",4),"DOGE-USD":("Dogecoin","DOGE","🐕",5)}
    crypto_q=fetch_multi_quotes(tuple(CRYPTO_SYMS.keys()))
    crypto_chips="".join(make_chip_html(ticker,name,info["price"],info["pct"],decimals=dec,icon=icon) for sym,(name,ticker,icon,dec) in CRYPTO_SYMS.items() if (info:=crypto_q.get(sym)))
    if crypto_chips:
        st.markdown(f'<div class="crypto-panel"><div class="v-panel-title" style="margin-bottom:.7rem;">Crypto Markets</div><div class="chips-row">{crypto_chips}</div><div style="font-family:Space Mono,monospace;font-size:.48rem;color:#4A3858;margin-top:.55rem;text-align:right;">Spot · Yahoo Finance · 60s</div></div>', unsafe_allow_html=True)

    # ── Live Stock Chart ──────────────────────────────────────────────────────
    st.markdown('<div class="v-panel">', unsafe_allow_html=True)
    st.markdown('<div class="v-panel-title">Live Stock Chart</div>', unsafe_allow_html=True)
    col_sym,col_rng=st.columns([4,1])
    with col_sym:
        symbols=st.multiselect("syms",["AAPL","MSFT","NVDA","GOOGL","AMZN","TSLA","META","TSM","RELIANCE.NS","TCS.NS","INFY.NS"],default=["AAPL","MSFT","NVDA","TSLA"],label_visibility="collapsed")
    with col_rng:
        rng=st.selectbox("rng",["1D","5D","1M","3M","6M","1Y"],index=2,label_visibility="collapsed")
    pm={"1D":"1d","5D":"5d","1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y"}
    im={"1D":"5m","5D":"30m","1M":"1d","3M":"1d","6M":"1d","1Y":"1wk"}
    if symbols:
        sq=fetch_multi_quotes(tuple(symbols))
        cps="".join(
            f'<div style="display:flex;flex-direction:column;align-items:center;background:#120E1A;border:1px solid rgba(139,58,139,.22);border-radius:7px;padding:.4rem .65rem;min-width:74px;font-family:Space Mono,monospace;">'
            f'<span style="font-size:.58rem;color:#C084C8;font-weight:700;">{sym}</span>'
            f'<span style="font-size:.7rem;color:#EDE8F5;margin-top:.08rem;">${info["price"]:,.2f}</span>'
            f'<span style="font-size:.54rem;color:{"#4ade80" if info["pct"]>=0 else "#f87171"};">{"▲" if info["pct"]>=0 else "▼"} {abs(info["pct"]):.2f}%</span></div>'
            for sym in symbols if (info:=sq.get(sym)))
        if cps: st.markdown(f'<div style="display:flex;gap:.45rem;flex-wrap:wrap;margin-bottom:.7rem;">{cps}</div>', unsafe_allow_html=True)
        chart=pd.DataFrame()
        for sym in symbols:
            s=fetch_yahoo_series(sym,pm[rng],im[rng])
            if s is not None and not s.empty: chart[sym]=s
        if not chart.empty:
            normed=(chart.dropna(how="all").ffill()/chart.dropna(how="all").ffill().iloc[0]-1)*100
            st.line_chart(normed,height=220,use_container_width=True)
            st.caption(f"% return from period start · {rng} · Yahoo Finance")
        else: st.warning("Chart data unavailable.")
    else: st.info("Select at least one symbol.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Currency Panel ────────────────────────────────────────────────────────
    ALL_FX={"USDINR=X":{"label":"USD/INR","flag":"🇮🇳","name":"Indian Rupee","invert":False},"USDJPY=X":{"label":"USD/JPY","flag":"🇯🇵","name":"Japanese Yen","invert":False},"USDCNY=X":{"label":"USD/CNY","flag":"🇨🇳","name":"Chinese Yuan","invert":False},"EURUSD=X":{"label":"EUR/USD","flag":"🇪🇺","name":"Euro","invert":True},"GBPUSD=X":{"label":"GBP/USD","flag":"🇬🇧","name":"British Pound","invert":True},"USDCHF=X":{"label":"USD/CHF","flag":"🇨🇭","name":"Swiss Franc","invert":False},"USDKRW=X":{"label":"USD/KRW","flag":"🇰🇷","name":"S. Korean Won","invert":False},"USDBRL=X":{"label":"USD/BRL","flag":"🇧🇷","name":"Brazilian Real","invert":False},"USDCAD=X":{"label":"USD/CAD","flag":"🇨🇦","name":"Canadian Dollar","invert":False},"USDSGD=X":{"label":"USD/SGD","flag":"🇸🇬","name":"Singapore Dollar","invert":False},"USDHKD=X":{"label":"USD/HKD","flag":"🇭🇰","name":"HK Dollar","invert":False},"USDMXN=X":{"label":"USD/MXN","flag":"🇲🇽","name":"Mexican Peso","invert":False},"USDTRY=X":{"label":"USD/TRY","flag":"🇹🇷","name":"Turkish Lira","invert":False},"USDZAR=X":{"label":"USD/ZAR","flag":"🇿🇦","name":"SA Rand","invert":False},"USDAED=X":{"label":"USD/AED","flag":"🇦🇪","name":"UAE Dirham","invert":False},"USDNOK=X":{"label":"USD/NOK","flag":"🇳🇴","name":"NOK","invert":False},"USDSEK=X":{"label":"USD/SEK","flag":"🇸🇪","name":"SEK","invert":False},"USDNZD=X":{"label":"USD/NZD","flag":"🇳🇿","name":"NZD","invert":False}}
    fx_opts={f"{m['flag']} {m['label']} · {m['name']}":sym for sym,m in ALL_FX.items()}
    def_lbls=[k for k,v in fx_opts.items() if v in ("USDINR=X","USDJPY=X","USDCNY=X","EURUSD=X","GBPUSD=X","USDCHF=X")]
    st.markdown('<div class="fx-panel"><div class="v-panel-title" style="margin-bottom:.7rem;">Currencies vs USD</div>', unsafe_allow_html=True)
    fx_r1,fx_r2=st.columns([5,1])
    with fx_r1: sel_lbls=st.multiselect("fx",list(fx_opts.keys()),default=def_lbls,label_visibility="collapsed",key="fx_sel")
    with fx_r2: fx_rng=st.selectbox("fxr",["1M","3M","6M","1Y"],index=0,label_visibility="collapsed",key="fx_rng")
    sel_syms=[fx_opts[l] for l in sel_lbls]
    st.session_state["fx_select_syms"]=sel_syms
    fxpm={"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y"}; fxim={"1M":"1d","3M":"1d","6M":"1d","1Y":"1wk"}
    if sel_syms:
        fx_chart=pd.DataFrame()
        for sym in sel_syms:
            meta=ALL_FX[sym]; s=fetch_yahoo_series(sym,fxpm[fx_rng],fxim[fx_rng])
            if s is not None and not s.empty:
                if meta["invert"]: s=1.0/s
                s=(s/s.iloc[0]-1)*100; s.name=meta["flag"]+" "+meta["label"]; fx_chart[s.name]=s
        if not fx_chart.empty:
            st.line_chart(fx_chart.dropna(how="all").ffill(),height=210,use_container_width=True)
            st.caption(f"% change from {fx_rng} start · EUR/GBP inverted · Yahoo Finance")
        fx_q=fetch_multi_quotes(tuple(sel_syms))
        fx_cps=[]
        for sym in sel_syms:
            meta=ALL_FX[sym]; info=fx_q.get(sym)
            if info:
                r=info["price"]; rs=f"{r:,.2f}" if r>=10 else f"{r:.4f}"
                p=info["pct"]; arrow="▲" if p>0.005 else ("▼" if p<-0.005 else "●"); cls="up" if p>0.005 else ("down" if p<-0.005 else "flat")
                fx_cps.append(f'<div class="price-chip"><div class="pc-sym">{meta["flag"]} {meta["label"]}</div><div class="pc-name">{meta["name"]}</div><div class="pc-val">{rs}</div><div class="pc-chg {cls}">{arrow} {abs(p):.3f}%</div></div>')
        if fx_cps:
            now_ist=_dt.datetime.utcnow()+_dt.timedelta(hours=5,minutes=30)
            st.markdown(f'<div class="chips-row" style="margin-top:.65rem;">'+"".join(fx_cps)+f'</div><div style="font-family:Space Mono,monospace;font-size:.48rem;color:#4A3858;margin-top:.5rem;text-align:right;">Live · {now_ist.strftime("%H:%M")} IST · 60s</div>', unsafe_allow_html=True)
    else: st.info("Select at least one currency pair.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── India News ────────────────────────────────────────────────────────────
    st.markdown("""<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.7rem;">
      <span style="display:inline-block;width:3px;height:1.3rem;background:linear-gradient(180deg,#6B2D6B,#C084C8);border-radius:2px;flex-shrink:0;"></span>
      <span style="font-family:'Cormorant Garamond',serif;font-size:1.25rem;font-weight:300;color:#EDE8F5;">India News &amp; Policy</span>
    </div>""", unsafe_allow_html=True)
    nc1,nc2,nc3=st.columns([3,2,1])
    with nc1: sel_src=st.multiselect("srcs",list(NEWS_SOURCES.keys()),default=["📰 Economic Times","📰 Business Standard","🏛️ RBI"],label_visibility="collapsed",key="news_srcs")
    with nc2: nf=st.selectbox("nflt",["All","Markets","Policy"],index=0,label_visibility="collapsed",key="news_flt")
    with nc3: npp=st.selectbox("npp",[3,5,8],index=0,label_visibility="collapsed",key="news_pp")
    act_srcs=[s for s in sel_src if nf=="All" or NEWS_SOURCES[s]["tag"]==nf]
    if act_srcs:
        all_arts=[]
        for sn in act_srcs:
            arts=fetch_rss(NEWS_SOURCES[sn]["rss"],npp)
            for a in arts: a["source"]=sn; a["src_tag"]=NEWS_SOURCES[sn]["tag"]
            all_arts.extend(arts)
        if all_arts:
            cl,cr=st.columns(2)
            with cl: st.markdown("".join(render_news_card(a) for a in all_arts[0::2]), unsafe_allow_html=True)
            with cr: st.markdown("".join(render_news_card(a) for a in all_arts[1::2]), unsafe_allow_html=True)
            now_ist2=_dt.datetime.utcnow()+_dt.timedelta(hours=5,minutes=30)
            st.markdown(f'<div style="font-family:Space Mono,monospace;font-size:.48rem;color:#4A3858;text-align:right;">Fetched {now_ist2.strftime("%H:%M")} IST · {len(all_arts)} articles · 10min cache</div>', unsafe_allow_html=True)
        else: st.info("No articles — try different sources.")
    else: st.info("Select at least one source.")

    st.markdown("<hr style='border-color:rgba(139,58,139,.12);margin:1.2rem 0;'>", unsafe_allow_html=True)

    # ── CHAT SECTION ──────────────────────────────────────────────────────────
    if st.session_state.show_chat:

        st.markdown("""<div style="font-family:'Cormorant Garamond',serif;font-size:1.25rem;font-weight:300;color:#EDE8F5;margin:.4rem 0 .7rem;">
          Ask Anything — Markets, Currencies, Gold &amp; Documents</div>""", unsafe_allow_html=True)

        if not st.session_state.messages:
            st.markdown("""<div class="empty"><div class="empty-orb">◈</div>
              <div class="empty-title">Ready without uploads</div>
              <div class="empty-sub">Ask about <strong>live stocks</strong>, <strong>gold</strong>,
              <strong>crypto</strong>, <strong>FX rates</strong> — no documents needed.<br><br>
              Use <strong>＋</strong> to upload financial reports for document analysis.</div></div>""", unsafe_allow_html=True)

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander(f"↳ {len(msg['sources'])} source(s) — click to inspect"):
                        for src in msg["sources"]:
                            sc=src["score"]; sc_pct=int(sc*100)
                            bar_c2="#4ade80" if sc>0.75 else ("#F0C040" if sc>0.5 else "#f87171")
                            exp=("High relevance" if sc>0.75 else ("Moderate relevance" if sc>0.5 else "Low relevance"))
                            tags_str=src.get("tags","")
                            tag_pills="".join(f'<span style="background:rgba(192,132,200,.1);border:1px solid rgba(192,132,200,.28);font-family:Space Mono,monospace;font-size:.46rem;padding:.06rem .28rem;border-radius:3px;color:#C084C8;margin-right:.18rem;">{t}</span>' for t in (tags_str.split("|") if tags_str else [])[:3])
                            st.markdown(
                                f'<div class="src-card">'
                                f'<div class="src-name">📄 {src["filename"]}</div>'
                                f'<div class="src-score">{exp} · {sc:.3f}</div>'
                                f'<div class="src-bar" style="width:{sc_pct}%;background:{bar_c2};"></div>'
                                f'<div style="margin-bottom:.2rem;">{tag_pills}</div>'
                                f'<div class="src-preview">{src["preview"]}…</div></div>',
                                unsafe_allow_html=True)

        # Upload drawer
        if st.session_state.show_upload:
            st.markdown('<div class="upload-drawer"><div class="upload-drawer-title">◈ Upload Financial Documents</div>', unsafe_allow_html=True)
            inline_files=st.file_uploader("Upload",type=["pdf","txt","csv","xlsx","xls","json","html"],accept_multiple_files=True,label_visibility="collapsed",key="drawer_upload")
            # Tag input
            tag_input=st.text_input("Optional tags (comma-separated)","",label_visibility="collapsed",placeholder="e.g. Q3 2024, Apple, 10-K",key="tag_inp")
            ci,cc=st.columns([3,1])
            with ci:
                if inline_files and st.button("⬆  Ingest Documents",use_container_width=True,key="drawer_ingest"):
                    if not GROQ_API_KEY: st.error("Enter your Groq API key first.")
                    else:
                        user_tags={}
                        if tag_input:
                            tags_list=[t.strip() for t in tag_input.split(",") if t.strip()]
                            for f in inline_files: user_tags[f.name]=tags_list
                        try:
                            n=ingest_documents(inline_files)
                            st.success(f"✓ {n} chunks from {len(inline_files)} file(s)")
                            st.session_state.show_upload=False; st.rerun()
                        except Exception as e: st.error(str(e))
            with cc:
                if st.button("✕ Close",use_container_width=True,key="drawer_close"):
                    st.session_state.show_upload=False; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # Chat input bar
        bar1,bar2=st.columns([1,16],gap="small")
        with bar1:
            if st.button("＋",key="plus_btn",use_container_width=True,help="Upload documents (PDF, Excel, CSV, JSON, HTML)"):
                st.session_state.show_upload=not st.session_state.show_upload; st.rerun()
        with bar2:
            prefill=st.session_state.pop("_prefill",None)
            question=st.chat_input("Ask about stocks, gold, crypto, currencies, or your documents…")

        q=prefill or question

        if q:
            if not GROQ_API_KEY: st.error("Please enter your Groq API key in the sidebar."); st.stop()
            with st.chat_message("user"): st.markdown(q)
            st.session_state.messages.append({"role":"user","content":q})

            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    try:
                        from openai import OpenAI
                        active_model=st.session_state.active_model
                        cfg2=MODEL_REGISTRY[active_model]
                        api_key_to_use=OPENAI_KEY if cfg2["provider"]=="openai" else GROQ_API_KEY
                        oai=OpenAI(api_key=api_key_to_use,base_url=cfg2["base_url"])

                        # Live market context
                        stock_lines=[f"  {sym}: ${info['price']:,.2f} ({'▲' if info['pct']>=0 else '▼'}{abs(info['pct']):.2f}%)" for sym in symbols if (info:=fetch_quote(sym))]
                        comm_lines=[f"  {n}: ${info['price']:,.{d}f} {u} ({'+' if info['pct']>=0 else ''}{info['pct']:.2f}%)" for sym,(n,u,ic,d) in COMMODITY_SYMS.items() if (info:=fetch_quote(sym))]
                        crypto_lines=[f"  {ticker}: ${info['price']:,.{dec}f} ({'+' if info['pct']>=0 else ''}{info['pct']:.2f}%)" for sym,(name,ticker,icon,dec) in CRYPTO_SYMS.items() if (info:=fetch_quote(sym))]
                        fx_lines=[]
                        for _fxsym in st.session_state.get("fx_select_syms",("USDINR=X","USDJPY=X")):
                            _fxi=fetch_quote(_fxsym)
                            if _fxi:
                                _p=_fxi["price"]; _rs=f"{_p:,.2f}" if _p>=10 else f"{_p:.4f}"
                                fx_lines.append(f"  {ALL_FX.get(_fxsym,{}).get('label',_fxsym)}: {_rs} ({'+' if _fxi['pct']>=0 else ''}{_fxi['pct']:.3f}%)")
                        utc_now=_dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
                        live_ctx=f"""=== LIVE MARKET DATA ({utc_now}) ===
STOCKS:\n{chr(10).join(stock_lines) or '  (none)'}
COMMODITIES:\n{chr(10).join(comm_lines) or '  (unavailable)'}
CRYPTO:\n{chr(10).join(crypto_lines) or '  (unavailable)'}
CURRENCIES (vs USD):\n{chr(10).join(fx_lines) or '  (unavailable)'}
MARKET MOOD: Fear & Greed = {fng_val} ({fng_label})""".strip()

                        # Document context with hybrid retrieval
                        doc_ctx=""; sources_data=[]
                        if st.session_state.vectorstore:
                            import time as _t2; t0=_t2.monotonic()
                            vs=st.session_state.vectorstore
                            # Use hybrid retrieval if available
                            try:
                                all_res=vs["collection"].get(include=["documents","embeddings","metadatas"])
                                chunks_all=all_res["documents"]; embs_all=all_res["embeddings"]; metas_all=all_res["metadatas"]
                                q_emb=vs["model"].encode([q],normalize_embeddings=True).tolist()[0]
                                hr=HybridRetriever(chunks_all,embs_all)
                                hits=hr.retrieve(q,q_emb,n=5,bm25_weight=0.3,rerank=False)
                                doc_ctx="\n---\n".join(f"[{metas_all[h['idx']].get('filename','?')}]\n{h['chunk']}" for h in hits)
                                sources_data=[{"filename":metas_all[h["idx"]].get("filename","?"),"score":round(h["score"],3),"preview":h["chunk"][:220],"tags":metas_all[h["idx"]].get("tags",""),"chunk_idx":metas_all[h["idx"]].get("chunk",0)} for h in hits]
                            except:
                                q_emb2=vs["model"].encode([q],normalize_embeddings=True).tolist()
                                res=vs["collection"].query(query_embeddings=q_emb2,n_results=5,include=["documents","metadatas","distances"])
                                cks,mts,dts=res["documents"][0],res["metadatas"][0],res["distances"][0]
                                doc_ctx="\n---\n".join(f"[{m['filename']}]\n{c}" for c,m in zip(cks,mts))
                                sources_data=[{"filename":m["filename"],"score":round(1-d/2,3),"preview":c[:220],"tags":m.get("tags",""),"chunk_idx":m.get("chunk",0)} for c,m,d in zip(cks,mts,dts)]
                            lat=round((_t2.monotonic()-t0)*1000)
                            st.session_state.retrieval_stats.append({"query":q[:40],"n":len(sources_data),"top_score":sources_data[0]["score"] if sources_data else 0,"latency_ms":lat})

                        # Format modifier in system prompt
                        fmt_instruction=""
                        if st.session_state.output_mode=="Executive Summary":
                            fmt_instruction=" Respond in executive summary format: 3-5 bullet points, key numbers bolded, total <200 words."
                        elif st.session_state.output_mode=="JSON":
                            fmt_instruction=' Respond ONLY with valid JSON. Schema: {"summary": str, "key_metrics": {metric: value}, "sources_used": [filename]}. No markdown fences.'

                        sys_prompt=(f"You are an expert financial analyst with real-time data access. "
                            "Use live market data for market questions. For document questions, cite specific numbers and page references. "
                            f"Be precise, never fabricate.{fmt_instruction}")
                        user_msg=(f"{live_ctx}\n\n=== DOCUMENT CONTEXT ===\n{doc_ctx}\n\nQuestion: {q}" if doc_ctx else f"{live_ctx}\n\nQuestion: {q}")

                        resp=oai.chat.completions.create(
                            model=active_model,
                            messages=[{"role":"system","content":sys_prompt},
                                      *[{"role":m["role"],"content":m["content"]} for m in st.session_state.messages[:-1]],
                                      {"role":"user","content":user_msg}],
                            temperature=0.12,max_tokens=1800)
                        answer=resp.choices[0].message.content; tokens=resp.usage.total_tokens

                        if st.session_state.output_mode=="JSON":
                            try:
                                parsed=json.loads(answer)
                                st.json(parsed)
                            except: st.markdown(answer)
                        else: st.markdown(answer)

                        if sources_data:
                            with st.expander(f"↳ {len(sources_data)} document source(s) — confidence scores"):
                                for src in sources_data:
                                    sc=src["score"]; sc_pct=int(sc*100)
                                    bar_c2="#4ade80" if sc>0.75 else ("#F0C040" if sc>0.5 else "#f87171")
                                    exp="High relevance" if sc>0.75 else ("Moderate" if sc>0.5 else "Low")
                                    tags_str=src.get("tags","")
                                    tag_pills="".join(f'<span style="background:rgba(192,132,200,.1);border:1px solid rgba(192,132,200,.25);font-family:Space Mono,monospace;font-size:.44rem;padding:.06rem .28rem;border-radius:3px;color:#C084C8;margin-right:.15rem;">{t}</span>' for t in (tags_str.split("|") if tags_str else [])[:3])
                                    st.markdown(
                                        f'<div class="src-card"><div class="src-name">📄 {src["filename"]} — chunk #{src.get("chunk_idx","?")}</div>'
                                        f'<div class="src-score">{exp} · {sc:.3f} confidence</div>'
                                        f'<div class="src-bar" style="width:{sc_pct}%;background:{bar_c2};"></div>'
                                        f'<div style="margin-bottom:.18rem;">{tag_pills}</div>'
                                        f'<div class="src-preview">{src["preview"]}…</div></div>', unsafe_allow_html=True)

                        st.caption(f"{cfg2['label']} · {tokens} tokens · {st.session_state.output_mode} mode · live data injected")
                        st.session_state.messages.append({"role":"assistant","content":answer,"sources":sources_data})

                    except Exception as e:
                        st.error(f"Error: {e}")
    else:
        st.markdown('<div style="text-align:center;padding:1rem;background:#0D0B12;border:1px solid rgba(139,58,139,.2);border-radius:10px;">'
            '<span style="font-family:Space Mono,monospace;font-size:.58rem;color:#4A3858;">Chat hidden — click Show Chat in sidebar</span></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHANGE 3 — INLINE ANALYTICS DASHBOARD
# Appears automatically below the chat section after any document is ingested.
# Uses exactly the same render_analytics_tab() logic but wrapped in a styled
# panel so users don't need to switch tabs.
# ══════════════════════════════════════════════════════════════════════════════
def _render_inline_analytics(vectorstore, groq_api_key: str, doc_full_text: str) -> None:
    """Render the analytics dashboard inline, below the chat area."""
    st.markdown(
        '<div class="analytics-inline">'
        '<div class="analytics-inline-title">📊 Document Analytics — Auto-Extracted Insights</div>',
        unsafe_allow_html=True,
    )

    sub = st.tabs(["📊 Metrics", "📋 Templates", "🔍 Hybrid Search", "🧪 Eval Benchmark"])

    # ── TAB A: Metrics ───────────────────────────────────────────────────────
    with sub[0]:
        st.markdown(
            '<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.16em;'
            'text-transform:uppercase;color:#C084C8;margin-bottom:.7rem;">'
            'Auto-Extracted via FinBERT-indexed document</div>', unsafe_allow_html=True)
        if doc_full_text:
            with st.spinner("Extracting metrics…"):
                metrics = extract_metrics(doc_full_text)
            if metrics:
                render_metrics_dashboard(metrics)
                st.markdown("<hr style='border-color:rgba(139,58,139,.15);margin:.8rem 0;'>",
                            unsafe_allow_html=True)
                render_trend_chart(metrics)
                with st.expander("📄 Raw table"):
                    rows = [{"Metric": m["label"],
                             "Value":  format_metric_value(m["value"], m["unit"]),
                             "Unit":   m["unit"],
                             "Category": m["category"]} for m in metrics]
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.info("No metrics matched. Try the Templates tab for LLM-based extraction.")
        else:
            st.info("Re-ingest documents to enable metric extraction.")

    # ── TAB B: Templates ─────────────────────────────────────────────────────
    with sub[1]:
        cats = sorted({v["category"] for v in TEMPLATES.values()})
        chosen_cat = st.selectbox("Filter", ["All"] + cats,
                                  label_visibility="collapsed", key="il_tpl_cat")
        visible = {k: v for k, v in TEMPLATES.items()
                   if chosen_cat == "All" or v["category"] == chosen_cat}
        items_list = list(visible.items())
        for rs in range(0, len(items_list), 3):
            cols = st.columns(3)
            for ci2, (tname, tmeta) in enumerate(items_list[rs:rs + 3]):
                with cols[ci2]:
                    color = CATEGORY_COLORS.get(tmeta["category"], "#9A8AAA")
                    st.markdown(
                        f'<div style="background:#120E1A;border:1px solid rgba(139,58,139,.22);'
                        f'border-top:2px solid {color};border-radius:10px;'
                        f'padding:.8rem .9rem .6rem;">'
                        f'<div style="font-size:1.1rem;">{tmeta["icon"]}</div>'
                        f'<div style="font-family:Syne,sans-serif;font-size:.8rem;font-weight:600;'
                        f'color:#EDE8F5;margin:.25rem 0 .15rem;">{tname}</div>'
                        f'<div style="font-family:Space Mono,monospace;font-size:.5rem;'
                        f'color:{color};text-transform:uppercase;letter-spacing:.1em;">'
                        f'{tmeta["category"]}</div></div>', unsafe_allow_html=True)
                    if st.button("Run →", key=f"il_tpl_{tname[:16]}", use_container_width=True):
                        st.session_state["_prefill"] = tmeta["prompt"]
                        st.success(f"✓ '{tname}' queued — scroll up to the chat ↑")

    # ── TAB C: Hybrid Search ─────────────────────────────────────────────────
    with sub[2]:
        st.markdown(
            '<div style="font-family:Space Mono,monospace;font-size:.52rem;letter-spacing:.16em;'
            'text-transform:uppercase;color:#C084C8;margin-bottom:.7rem;">'
            'FinBERT Dense + BM25 Keyword · Cross-Encoder Re-Rank</div>',
            unsafe_allow_html=True)
        hs_q = st.text_input("Search", placeholder="e.g. free cash flow 2024",
                             label_visibility="collapsed", key="il_hs_q")
        hc1, hc2, hc3 = st.columns(3)
        with hc1: bm25_w = st.slider("BM25 weight", 0.0, 1.0, 0.35, 0.05, key="il_bm25")
        with hc2: top_n  = st.slider("Top results", 3, 10, 5, key="il_topn")
        with hc3: use_ce = st.checkbox("Cross-encoder", value=False, key="il_ce")
        tax_f = st.multiselect("Taxonomy filter", list(TAXONOMY.keys()),
                               default=[], label_visibility="collapsed", key="il_tax")
        if hs_q and vectorstore:
            with st.spinner("Searching with FinBERT…"):
                try:
                    vs2 = vectorstore
                    all_r = vs2["collection"].get(include=["documents", "embeddings", "metadatas"])
                    ch2, em2, mt2 = all_r["documents"], all_r["embeddings"], all_r["metadatas"]
                    if tax_f:
                        fi2 = [i for i, c in enumerate(ch2)
                               if any(tc in tag_chunk(c) for tc in tax_f)]
                        ch2 = [ch2[i] for i in fi2]
                        em2 = [em2[i] for i in fi2]
                        mt2 = [mt2[i] for i in fi2]
                    if not ch2:
                        st.warning("No chunks match the taxonomy filters.")
                    else:
                        q_emb2 = vs2["model"].encode([hs_q], normalize_embeddings=True).tolist()[0]
                        hr2 = HybridRetriever(ch2, em2)
                        hits2 = hr2.retrieve(hs_q, q_emb2, n=top_n,
                                             bm25_weight=bm25_w, rerank=use_ce)
                        for rank, h in enumerate(hits2, 1):
                            meta2 = mt2[h["idx"]] if h["idx"] < len(mt2) else {}
                            tags2 = tag_chunk(h["chunk"])
                            tag_html2 = " ".join(
                                f'<span style="background:rgba(139,58,139,.15);'
                                f'border:1px solid rgba(139,58,139,.3);'
                                f'font-family:Space Mono,monospace;font-size:.5rem;'
                                f'padding:.1rem .35rem;border-radius:3px;'
                                f'color:{CATEGORY_COLORS.get(t,"#9A8AAA")}">{t}</span>'
                                for t in tags2)
                            sc2 = h["score"]
                            bar_c = "#4ade80" if sc2 > 0.75 else ("#F0C040" if sc2 > 0.5 else "#f87171")
                            fname2 = meta2.get("filename", "—")
                            st.markdown(
                                f'<div style="background:#0D0B12;border:1px solid rgba(139,58,139,.22);'
                                f'border-left:3px solid #C084C8;border-radius:0 8px 8px 0;'
                                f'padding:.7rem .9rem;margin-bottom:.5rem;">'
                                f'<div style="display:flex;justify-content:space-between;'
                                f'align-items:center;margin-bottom:.3rem;">'
                                f'<div style="font-family:Space Mono,monospace;font-size:.58rem;'
                                f'color:#C084C8;">#{rank} · 📄 {fname2}</div>'
                                f'<div style="font-family:Space Mono,monospace;font-size:.5rem;'
                                f'color:#4A3858;">hybrid:{sc2:.3f} '
                                f'dense:{h["dense"]:.3f} bm25:{h["bm25"]:.3f}</div></div>'
                                f'<div class="src-rel-bar" style="width:{int(sc2*100)}%;'
                                f'background:{bar_c};"></div>'
                                f'<div style="font-size:.8rem;color:#9A8AAA;line-height:1.55;">'
                                f'{h["chunk"][:300]}…</div>'
                                f'<div style="margin-top:.35rem;display:flex;gap:.3rem;flex-wrap:wrap;">'
                                f'{tag_html2}</div></div>',
                                unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Search error: {e}")
        elif hs_q:
            st.info("Upload and ingest documents first.")

    # ── TAB D: Eval Benchmark ────────────────────────────────────────────────
    with sub[3]:
        st.markdown(
            '<div style="font-family:Syne,sans-serif;font-size:.8rem;color:#4A3858;'
            'margin-bottom:1rem;line-height:1.7;">'
            'Runs 8 standard financial QA prompts and measures keyword-recall accuracy '
            'using FinBERT retrieval. Great for gauging document ingestion quality.</div>',
            unsafe_allow_html=True)
        if st.button("▶  Run Benchmark", key="il_bench"):
            if not vectorstore or not groq_api_key:
                st.error("Need both documents and an API key.")
            else:
                _eval_qs = [
                    {"q": "What was total revenue?",           "kw": ["revenue","billion","million","$"],               "cat": "Income Statement"},
                    {"q": "What was diluted EPS?",             "kw": ["eps","diluted","$","per share"],                 "cat": "Per Share"},
                    {"q": "What was the gross margin?",        "kw": ["gross margin","%","percent"],                   "cat": "Ratios"},
                    {"q": "What was free cash flow?",          "kw": ["free cash flow","operating","capex"],           "cat": "Cash Flow"},
                    {"q": "What are the main risk factors?",   "kw": ["risk","competition","regulatory","uncertainty"], "cat": "Risk Factors"},
                    {"q": "What is the revenue guidance?",     "kw": ["guidance","outlook","forecast","expect"],       "cat": "Growth"},
                    {"q": "What is the debt-to-equity ratio?", "kw": ["debt","equity","ratio","leverage"],             "cat": "Ratios"},
                    {"q": "How much did company spend on R&D?","kw": ["research","development","r&d","billion"],       "cat": "Income Statement"},
                ]
                results_list = []; prog2 = st.progress(0, text="Evaluating…")
                for i2, eq2 in enumerate(_eval_qs):
                    try:
                        from openai import OpenAI as _OAI2
                        _oai2 = _OAI2(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
                        qe2 = vectorstore["model"].encode([eq2["q"]], normalize_embeddings=True).tolist()
                        res2 = vectorstore["collection"].query(
                            query_embeddings=qe2, n_results=4,
                            include=["documents","metadatas","distances"])
                        ctx2 = "\n---\n".join(res2["documents"][0])
                        rsp2 = _oai2.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role":"system","content":"Answer using only the provided context. Be concise."},
                                      {"role":"user","content":f"Context:\n{ctx2}\n\nQuestion: {eq2['q']}"}],
                            temperature=0.05, max_tokens=400)
                        ans2 = rsp2.choices[0].message.content; al2 = ans2.lower()
                        hits2b = sum(1 for kw in eq2["kw"] if kw.lower() in al2)
                        sc2b = round(hits2b / len(eq2["kw"]) * 100, 1)
                        results_list.append({"q": eq2["q"], "cat": eq2["cat"],
                                             "ans": ans2, "score": sc2b,
                                             "hits": hits2b, "total": len(eq2["kw"])})
                    except Exception as exc2:
                        results_list.append({"q": eq2["q"], "cat": eq2["cat"],
                                             "ans": f"Error: {exc2}", "score": 0,
                                             "hits": 0, "total": len(eq2["kw"])})
                    prog2.progress((i2 + 1) / len(_eval_qs), text=f"Q{i2+1}/8…")
                prog2.empty()
                avg2 = sum(r["score"] for r in results_list) / len(results_list)
                col2 = "#4ade80" if avg2 >= 70 else ("#F0C040" if avg2 >= 40 else "#f87171")
                st.markdown(
                    f'<div style="background:#120E1A;border:1px solid rgba(139,58,139,.25);'
                    f'border-radius:10px;padding:1rem 1.2rem;margin-bottom:1rem;">'
                    f'<div style="font-family:Space Mono,monospace;font-size:.52rem;'
                    f'text-transform:uppercase;color:#4A3858;">Recall Score · FinBERT Retrieval</div>'
                    f'<div style="font-family:Cormorant Garamond,serif;font-size:2.2rem;'
                    f'font-weight:300;color:{col2};">{avg2:.1f}%</div>'
                    f'<div style="font-family:Space Mono,monospace;font-size:.48rem;'
                    f'color:#4A3858;">8 questions evaluated</div></div>',
                    unsafe_allow_html=True)
                st.dataframe(
                    pd.DataFrame([{"Question": r["q"][:55]+"…", "Category": r["cat"],
                                   "Score": f"{r['score']}%",
                                   "Hits": f"{r['hits']}/{r['total']}"} for r in results_list]),
                    use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close .analytics-inline


# ── CHANGE 3: Render inline analytics below chat when docs are loaded ────────
if (st.session_state.get("show_analytics")
        and (st.session_state.get("vectorstore") or st.session_state.get("doc_full_text"))):
    _render_inline_analytics(
        vectorstore   = st.session_state.get("vectorstore"),
        groq_api_key  = GROQ_API_KEY,
        doc_full_text = st.session_state.get("doc_full_text", ""),
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANALYTICS DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with _main_tabs[1]:
    render_analytics_tab(
        vectorstore   = st.session_state.get("vectorstore"),
        groq_api_key  = GROQ_API_KEY,
        doc_full_text = st.session_state.get("doc_full_text",""),
        active_model  = st.session_state.active_model,
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""<div class="vfooter">
  <div class="vfooter-text">Built by Yash Chaudhary &nbsp;·&nbsp; Financial RAG Assistant v5 &nbsp;·&nbsp; FinBERT · Llama · GPT-4o · Groq · ChromaDB</div>
</div>""", unsafe_allow_html=True)
