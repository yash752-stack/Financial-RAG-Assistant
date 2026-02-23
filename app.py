import os
import sys
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from langchain.text_splitter 
import RecursiveCharacterTextSplitter
load_dotenv()

st.set_page_config(page_title="Financial RAG Assistant", page_icon="📊", layout="wide")

st.markdown("""
<style>
.main-header{background:linear-gradient(135deg,#1a1a2e,#0f3460);padding:2rem;border-radius:12px;text-align:center;margin-bottom:1.5rem}
.main-header h1{color:#e94560;font-size:2rem;margin:0}
.main-header p{color:#a8b2d8;margin:0.5rem 0 0}
.source-card{background:#f8f9fa;border-left:4px solid #e94560;padding:0.8rem;margin:0.4rem 0;border-radius:0 8px 8px 0;font-size:0.85rem}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
<h1>📊 Financial RAG Assistant</h1>
<p>Intelligent Q&A over Annual Reports, 10-Ks & Earnings Transcripts</p>
</div>
""", unsafe_allow_html=True)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Setup")
    api_key = st.text_input("Groq API Key", type="password", value=os.getenv("GROQ_API_KEY",""))
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key

    st.markdown("---")
    st.markdown("## 📂 Upload Documents")
    uploaded_files = st.file_uploader("Upload Financial PDFs/TXTs", type=["pdf","txt"], accept_multiple_files=True)

    if uploaded_files and st.button("📥 Ingest Documents", use_container_width=True):
        if not api_key:
            st.error("Please enter your OpenAI API key first.")
        else:
            with st.spinner("Processing documents..."):
                try:
                    from chromadb import PersistentClient
                    from chromadb.config import Settings
                    from sentence_transformers import SentenceTransformer
                    from pypdf import PdfReader
                    from langchain.text_splitter import RecursiveCharacterTextSplitter

                    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                    model = SentenceTransformer("all-MiniLM-L6-v2")
                    client = PersistentClient(path="./chroma_db", settings=Settings(anonymized_telemetry=False))
                    collection = client.get_or_create_collection("financials", metadata={"hnsw:space":"cosine"})

                    all_chunks, all_ids, all_meta = [], [], []
                    for f in uploaded_files:
                        if f.name.endswith(".pdf"):
                            reader = PdfReader(f)
                            text = " ".join(p.extract_text() or "" for p in reader.pages)
                        else:
                            text = f.read().decode("utf-8")
                        chunks = splitter.split_text(text)
                        for i, chunk in enumerate(chunks):
                            cid = f"{f.name}_chunk_{i}"
                            if cid not in collection.get()["ids"]:
                                all_chunks.append(chunk)
                                all_ids.append(cid)
                                all_meta.append({"filename": f.name, "chunk": i})

                    if all_chunks:
                        embeddings = model.encode(all_chunks, normalize_embeddings=True).tolist()
                        collection.add(documents=all_chunks, embeddings=embeddings, ids=all_ids, metadatas=all_meta)

                    st.session_state.vectorstore = {"collection": collection, "model": model}
                    st.success(f"✅ Ingested {len(all_chunks)} chunks from {len(uploaded_files)} files!")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("## 💡 Sample Questions")
    samples = ["What was total revenue?", "What are the main risk factors?", "How did EPS change YoY?", "Summarize key highlights"]
    for q in samples:
        if st.button(q, use_container_width=True, key=q):
            st.session_state.prefill = q

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Chat
st.markdown("### 💬 Ask About Your Financial Documents")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prefill = st.session_state.pop("prefill", None)
question = st.chat_input("Ask a question about your financial documents...")

if question or prefill:
    q = question or prefill
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
        st.stop()

    st.session_state.messages.append({"role":"user","content":q})
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
                    results = vs["collection"].query(query_embeddings=q_emb, n_results=5, include=["documents","metadatas","distances"])
                    chunks = results["documents"][0]
                    metas = results["metadatas"][0]
                    dists = results["distances"][0]
                    context = "\n---\n".join(f"[{m['filename']}]\n{c}" for c,m in zip(chunks,metas))
                    sources = [(m["filename"], round(1-d/2,3), c[:200]) for c,m,d in zip(chunks,metas,dists)]

                response = client_oai.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role":"system","content":"You are an expert financial analyst. Answer questions based only on the provided context. Always cite specific numbers and dates. If information is missing, say so clearly."},
                        {"role":"user","content":f"Context:\n{context}\n\nQuestion: {q}"}
                    ],
                    temperature=0.1,
                    max_tokens=1500
                )
                answer = response.choices[0].message.content
                st.markdown(answer)

                if sources:
                    with st.expander("📎 Sources"):
                        for fname, score, preview in sources:
                            st.markdown(f'<div class="source-card"><b>{fname}</b> — relevance: <code>{score}</code><br><i>{preview}...</i></div>', unsafe_allow_html=True)

                st.caption(f"llama3-8b-8192 | {response.usage.total_tokens} tokens")
                st.session_state.messages.append({"role":"assistant","content":answer})

            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.markdown("<div style='text-align:center;color:#888;font-size:0.85rem'>Built by <b>Yash Chaudhary</b> | Financial RAG Assistant</div>", unsafe_allow_html=True)
