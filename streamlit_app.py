import streamlit as st
from google import genai

# On Streamlit Cloud the key comes from "Secrets" (safe).
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = "your-gemini-key-here"  # LOCAL ONLY

# Models are tried in order. If one is busy or fails, the next one is used.
MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.7-flash",
]

MAX_MESSAGES = 40  # only the latest messages are sent to the model

st.set_page_config(page_title="My AI Chatbot", page_icon="💬")
st.title("💬 My AI Chatbot")
st.caption("Ask me anything. Your chat is private to you and clears when you close the page.")


@st.cache_resource
def get_client():
    return genai.Client(api_key=API_KEY)


def to_contents(messages):
    recent = messages[-MAX_MESSAGES:]
    while recent and recent[0]["role"] != "user":  # must start with a user message
        recent = recent[1:]
    return [{"role": m["role"], "parts": [{"text": m["text"]}]} for m in recent]


def get_reply(messages):
    client = get_client()
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model, contents=to_contents(messages)
            )
            return response.text or "I couldn't think of a reply. Try asking differently."
        except Exception as e:
            print(f"{model} failed: {str(e)[:100]}")
    return None


# Each visitor gets their own chat, stored only in their own session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("Options")
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

# Show the earlier messages
for m in st.session_state.messages:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["text"])

# Chat box at the bottom of the page
prompt = st.chat_input("Type your message...")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "text": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = get_reply(st.session_state.messages)

        if reply is None:
            st.error("All models are busy or failed. Please try again in a minute.")
            st.session_state.messages.pop()  # forget the message that got no answer
        else:
            st.markdown(reply)
            st.session_state.messages.append({"role": "model", "text": reply})
