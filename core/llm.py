import os

import streamlit as st
from openai import OpenAI

MODEL = "openai/gpt-4o-mini"
SYSTEM = ("You are a sales advisor for a small general store owner. Use ONLY the data summary below. "
          "Be concise and concrete, plain language, no jargon. Give numbered actions with expected impact. "
          "If the data does not support an answer, say so.")


def _key():
    try:
        return st.secrets.get("OPENROUTER_API_KEY", "") or os.getenv("OPENROUTER_API_KEY", "")
    except Exception:
        return os.getenv("OPENROUTER_API_KEY", "")


def ask(messages, context):
    key = _key()
    if not key or key.startswith("paste-"):
        return "⚠️ Add your OPENROUTER_API_KEY to .streamlit/secrets.toml and restart the app."
    try:
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=key)
        r = client.chat.completions.create(
            model=MODEL, temperature=0.3, max_tokens=700,
            messages=[{"role": "system", "content": f"{SYSTEM}\n\nDATA SUMMARY:\n{context}"}] + messages[-8:])
        return r.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI request failed: {e}"


def chat_panel(context: str):
    """Chat box shown at the bottom of every page. `context` = this page's results as text."""
    st.divider()
    st.subheader("💬 Ask the AI advisor")
    hist = st.session_state.setdefault("chat", [])
    for m in hist:
        st.chat_message(m["role"]).write(m["content"])
    if q := st.chat_input("e.g. What should I restock this week?"):
        hist.append({"role": "user", "content": q})
        st.chat_message("user").write(q)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                a = ask(hist, context)
            st.write(a)
        hist.append({"role": "assistant", "content": a})
