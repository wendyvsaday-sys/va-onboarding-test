import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

st.title("Prompt Model Logger")

# Model selection
models = [
    "anthropic/claude-3-haiku",
    "anthropic/claude-3.5-sonnet",
    "anthropic/claude-3-opus",
    "openai/gpt-4o-mini",
    "openai/gpt-4o",
    "meta-llama/llama-3-70b-instruct",
]

selected_model = st.selectbox("Select Model", models)

# Prompt input
prompt = st.text_area("Enter your prompt", height=150)

if st.button("Send"):
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-key-here":
        st.error("Please set your OPENROUTER_API_KEY in the .env file")
    elif not prompt:
        st.warning("Please enter a prompt")
    else:
        with st.spinner("Generating response..."):
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "HTTP-Referer": "http://localhost:8501",
                    },
                    json={
                        "model": selected_model,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                response.raise_for_status()
                data = response.json()

                st.subheader("Response")
                st.write(data["choices"][0]["message"]["content"])

                st.subheader("Metadata")
                st.json({
                    "model": selected_model,
                    "prompt_tokens": data.get("usage", {}).get("prompt_tokens"),
                    "completion_tokens": data.get("usage", {}).get("completion_tokens"),
                })
            except Exception as e:
                st.error(f"Error: {e}")
