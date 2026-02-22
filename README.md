# 📊 Financial RAG Assistant

> Intelligent Q&A over financial documents — Annual Reports, 10-Ks & Earnings Transcripts

Built with ChromaDB, Sentence Transformers, OpenAI GPT-3.5, and Streamlit.

## 🚀 Demo
Upload any financial PDF → Ask natural language questions → Get cited answers powered by RAG + GPT

## 🛠️ Tech Stack
- **LLM**: OpenAI GPT-3.5-turbo
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector DB**: ChromaDB (cosine similarity)
- **PDF Parsing**: PyPDF
- **UI**: Streamlit

## ⚙️ Setup
```bash
pip install streamlit openai chromadb sentence-transformers pypdf python-dotenv rich
streamlit run app.py
```

## 💡 Features
- Upload PDF/TXT financial documents
- Semantic search over document chunks
- GPT-powered cited answers
- Multi-turn chat interface
- Source citations with relevance scores

## 👤 Author
**Yash Chaudhary** | CAT 98.13%ile | [LinkedIn](https://linkedin.com)
