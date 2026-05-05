from __future__ import annotations

import io
import re
import zipfile
import xml.etree.ElementTree as ET

import pandas as pd
import streamlit as st

from .analytics import extract_metrics

FIN_SECTION_PATTERNS = [
    (r"income statement|profit.{0,10}loss|revenue|net income|gross profit|ebitda|operating income|COGS", "Income Statement"),
    (r"balance sheet|total assets|liabilities|shareholders.{0,8}equity|book value|working capital", "Balance Sheet"),
    (r"cash flow|operating activities|investing activities|financing activities|capex|free cash flow", "Cash Flow"),
    (r"\bEPS\b|earnings per share|diluted|basic eps|per share", "Per Share"),
    (r"P/E|price.{0,6}earnings|ROE|ROA|ROCE|debt.{0,6}equity|current ratio|quick ratio|gross margin|net margin", "Ratios"),
    (r"risk factor|material risk|litigation|regulatory|compliance|contingent", "Risk Factors"),
    (r"guidance|outlook|forward.looking|forecast|target|next quarter", "Outlook & Guidance"),
]

ITEM_RE = re.compile(r"^\s*(?:ITEM|Item)\s+(\d{1,2}[ABab]?)[\.\:\s]", re.MULTILINE)


def extract_text_from_file(file_obj) -> str:
    raw = file_obj.read()
    file_obj.seek(0)
    blocks = extract_page_aware(file_obj)
    return " ".join(block["text"] for block in blocks) if blocks else raw.decode("utf-8", errors="ignore")


def extract_chunk_keywords(text: str, max_keywords: int = 8) -> str:
    stop_words = {
        "the", "and", "of", "in", "to", "a", "is", "are", "was", "were", "for",
        "as", "on", "at", "by", "an", "be", "with", "or", "from", "this", "that",
    }
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9\-\.\/]{2,}", text)
    counts: dict[str, int] = {}
    for token in tokens:
        lowered = token.lower()
        if lowered not in stop_words and len(lowered) >= 3:
            counts[lowered] = counts.get(lowered, 0) + 1
    return " ".join(sorted(counts, key=lambda token: counts[token], reverse=True)[:max_keywords])


def infer_section(text: str) -> str:
    sample = text[:800].lower()
    for pattern, label in FIN_SECTION_PATTERNS:
        if re.search(pattern, sample, re.IGNORECASE):
            return label
    return "General"


def is_10k_document(text: str) -> bool:
    head = text[:4000]
    if re.search(r"Form\s+10-K|Annual\s+Report\s+on\s+Form\s+10", head, re.IGNORECASE):
        return True
    items = set(match.group(1).lower() for match in ITEM_RE.finditer(text[:20000]))
    return len(items) >= 3


def split_10k_into_sections(text: str) -> list[dict]:
    boundaries = [(match.start(), f"Item {match.group(1).upper()}") for match in ITEM_RE.finditer(text)]
    if not boundaries:
        return [{"section_label": "General", "text": text}]
    sections: list[dict] = []
    for index, (start, label) in enumerate(boundaries):
        end = boundaries[index + 1][0] if index + 1 < len(boundaries) else len(text)
        body = text[start:end].strip()
        if body:
            lines = body.splitlines()
            payload = "\n".join(lines[1:]).strip() if len(lines) > 1 else body
            if payload:
                sections.append({"section_label": label, "text": payload})
    return sections or [{"section_label": "General", "text": text}]


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    if not text.strip():
        return []
    separators = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""]

    def split_recursive(payload: str, remaining: list[str]) -> list[str]:
        if len(payload) <= chunk_size or not remaining:
            return [payload] if payload.strip() else []
        separator = remaining[0]
        parts = payload.split(separator)
        chunks: list[str] = []
        buffer = ""
        for part in parts:
            candidate = (buffer + separator + part).lstrip(separator) if buffer else part
            if len(candidate) <= chunk_size:
                buffer = candidate
            else:
                if buffer:
                    chunks.append(buffer)
                    buffer = buffer[-overlap:] + separator + part if len(buffer) > overlap else part
                else:
                    chunks.extend(split_recursive(part, remaining[1:]))
                    buffer = ""
        if buffer:
            chunks.append(buffer)
        return [chunk for chunk in chunks if chunk.strip()]

    return split_recursive(text, separators)


