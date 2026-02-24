import os
import streamlit as st
from dotenv import load_dotenv

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
if "ingested_files" not in st.session_state:
    st.session_state.ingested_files = []

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Setup")

    # API Key — use secret if available, otherwise show input box
    default_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    if default_key:
        GEMINI_API_KEY = default_key
        st.success("✅ API Key configured", icon="🔑")
    else:
        GEMINI_API_KEY = st.text_input("🔑 Gemini API Key", type="password", placeholder="AIza...")
        st.markdown("<small>Get your free key at [aistudio.google.com](https://aistudio.google.com)</small>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 📂 Upload Financial Documents")
    uploaded_files = st.file_uploader("Upload Financial PDFs/TXTs", type=["pdf","txt"], accept_multiple_files=True)

    if uploaded_files and st.button("📥 Ingest Documents", use_container_width=True):
        if not GEMINI_API_KEY:
            st.error("Please enter your Gemini API key first.")
        else:
            with st.spinner("Processing documents..."):
                try:
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

                    chroma_client = EphemeralClient(settings=Settings(anonymized_telemetry=False))
                    try:
                        chroma_client.delete_collection("financials")
                    except Exception:
                        pass
                    collection = chroma_client.create_collection("financials", metadata={"hnsw:space":"cosine"})

                    all_chunks, all_ids, all_meta = [], [], []
                    file_names = []

                    for f in uploaded_files:
                        if f.name.endswith(".pdf"):
                            reader = PdfReader(f)
                            text = " ".join(p.extract_text() or "" for p in reader.pages)
                        else:
                            text = f.read().decode("utf-8")
                        chunks = splitter.split_text(text)
                        file_names.append(f.name)
                        for i, chunk in enumerate(chunks):
                            all_chunks.append(chunk)
                            all_ids.append(f"{f.name}_chunk_{i}")
                            all_meta.append({"filename": f.name, "chunk": i})

                    if all_chunks:
                        embeddings = model.encode(all_chunks, normalize_embeddings=True).tolist()
                        collection.add(documents=all_chunks, embeddings=embeddings, ids=all_ids, metadatas=all_meta)

                    st.session_state.vectorstore = {"collection": collection, "model": model}
                    st.session_state.ingested_files = file_names
                    st.success(f"✅ Ingested {len(all_chunks)} chunks from {len(uploaded_files)} files!")
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.ingested_files:
        st.markdown("**📋 Loaded Documents:**")
        for fname in st.session_state.ingested_files:
            st.markdown(f"- `{fname}`")

    st.markdown("---")
    st.markdown("## 💡 Sample Questions")
    samples = ["What was total revenue?", "What are the main risk factors?", "How did EPS change YoY?", "Summarize key highlights", "Compare the two companies"]
    for q in samples:
        if st.button(q, use_container_width=True, key=q):
            st.session_state.prefill = q

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("<div style='text-align:center;color:#888;font-size:0.8rem'>Built by <b>Yash Chaudhary</b><br>Powered by Gemini 2.0 · ChromaDB</div>", unsafe_allow_html=True)

# Chat
if not st.session_state.vectorstore:
    st.info("👈 Upload financial documents in the sidebar to get started.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prefill = st.session_state.pop("prefill", None)
question = st.chat_input("Ask a question about your financial documents...")

if question or prefill:
    q = question or prefill

    if not GEMINI_API_KEY:
        st.error("Please enter your Gemini API key in the sidebar.")
        st.stop()

    st.session_state.messages.append({"role":"user","content":q})
    with st.chat_message("user"):
        st.markdown(q)

    with st.chat_message("assistant"):
        with st.spinner("Searching and generating answer..."):
            try:
                import google.generativeai as genai

                genai.configure(api_key=GEMINI_API_KEY)
                gemini = genai.GenerativeModel(
                    model_name="gemini-2.0-flash",
                    system_instruction="You are an expert financial analyst. Answer questions based only on the provided context. Always cite specific numbers and dates. When comparing multiple documents, clearly label which figures come from which source. If information is missing, say so clearly."
                )

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

                prompt = f"Context:\n{context}\n\nQuestion: {q}"
                response = gemini.generate_content(prompt)
                answer = response.text
                st.markdown(answer)

                if sources:
                    with st.expander("📎 Sources"):
                        for fname, score, preview in sources:
                            st.markdown(f'<div class="source-card"><b>{fname}</b> — relevance: <code>{score}</code><br><i>{preview}...</i></div>', unsafe_allow_html=True)

                st.caption("gemini-2.0-flash | Google AI")
                st.session_state.messages.append({"role":"assistant","content":answer})

            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.markdown("<div style='text-align:center;color:#888;font-size:0.85rem'>Built by <b>Yash Chaudhary</b> | Financial RAG Assistant</div>", unsafe_allow_html=True)
