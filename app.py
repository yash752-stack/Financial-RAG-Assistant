"""
app.py — Financial RAG Assistant
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
[data-testid="stDecoration"], .stDeployButton { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── DESIGN SYSTEM ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --ink:       #0D0D0D;
  --ink-2:     #1A1A1A;
  --ink-3:     #2A2A2A;
  --slate:     #4A4A5A;
  --mist:      #8A8A9A;
  --fog:       #C8C8D8;
  --paper:     #F5F3EE;
  --cream:     #FDFCF8;
  --gold:      #C8922A;
  --gold-l:    #F0C870;
  --gold-pale: #FBF3DF;
  --teal:      #1B6B6B;
  --teal-l:    #2FA8A8;
  --teal-pale: #E0F4F4;
  --red:       #B03030;
  --red-pale:  #FDEAEA;
  --card-bg:   #FFFFFF;
  --card-br:   #E8E6E0;
  --r:         8px;
  --r-lg:      14px;
  --shadow-sm: 0 1px 4px rgba(0,0,0,0.06), 0 2px 8px rgba(0,0,0,0.04);
  --shadow:    0 2px 12px rgba(0,0,0,0.08), 0 4px 24px rgba(0,0,0,0.05);
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
  color: var(--ink) !important;
}

.stApp, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(ellipse 900px 600px at 0% 0%, rgba(200,146,42,0.06) 0%, transparent 60%),
    radial-gradient(ellipse 700px 500px at 100% 100%, rgba(27,107,107,0.07) 0%, transparent 60%),
    var(--paper) !important;
}

[data-testid="stMain"], [data-testid="block-container"] {
  background: transparent !important;
  padding-top: 0 !important;
  max-width: 1100px !important;
}

[data-testid="stSidebar"] {
  background: var(--cream) !important;
  border-right: 1px solid var(--card-br) !important;
  box-shadow: 2px 0 16px rgba(0,0,0,0.04) !important;
}
[data-testid="stSidebar"] > div { padding: 1.5rem 1.25rem !important; }

h1, h2, h3 {
  font-family: 'DM Serif Display', serif !important;
  color: var(--ink) !important;
  letter-spacing: -0.02em !important;
}
code, pre { font-family: 'DM Mono', monospace !important; }

/* Metrics */
[data-testid="stMetric"] {
  background: var(--card-bg) !important;
  border: 1px solid var(--card-br) !important;
  border-radius: var(--r) !important;
  padding: 0.85rem 1rem !important;
  box-shadow: var(--shadow-sm) !important;
}
[data-testid="stMetricLabel"] p {
  font-size: 0.7rem !important; color: var(--mist) !important;
  text-transform: uppercase !important; letter-spacing: 0.08em !important;
}
[data-testid="stMetricValue"] {
  font-family: 'DM Serif Display', serif !important;
  font-size: 1.5rem !important; color: var(--ink) !important;
}

/* Buttons */
.stButton > button {
  border-radius: var(--r) !important;
  border: 1px solid var(--card-br) !important;
  background: var(--card-bg) !important;
  color: var(--ink-3) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  padding: 0.4rem 0.9rem !important;
  box-shadow: var(--shadow-sm) !important;
  transition: all 0.18s ease !important;
}
.stButton > button:hover {
  border-color: var(--gold) !important;
  background: var(--gold-pale) !important;
  color: var(--gold) !important;
  transform: translateY(-1px) !important;
}

/* Inputs */
.stTextInput input, .stTextArea textarea {
  background: var(--card-bg) !important;
  border: 1px solid var(--card-br) !important;
  border-radius: var(--r) !important;
  color: var(--ink) !important;
  font-family: 'DM Sans', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--teal-l) !important;
  box-shadow: 0 0 0 2px rgba(47,168,168,0.15) !important;
}
.stTextInput input::placeholder { color: var(--fog) !important; }

/* Chat input */
[data-testid="stChatInput"] {
  background: var(--card-bg) !important;
  border: 1px solid var(--card-br) !important;
  border-radius: var(--r-lg) !important;
  box-shadow: var(--shadow) !important;
}
[data-testid="stChatInput"] textarea {
  background: transparent !important;
  border: none !important; box-shadow: none !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--teal-l) !important;
  box-shadow: 0 0 0 2px rgba(47,168,168,0.15), var(--shadow) !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
  background: var(--card-bg) !important;
  border: 1px solid var(--card-br) !important;
  border-radius: var(--r-lg) !important;
  box-shadow: var(--shadow-sm) !important;
  padding: 0.75rem 1rem !important;
  margin-bottom: 0.6rem !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
  background: var(--card-bg) !important;
  border: 1.5px dashed var(--fog) !important;
  border-radius: var(--r-lg) !important;
}
[data-testid="stFileUploader"]:hover { border-color: var(--teal-l) !important; }

/* Expander */
[data-testid="stExpander"] summary {
  background: var(--card-bg) !important;
  border-radius: var(--r) !important;
  border: 1px solid var(--card-br) !important;
  font-size: 0.82rem !important;
  color: var(--slate) !important;
}

/* Alerts */
.stSuccess { background: var(--teal-pale) !important; border: 1px solid var(--teal-l) !important; border-radius: var(--r) !important; color: var(--teal) !important; }
.stError   { background: var(--red-pale) !important;  border: 1px solid var(--red) !important;    border-radius: var(--r) !important; }
.stInfo    { background: var(--gold-pale) !important; border: 1px solid var(--gold) !important;   border-radius: var(--r) !important; }

/* Progress */
.stProgress > div > div { background: linear-gradient(90deg, var(--teal), var(--teal-l)) !important; }

hr { border-color: var(--card-br) !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: var(--fog); border-radius: 2px; }

/* ── Custom components ── */
.rag-header {
  display: flex; align-items: center; gap: 1.2rem;
  padding: 1.6rem 2rem;
  background: var(--card-bg);
  border: 1px solid var(--card-br);
  border-radius: var(--r-lg);
  box-shadow: var(--shadow);
  margin-bottom: 1.4rem;
}
.rag-icon {
  width: 54px; height: 54px; border-radius: 12px;
  background: linear-gradient(135deg, var(--teal) 0%, var(--teal-l) 100%);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.5rem; flex-shrink: 0;
  box-shadow: 0 4px 16px rgba(27,107,107,0.3);
}
.rag-header-text h1 {
  font-family: 'DM Serif Display', serif !important;
  font-size: 1.8rem !important; margin: 0 !important;
  color: var(--ink) !important; line-height: 1.1 !important;
}
.rag-header-text p { margin: 0.2rem 0 0 !important; font-size: 0.86rem !important; color: var(--mist) !important; }
.badge-row { display: flex; gap: 0.4rem; margin-top: 0.5rem; flex-wrap: wrap; }
.badge { font-size: 0.7rem; font-weight: 500; padding: 0.15rem 0.5rem; border-radius: 999px; border: 1px solid var(--card-br); color: var(--slate); background: var(--paper); }
.badge.teal { border-color: var(--teal-l); color: var(--teal); background: var(--teal-pale); }
.badge.gold { border-color: var(--gold);   color: var(--gold); background: var(--gold-pale); }

.src-card {
  background: var(--card-bg); border: 1px solid var(--card-br);
  border-left: 3px solid var(--teal-l);
  border-radius: var(--r); padding: 0.7rem 0.9rem; margin: 0.4rem 0; font-size: 0.84rem;
}
.src-name { font-weight: 600; color: var(--teal); font-size: 0.78rem; margin-bottom: 0.15rem; }
.src-score { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: var(--mist); }
.src-preview { color: var(--slate); line-height: 1.5; margin-top: 0.2rem; }

.sb-section {
  font-size: 0.62rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--mist); padding: 1rem 0 0.4rem; border-top: 1px solid var(--card-br); margin-top: 0.5rem;
}

.key-badge {
  display: flex; align-items: center; gap: 0.4rem;
  background: var(--teal-pale); border: 1px solid var(--teal-l);
  color: var(--teal); border-radius: var(--r); padding: 0.35rem 0.7rem;
  font-size: 0.76rem; font-weight: 500;
}
.key-dot { width:6px; height:6px; border-radius:50%; background:var(--teal-l); animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

.empty-state { text-align: center; padding: 3.5rem 2rem; color: var(--mist); }
.empty-icon { font-size: 2.2rem; margin-bottom: 0.8rem; }
.empty-title { font-family: 'DM Serif Display', serif; font-size: 1.3rem; color: var(--ink-3); margin-bottom: 0.35rem; }
.empty-sub { font-size: 0.83rem; color: var(--mist); max-width: 300px; margin: 0 auto; line-height: 1.7; }

.footer { text-align: center; padding: 1.4rem 0 0.4rem; font-size: 0.76rem; color: var(--fog); border-top: 1px solid var(--card-br); margin-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
for k, v in [
    ("messages", []),
    ("vectorstore", None),
    ("uploaded_docs", 0),
    ("chunk_count", 0),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── INGEST FUNCTION ───────────────────────────────────────────────────────────
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
    # EphemeralClient = pure in-memory, no SQLite, no threading issues on Streamlit Cloud
    client = EphemeralClient(settings=Settings(anonymized_telemetry=False))
    try:
        client.delete_collection("financials")
    except Exception:
        pass
    collection = client.create_collection("financials", metadata={"hnsw:space": "cosine"})

    all_chunks, all_ids, all_meta = [], [], []
    prog = st.progress(0, text="Reading files…")

    for i, f in enumerate(files):
        if f.name.lower().endswith(".pdf"):
            reader = PdfReader(f)
            text = " ".join(page.extract_text() or "" for page in reader.pages)
        else:
            text = f.read().decode("utf-8")
        chunks = splitter.split_text(text)
        for j, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(f"{f.name}_chunk_{j}")
            all_meta.append({"filename": f.name, "chunk": j})
        prog.progress((i + 1) / len(files), text=f"Processed {f.name}")

    prog.empty()

    if all_chunks:
        with st.spinner(f"Embedding {len(all_chunks)} chunks…"):
            embeddings = model.encode(all_chunks, normalize_embeddings=True).tolist()
            collection.add(documents=all_chunks, embeddings=embeddings, ids=all_ids, metadatas=all_meta)

    st.session_state.vectorstore     = {"collection": collection, "model": model}
    st.session_state.uploaded_docs   = len(files)
    st.session_state.chunk_count     = len(all_chunks)
    return len(all_chunks)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0.1rem 0 1rem;">
      <div style="font-family:'DM Serif Display',serif;font-size:1.25rem;color:#0D0D0D;line-height:1.1;">
        Financial<br><em style="color:#1B6B6B;">RAG Assistant</em>
      </div>
      <div style="font-size:0.65rem;color:#8A8A9A;letter-spacing:0.1em;text-transform:uppercase;margin-top:0.3rem;">
        Llama 3.3 · 70B · Groq
      </div>
    </div>
    """, unsafe_allow_html=True)

    # API key
    st.markdown('<div class="sb-section" style="border-top:none;padding-top:0;">Configuration</div>', unsafe_allow_html=True)
    default_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))

    if default_key:
        GROQ_API_KEY = default_key
        st.markdown('<div class="key-badge"><div class="key-dot"></div>API Key Active</div>', unsafe_allow_html=True)
    else:
        GROQ_API_KEY = st.text_input("Groq API Key", type="password", placeholder="gsk_…", label_visibility="collapsed")
        st.caption("Get a free key at [console.groq.com](https://console.groq.com)")
        if GROQ_API_KEY:
            os.environ["GROQ_API_KEY"] = GROQ_API_KEY
            st.markdown('<div class="key-badge"><div class="key-dot"></div>API Key Active</div>', unsafe_allow_html=True)

    # Upload
    st.markdown('<div class="sb-section">Documents</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Upload PDFs or TXTs",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        if st.button("⬆  Ingest Documents", use_container_width=True):
            if not GROQ_API_KEY:
                st.error("Enter your Groq API key first.")
            else:
                try:
                    n = ingest_documents(uploaded_files)
                    st.success(f"✓  {n} chunks from {len(uploaded_files)} file(s)")
                except Exception as e:
                    st.error(str(e))

    if st.session_state.chunk_count:
        st.markdown(f"""
        <div style="background:var(--teal-pale);border:1px solid var(--teal-l);
                    border-radius:8px;padding:0.55rem 0.75rem;margin-top:0.5rem;
                    font-size:0.78rem;color:var(--teal);">
          📚 &nbsp;<b>{st.session_state.chunk_count}</b> chunks &nbsp;·&nbsp;
          <b>{st.session_state.uploaded_docs}</b> file(s)
        </div>""", unsafe_allow_html=True)

    # Quick ask
    st.markdown('<div class="sb-section">Quick Ask</div>', unsafe_allow_html=True)
    for q_item in [
        "What was total revenue?",
        "Main risk factors?",
        "EPS change YoY?",
        "Key business highlights",
        "Debt and liquidity summary",
    ]:
        if st.button(q_item, use_container_width=True, key=f"qa_{q_item[:12]}"):
            st.session_state["_prefill"] = q_item

    st.markdown('<div class="sb-section">Actions</div>', unsafe_allow_html=True)
    if st.button("🗑  Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── MAIN ──────────────────────────────────────────────────────────────────────

# Header card
st.markdown("""
<div class="rag-header">
  <div class="rag-icon">📈</div>
  <div class="rag-header-text">
    <h1>Financial RAG Assistant</h1>
    <p>Sharper answers from annual reports, 10-Ks &amp; earnings transcripts.</p>
    <div class="badge-row">
      <span class="badge teal">Semantic Retrieval</span>
      <span class="badge teal">Source-backed Answers</span>
      <span class="badge gold">Llama 3.3 · 70B</span>
      <span class="badge">Groq</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Model", "Llama 3.3 70B")
c2.metric("Chunks", st.session_state.chunk_count or "—")
c3.metric("Documents", st.session_state.uploaded_docs or "—")
c4.metric("Exchanges", len(st.session_state.messages) // 2 or "—")

st.write("")

# ── STOCK TRACKER ─────────────────────────────────────────────────────────────
with st.expander("📊  Global Stock Tracker", expanded=False):
    col_sym, col_range = st.columns([4, 1])
    with col_sym:
        symbols = st.multiselect(
            "Symbols",
            options=["AAPL","MSFT","NVDA","GOOGL","AMZN","TSLA","META","TSM","SAP","BABA","SONY","NVO","RELIANCE.NS","TCS.NS","INFY.NS"],
            default=["AAPL","MSFT","NVDA","TSM"],
            label_visibility="collapsed",
        )
    with col_range:
        rng = st.selectbox("Range", ["30d","90d","180d","1y"], index=1, label_visibility="collapsed")

    days_map = {"30d": 30, "90d": 90, "180d": 180, "1y": 365}
    if symbols:
        try:
            import pandas as pd
            import yfinance as yf

            end_dt   = date.today()
            start_dt = end_dt - timedelta(days=days_map[rng])
            raw = yf.download(
                tickers=symbols,
                start=start_dt.isoformat(),
                end=end_dt.isoformat(),
                interval="1d",
                auto_adjust=True,
                progress=False,
                group_by="ticker",
                threads=True,
            )
            chart = pd.DataFrame()
            if len(symbols) == 1:
                chart[symbols[0]] = raw["Close"] if "Close" in raw.columns else raw.iloc[:, 0]
            else:
                for sym in symbols:
                    if (sym, "Close") in raw.columns:
                        chart[sym] = raw[(sym, "Close")]

            chart = chart.dropna(how="all")
            if not chart.empty:
                normed = (chart / chart.iloc[0] - 1) * 100
                st.line_chart(normed, height=230, use_container_width=True)
                st.caption(f"% return from {start_dt}  ·  {len(chart)} trading days  ·  Yahoo Finance")
            else:
                st.info("No data for selected symbols. Try a different range.")
        except Exception as e:
            st.info(f"Stock chart unavailable: {e}")
    else:
        st.info("Select at least one symbol.")

st.write("")
st.markdown("#### Ask About Your Financial Documents")

# Empty state
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
      <div class="empty-icon">🔍</div>
      <div class="empty-title">Ready to analyse</div>
      <div class="empty-sub">
        Upload financial documents in the sidebar, then ask anything —
        revenue figures, risk factors, YoY comparisons, or competitive positioning.
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
                      <div class="src-score">relevance score: {src['score']}</div>
                      <div class="src-preview">{src['preview']}…</div>
                    </div>""", unsafe_allow_html=True)

# Chat input
prefill = st.session_state.pop("_prefill", None)
question = st.chat_input("Ask about your financial documents…")
q = prefill or question

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
                    vs     = st.session_state.vectorstore
                    q_emb  = vs["model"].encode([q], normalize_embeddings=True).tolist()
                    res    = vs["collection"].query(
                        query_embeddings=q_emb,
                        n_results=5,
                        include=["documents", "metadatas", "distances"],
                    )
                    cks    = res["documents"][0]
                    mts    = res["metadatas"][0]
                    dts    = res["distances"][0]
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

# Footer
st.markdown("""
<div class="footer">
  Built by <b>Yash Chaudhary</b> &nbsp;·&nbsp; Financial RAG Assistant
  &nbsp;·&nbsp; Llama 3.3 70B × Groq × ChromaDB
</div>
""", unsafe_allow_html=True)