def extract_page_aware(file_obj) -> list[dict]:
    name = file_obj.name.lower()
    raw = file_obj.read()
    pages: list[dict] = []

    if name.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(raw))
        for index, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text(extraction_mode="layout") or ""
            except Exception:
                text = page.extract_text() or ""
            if text.strip():
                pages.append({"text": text, "page": index, "source": file_obj.name})
        if pages:
            combined = "\n".join(page["text"] for page in pages)
            if is_10k_document(combined):
                pages = [
                    {"text": section["text"], "page": index + 1, "source": file_obj.name, "10k_item": section["section_label"]}
                    for index, section in enumerate(split_10k_into_sections(combined))
                ]
    elif name.endswith((".xlsx", ".xls")):
        sheets = pd.read_excel(io.BytesIO(raw), sheet_name=None)
        for index, (sheet, df) in enumerate(sheets.items(), start=1):
            pages.append({"text": f"=== Sheet: {sheet} ===\n{df.fillna('').to_string(index=False)}", "page": index, "source": f"{file_obj.name}[{sheet}]"})
    elif name.endswith(".csv"):
        frame = pd.read_csv(io.BytesIO(raw), dtype=str)
        pages.append({"text": frame.fillna("").to_string(index=False), "page": 1, "source": file_obj.name})
    elif name.endswith(".docx"):
        archive = zipfile.ZipFile(io.BytesIO(raw))
        xml_content = archive.read("word/document.xml")
        tree = ET.fromstring(xml_content)
        namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        paragraphs = []
        for paragraph in tree.iter(f"{namespace}p"):
            line = "".join(node.text or "" for node in paragraph.iter(f"{namespace}t")).strip()
            if line:
                paragraphs.append(line)
        pages.append({"text": "\n".join(paragraphs), "page": 1, "source": file_obj.name})
    else:
        text = raw.decode("utf-8", errors="ignore")
        blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
        if not blocks:
            blocks = [text]
        for index, block in enumerate(blocks, start=1):
            pages.append({"text": block, "page": index, "source": file_obj.name})

    file_obj.seek(0)
    return pages


def ingest_documents(files):
    from sklearn.feature_extraction.text import TfidfVectorizer

    all_chunks: list[str] = []
    all_ids: list[str] = []
    all_meta: list[dict] = []
    filenames: list[str] = []
    full_texts: list[str] = []
    progress = st.progress(0, text="Reading files…")

    for index, file_obj in enumerate(files):
        progress.progress((index + 0.1) / len(files), text=f"Parsing {file_obj.name}…")
        page_blocks = extract_page_aware(file_obj)
        combined = " ".join(block["text"] for block in page_blocks)
        filenames.append(file_obj.name)
        full_texts.append(combined)

        if is_10k_document(combined):
            sections = split_10k_into_sections(combined)
            for section in sections:
                for chunk_index, chunk in enumerate(chunk_text(section["text"])):
                    if not chunk.strip():
                        continue
                    all_chunks.append(chunk)
                    all_ids.append(f"{file_obj.name}_{section['section_label'][:20]}_{chunk_index}")
                    all_meta.append(
                        {
                            "filename": file_obj.name,
                            "doc_title": file_obj.name.rsplit(".", 1)[0].replace("_", " ").title(),
                            "page": chunk_index + 1,
                            "chunk": chunk_index,
                            "section": section["section_label"],
                            "10k_item": section["section_label"],
                            "is_10k": True,
                            "keywords": extract_chunk_keywords(chunk),
                            "source": file_obj.name,
                            "_index_text": f"[10-K: {section['section_label']}] {chunk}",
                        }
                    )
        else:
            for block in page_blocks:
                for chunk_index, chunk in enumerate(chunk_text(block["text"])):
                    if not chunk.strip():
                        continue
                    section = infer_section(chunk)
                    prefix = f"[{section}] " if section != "General" else ""
                    all_chunks.append(chunk)
                    all_ids.append(f"{file_obj.name}_p{block['page']}_c{chunk_index}")
                    all_meta.append(
                        {
                            "filename": file_obj.name,
                            "doc_title": file_obj.name.rsplit(".", 1)[0].replace("_", " ").title(),
                            "page": block["page"],
                            "chunk": chunk_index,
                            "section": section,
                            "10k_item": block.get("10k_item", ""),
                            "is_10k": False,
                            "keywords": extract_chunk_keywords(chunk),
                            "source": block["source"],
                            "_index_text": f"{prefix}{chunk}".strip(),
                        }
                    )
        progress.progress((index + 1) / len(files), text=f"Processed {file_obj.name}")
    progress.empty()

    vectorizer = None
    tfidf_matrix = None
    if all_chunks:
        with st.spinner(f"Indexing {len(all_chunks)} chunks (TF-IDF)…"):
            vectorizer = TfidfVectorizer(max_features=8000, sublinear_tf=True, ngram_range=(1, 2), min_df=1)
            tfidf_matrix = vectorizer.fit_transform([meta["_index_text"] for meta in all_meta])

    combined_text = " ".join(full_texts)
    auto_metrics = extract_metrics(combined_text)
    clean_meta = [{key: value for key, value in meta.items() if key != "_index_text"} for meta in all_meta]

    st.session_state.vectorstore = {
        "chunks": all_chunks,
        "meta": clean_meta,
        "ids": all_ids,
        "vectorizer": vectorizer,
        "tfidf_matrix": tfidf_matrix,
        "model_label": "TF-IDF",
        "is_bge": False,
        "model": None,
        "collection": None,
    }
    st.session_state.uploaded_docs = len(files)
    st.session_state.chunk_count = len(all_chunks)
    st.session_state.file_names = filenames
    st.session_state.doc_full_text = combined_text
    st.session_state.auto_metrics = auto_metrics
    st.session_state.auto_generated = True
    return len(all_chunks)
