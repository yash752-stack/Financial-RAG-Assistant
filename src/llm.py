from __future__ import annotations

import re
import time as _tm

import streamlit as st
from openai import OpenAI

from .config import GROQ_MODEL


def parse_retry_seconds(err_str: str) -> float:
    match = re.search(r"try again in\s+(?:(\d+)m)?[\s]*([\d.]+)s", err_str, re.IGNORECASE)
    if match:
        minutes = int(match.group(1) or 0)
        seconds = float(match.group(2) or 0)
        return minutes * 60 + seconds
    fallback = re.search(r"([\d.]+)\s*second", err_str, re.IGNORECASE)
    return float(fallback.group(1)) if fallback else 60.0


def groq_call(
    api_key: str,
    messages: list[dict],
    *,
    system: str = "",
    model: str = GROQ_MODEL,
    temperature: float = 0.15,
    max_tokens: int = 600,
    site_key: str = "default",
) -> str:
    if not api_key:
        return "⚠ No API key — add your Groq key in the sidebar."
    if "_groq_last_err" not in st.session_state:
        st.session_state["_groq_last_err"] = {}

    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    payload = [{"role": "system", "content": system}] if system else []
    payload.extend(messages)

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=payload,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            st.session_state["_groq_last_err"].pop(site_key, None)
            return response.choices[0].message.content.strip()
        except Exception as exc:
            err = str(exc)
            is_rate = "rate_limit_exceeded" in err or "429" in err or "Rate limit" in err
            is_overload = "overloaded" in err.lower() or "503" in err or "502" in err
            if is_rate or is_overload:
                wait = parse_retry_seconds(err) if is_rate else 5.0
                wait = wait * (1 + 0.1 * attempt) + (attempt * 2)
                st.session_state["_groq_last_err"][site_key] = {
                    "wait": wait,
                    "msg": err[:200],
                    "type": "rate_limit" if is_rate else "overload",
                }
                if attempt < 2:
                    _tm.sleep(min(wait, 8))
                    continue
                retry_min = max(1, int(wait / 60))
                return (
                    f"⏱ Groq {'rate limit' if is_rate else 'overload'} — retry in ~{retry_min} min.\n"
                    "💡 Upgrade at console.groq.com/settings/billing to remove limits."
                )
            return f"⚠ API error: {err[:200]}"
    return "⚠ Max retries exceeded — Groq API unavailable right now."


def generate_doc_qa_pairs(doc_text: str, groq_api_key: str, n_chunks: int = 3) -> list[dict]:
    if not doc_text.strip() or not groq_api_key:
        return []
    client = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
    words = doc_text.split()
    passages: list[str] = []
    chunk_size = min(600, max(150, len(words) // max(n_chunks, 1)))
    step = max(1, len(words) // max(n_chunks, 1))
    for idx in range(0, len(words), step):
        passage = " ".join(words[idx : idx + chunk_size])
        if len(passage.strip()) > 100:
            passages.append(passage)
    passages = passages[:n_chunks]
    if not passages:
        return []

    prompt = (
        "Generate 4 high-quality financial QA benchmark items from the following document excerpts. "
        "Return JSON list with keys: question, answer, expected_keywords.\n\n"
        + "\n\n".join(f"Passage {i + 1}:\n{passage}" for i, passage in enumerate(passages))
    )
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=0.2,
            max_tokens=900,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content.strip()
        match = re.search(r"\[[\s\S]*\]", content)
        return __import__("json").loads(match.group(0) if match else content)
    except Exception:
        return []


def build_analyst_prompt(question: str, live_context: str, doc_context: str) -> str:
    return (
        "You are an expert buy-side financial analyst.\n\n"
        f"Question:\n{question}\n\n"
        f"Live market context:\n{live_context or 'No live market context available.'}\n\n"
        f"Document context:\n{doc_context or 'No uploaded document context available.'}\n\n"
        "Answer with:\n"
        "1. Direct answer\n"
        "2. Key evidence\n"
        "3. Risks or caveats\n"
        "4. Clear conclusion\n"
        "Always cite the underlying document or market context where possible."
    )

