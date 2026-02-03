import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="OpenRouter Playground", page_icon="🤖", layout="centered")
st.title("🤖 OpenRouter Playground")
st.caption("Choose a model tier (cheap vs top-tier), send a prompt, and compare outputs. Keep your API key private.")

api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
if not api_key:
    st.error("OPENROUTER_API_KEY not found. Add it to a .env file in this folder.")
    st.stop()

MODEL_TIERS = {
    "Cheap (good enough)": {
        "model": "openai/gpt-4o-mini",
        "notes": "Best for summaries, rewrites, extraction, quick drafts."
    },
    "Top-tier (expensive)": {
        "model": "anthropic/claude-3.5-sonnet",
        "notes": "Best for complex reasoning, high-stakes deliverables, tricky debugging."
    }
}

tier = st.selectbox("Model tier", list(MODEL_TIERS.keys()))
model = MODEL_TIERS[tier]["model"]
st.info(f"**Selected model:** `{model}`  \n{MODEL_TIERS[tier]['notes']}")

prompt = st.text_area("Your prompt", height=180, placeholder="Paste your task here…")
temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.2, 0.05)

col1, col2 = st.columns(2)
with col1:
    max_tokens = st.number_input("Max tokens (response length)", min_value=64, max_value=4000, value=800, step=64)
with col2:
    show_debug = st.checkbox("Show debug info", value=False)

def call_openrouter(prompt_text: str):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "OpenRouter Playground",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for a startup VA. Be concise and accurate."},
            {"role": "user", "content": prompt_text},
        ],
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
    }

    t0 = time.time()
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    elapsed = time.time() - t0
    r.raise_for_status()
    data = r.json()
    text = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return text, usage, elapsed, data

if st.button("Run", type="primary", disabled=not prompt.strip()):
    try:
        with st.spinner("Calling model…"):
            answer, usage, elapsed, raw = call_openrouter(prompt.strip())

        st.subheader("✅ Response")
        st.write(answer)

        st.subheader("📌 Meta")
        st.write({
            "tier": tier,
            "model": model,
            "seconds": round(elapsed, 2),
            "usage": usage
        })

        if show_debug:
            st.subheader("🛠 Raw response (debug)")
            st.json(raw)

    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP Error: {e}")
        try:
            st.json(e.response.json())
        except Exception:
            st.write(e.response.text if e.response else "No response body.")
    except Exception as e:
        st.error(f"Error: {e}")
