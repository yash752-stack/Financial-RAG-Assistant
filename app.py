import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Financial RAG Assistant", page_icon="📊", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Manrope:wght@400;600;700&display=swap');

:root {
    --bg: #07131f;
    --panel: #101f2f;
    --panel-soft: #13283d;
    --text: #e9f1f8;
    --muted: #9cb2c4;
    --accent: #00c389;
    --accent-2: #f7b955;
    --line: rgba(255, 255, 255, 0.12);
    --shadow: 0 20px 40px rgba(0, 0, 0, 0.24);
}

html, body, [class*="css"] {
    font-family: "Manrope", sans-serif;
}

[data-testid="block-container"] {
    max-width: 1120px;
    padding-top: 1rem;
    padding-bottom: 4.5rem;
}

.stApp {
    background:
        radial-gradient(1200px 500px at 92% -20%, rgba(247, 185, 85, 0.17), transparent 55%),
        radial-gradient(900px 500px at -10% 10%, rgba(0, 195, 137, 0.2), transparent 50%),
        linear-gradient(180deg, #060f1a 0%, var(--bg) 100%);
    color: var(--text);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.015));
    border-right: 1px solid var(--line);
}

.main-header {
    background: linear-gradient(128deg, rgba(0, 195, 137, 0.18), rgba(13, 34, 56, 0.95) 44%, rgba(247, 185, 85, 0.2));
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 22px;
    box-shadow: var(--shadow);
    padding: 2.2rem 2rem;
    text-align: center;
    margin: 0.4rem 0 1.2rem;
    animation: riseIn 0.65s ease both;
}

.main-header h1 {
    margin: 0;
    font-family: "Space Grotesk", sans-serif;
    letter-spacing: 0.2px;
    font-size: clamp(1.8rem, 4.2vw, 3rem);
    color: #f2faf9;
}

.brand-row {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0.8rem;
    flex-wrap: wrap;
}

.brand-logo {
    width: clamp(56px, 6vw, 76px);
    height: clamp(56px, 6vw, 76px);
    border-radius: 14px;
    object-fit: cover;
    border: 1px solid rgba(255, 255, 255, 0.22);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.24);
}

.main-header p {
    margin: 0.6rem auto 0;
    max-width: 720px;
    color: var(--muted);
    font-size: 1.05rem;
}

.badges {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 1rem;
}

.badge-pill {
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 999px;
    padding: 0.28rem 0.7rem;
    font-size: 0.8rem;
    color: #d7e7f3;
    background: rgba(255, 255, 255, 0.07);
}

.info-banner {
    margin: 0.25rem 0 1rem;
    background: linear-gradient(90deg, rgba(0, 195, 137, 0.2), rgba(16, 31, 47, 0.88));
    border: 1px solid rgba(0, 195, 137, 0.35);
    border-radius: 14px;
    padding: 0.95rem 1rem;
    color: #cdeee4;
}

.source-card {
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0.01));
    border: 1px solid rgba(255, 255, 255, 0.11);
    border-left: 4px solid var(--accent-2);
    color: #d8e5f0;
    border-radius: 12px;
    padding: 0.85rem 0.9rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.22) !important;
    color: #f5f9ff !important;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.11), rgba(255, 255, 255, 0.03)) !important;
    transition: transform 0.17s ease, border-color 0.2s ease, background 0.2s ease !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-1px);
    border-color: rgba(0, 195, 137, 0.75) !important;
    background: linear-gradient(180deg, rgba(0, 195, 137, 0.32), rgba(0, 195, 137, 0.12)) !important;
}

.stTextInput > div > div > input,
.stTextArea textarea,
.stChatInput textarea {
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.16) !important;
    background: rgba(16, 30, 46, 0.88) !important;
    color: #eaf2f9 !important;
}

.stTextInput > div > div > input:focus,
.stTextArea textarea:focus,
.stChatInput textarea:focus {
    border-color: rgba(0, 195, 137, 0.65) !important;
    box-shadow: 0 0 0 1px rgba(0, 195, 137, 0.45) !important;
}

.stFileUploader {
    background: rgba(7, 20, 34, 0.85);
    border: 1px dashed rgba(255, 255, 255, 0.24);
    border-radius: 14px;
    padding: 0.5rem;
}

.stAlert {
    border-radius: 14px !important;
}

[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 0.5rem 0.85rem;
    margin-bottom: 0.55rem;
}

[data-testid="stChatMessage"][aria-label="Chat message from user"] {
    border-left: 3px solid var(--accent);
}

[data-testid="stChatMessage"][aria-label="Chat message from assistant"] {
    border-left: 3px solid var(--accent-2);
}

