import os

import streamlit as st
from google import genai

# The key is read by NAME from Render/Streamlit settings. Do not paste it here.
API_KEY = os.environ.get("")
if not API_KEY:
    try:
        API_KEY = st.secrets[""]
    except Exception:
        API_KEY = None

MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.7-flash",
]

MAX_MESSAGES = 40

st.set_page_config(page_title="My AI Chatbot", page_icon="💬")
st.title("💬 My AI Chatbot")
st.caption("Ask me anything. Your chat is private to you and clears when you close the page.")

if not API_KEY:
    st.error("No API key found. Add GEMINI_API_KEY in Secrets (or Environment).")
    st.stop()


@st.cache_resource
def get_client():
    return genai.Client(api_key=API_KEY)


def to_contents(messages):
    recent = messages[-MAX_MESSAGES:]
    while recent and recent[0]["role"] != "user":
        recent = recent[1:]
    return [{"role": m["role"], "parts": [{"text": m["text"]}]} for m in recent]


def get_reply(messages):
    client = get_client()
    errors = []
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model, contents=to_contents(messages)
            )
            return response.text or "I couldn't think of a reply. Try asking differently.", None
        except Exception as e:
            errors.append(f"{model}: {str(e)[:200]}")
    return None, "\n\n".join(errors)


if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Options")
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

for m in st.session_state.messages:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["text"])

prompt = st.chat_input("Type your message...")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "text": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply, err = get_reply(st.session_state.messages)

        if reply is None:
            st.error("All models failed. Details below:")
            st.code(err)
            st.session_state.messages.pop()
        else:
            st.markdown(reply)
            st.session_state.messages.append({"role": "model", "text": reply})