.footer-note {
    text-align: center;
    color: #9bb0c2;
    font-size: 0.85rem;
    margin-top: 0.45rem;
}

.metrics-strip {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.6rem;
    margin: 0 0 1rem;
}

.metric-card {
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.02));
    padding: 0.75rem 0.85rem;
}

.metric-label {
    color: #9ec0d0;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.metric-value {
    color: #f4fbff;
    font-family: "Space Grotesk", sans-serif;
    font-size: 1.2rem;
    margin-top: 0.2rem;
}

.composer-hint {
    color: #9fc2cf;
    font-size: 0.82rem;
    margin-bottom: 0.45rem;
}

[data-testid="stTextInput"] input {
    min-height: 44px !important;
}

@keyframes riseIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 900px) {
    [data-testid="block-container"] {
        padding: 0.55rem 0.85rem 6.6rem !important;
    }

    .metrics-strip {
        grid-template-columns: 1fr;
    }

    .main-header {
        padding: 1.6rem 1.2rem;
        border-radius: 16px;
    }

    .main-header p {
        font-size: 0.95rem;
    }

    .badge-pill {
        font-size: 0.75rem;
    }

    [data-testid="stChatMessage"] {
        padding: 0.42rem 0.58rem;
    }

    .source-card {
        font-size: 0.82rem;
    }

    .composer-hint {
        font-size: 0.75rem;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="main-header">
<div class="brand-row">
<img class="brand-logo" src="https://tenor.com/en-GB/view/placek-placek-transparent-placek-white-cat-placek-cat-uncanny-cat-gif-4165873234353870418" alt="Placek logo">
<h1>Financial RAG Assistant</h1>
</div>
<p>Sharper answers from annual reports, 10-Ks, and earnings transcripts.</p>
<div class="badges">
<span class="badge-pill">Semantic Retrieval</span>
<span class="badge-pill">Grounded Answers</span>
<span class="badge-pill">Source-backed Insights</span>
</div>
</div>
""",
    unsafe_allow_html=True,
)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "composer_text" not in st.session_state:
    st.session_state.composer_text = ""
if "submit_from_enter" not in st.session_state:
    st.session_state.submit_from_enter = False
if "show_quick_actions" not in st.session_state:
    st.session_state.show_quick_actions = False

# Sidebar
with st.sidebar:
    st.markdown("## Setup")
    api_key = st.text_input("Groq API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key

    if api_key:
        st.success("API key configured")

    st.markdown("---")
    st.markdown("## Upload Financial Documents")
    uploaded_files = st.file_uploader("Upload Financial PDFs/TXTs", type=["pdf", "txt"], accept_multiple_files=True)

    if uploaded_files and st.button("Ingest Documents", use_container_width=True):
        if not api_key:
            st.error("Please enter your Groq API key first.")
        else:
            with st.spinner("Processing documents..."):
                try:
                    from chromadb import PersistentClient
                    from chromadb.config import Settings
                    from sentence_transformers import SentenceTransformer
                    from pypdf import PdfReader
                    from langchain_text_splitters import RecursiveCharacterTextSplitter

                    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                    model = SentenceTransformer("all-MiniLM-L6-v2")
                    client = PersistentClient(path="./chroma_db", settings=Settings(anonymized_telemetry=False))
                    collection = client.get_or_create_collection("financials", metadata={"hnsw:space": "cosine"})

                    all_chunks, all_ids, all_meta = [], [], []
                    existing_ids = set(collection.get()["ids"])

                    for f in uploaded_files:
                        if f.name.endswith(".pdf"):
                            reader = PdfReader(f)
                            text = " ".join(p.extract_text() or "" for p in reader.pages)
                        else:
                            text = f.read().decode("utf-8")
                        chunks = splitter.split_text(text)
                        for i, chunk in enumerate(chunks):
                            cid = f"{f.name}_chunk_{i}"
                            if cid not in existing_ids:
                                all_chunks.append(chunk)
                                all_ids.append(cid)
                                all_meta.append({"filename": f.name, "chunk": i})

                    if all_chunks:
                        embeddings = model.encode(all_chunks, normalize_embeddings=True).tolist()
                        collection.add(documents=all_chunks, embeddings=embeddings, ids=all_ids, metadatas=all_meta)

                    st.session_state.vectorstore = {"collection": collection, "model": model}
                    st.success(f"Ingested {len(all_chunks)} chunks from {len(uploaded_files)} files")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("## Sample Questions")
    samples = [
        "What was total revenue?",
        "What are the main risk factors?",
        "How did EPS change YoY?",
        "Summarize key highlights",
    ]
    for q in samples:
        if st.button(q, use_container_width=True, key=q):
            st.session_state.prefill = q

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown('<div class="info-banner">Upload financial documents in the sidebar to get started.</div>', unsafe_allow_html=True)

chunk_count = 0
if st.session_state.vectorstore:
    try:
        counts = st.session_state.vectorstore["collection"].count()
        chunk_count = counts if isinstance(counts, int) else 0
    except Exception:
        chunk_count = 0

st.markdown(
    f"""
<div class="metrics-strip">
  <div class="metric-card">
    <div class="metric-label">Model</div>
    <div class="metric-value">Llama 3.3 70B</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Chunks Indexed</div>
    <div class="metric-value">{chunk_count if chunk_count else "—"}</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Messages</div>
    <div class="metric-value">{len(st.session_state.messages)}</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# Chat
st.markdown("### Ask About Your Financial Documents")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prefill = st.session_state.pop("prefill", None)
if prefill:
    st.session_state.composer_text = prefill


def submit_from_enter():
    st.session_state.submit_from_enter = True


st.markdown('<div class="composer-hint">Press Enter to send, or use + for quick prompts.</div>', unsafe_allow_html=True)
composer_col_1, composer_col_2, composer_col_3 = st.columns([1, 12, 2], gap="small")
with composer_col_1:
    plus_clicked = st.button("＋", key="composer_plus", use_container_width=True, help="Quick prompts")
with composer_col_2:
    st.text_input(
        "Ask a question about your financial documents...",
        key="composer_text",
        placeholder="Ask a question about your financial documents...",
        label_visibility="collapsed",
        on_change=submit_from_enter,
    )
with composer_col_3:
    send_clicked = st.button("Send", key="composer_send", use_container_width=True)

if plus_clicked:
    st.session_state.show_quick_actions = not st.session_state.show_quick_actions

if st.session_state.show_quick_actions:
    quick_col_1, quick_col_2, quick_col_3 = st.columns(3)
    with quick_col_1:
        if st.button("Revenue snapshot", key="qa_revenue", use_container_width=True):
            st.session_state.composer_text = "Give me a concise revenue snapshot with YoY change."
    with quick_col_2:
        if st.button("Risk summary", key="qa_risk", use_container_width=True):
            st.session_state.composer_text = "Summarize the top risk factors from the documents."
    with quick_col_3:
        if st.button("EPS trend", key="qa_eps", use_container_width=True):
            st.session_state.composer_text = "How did EPS change YoY, and what drove it?"

question = st.session_state.composer_text.strip()
enter_submit = st.session_state.submit_from_enter
st.session_state.submit_from_enter = False
should_submit = bool(prefill) or send_clicked or enter_submit

if should_submit and question:
    q = question
    if not api_key:
        st.error("Please enter your Groq API key in the sidebar.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)

    with st.chat_message("assistant"):
        with st.spinner("Searching and generating answer..."):
            try:
                from openai import OpenAI

                client_oai = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

                context = "No documents ingested yet. Please upload financial documents first."
                sources = []

                if st.session_state.vectorstore:
                    vs = st.session_state.vectorstore
                    q_emb = vs["model"].encode([q], normalize_embeddings=True).tolist()
                    results = vs["collection"].query(
                        query_embeddings=q_emb,
                        n_results=5,
                        include=["documents", "metadatas", "distances"],
                    )
                    chunks = results["documents"][0]
                    metas = results["metadatas"][0]
                    dists = results["distances"][0]
                    context = "\n---\n".join(f"[{m['filename']}]\n{c}" for c, m in zip(chunks, metas))
                    sources = [
                        (m["filename"], round(1 - d / 2, 3), c[:200])
                        for c, m, d in zip(chunks, metas, dists)
                    ]

                response = client_oai.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert financial analyst. Answer questions based only on the provided context. "
                                "Always cite specific numbers and dates. If information is missing, say so clearly."
                            ),
                        },
                        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {q}"},
                    ],
                    temperature=0.1,
                    max_tokens=1500,
                )
                answer = response.choices[0].message.content
                st.markdown(answer)

                if sources:
                    with st.expander("Sources"):
                        for fname, score, preview in sources:
                            st.markdown(
                                f'<div class="source-card"><b>{fname}</b> - relevance: <code>{score}</code><br><i>{preview}...</i></div>',
                                unsafe_allow_html=True,
                            )

                st.caption(f"llama-3.3-70b-versatile | {response.usage.total_tokens} tokens")
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.composer_text = ""

            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.markdown(
    "<div class='footer-note'>Built by <b>Yash Chaudhary</b> | Financial RAG Assistant</div>",
    unsafe_allow_html=True,
)

