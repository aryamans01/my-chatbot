import os
import time
import streamlit as st
from google import genai
from google.genai import types

# Page configuration
st.set_page_config(page_title="Mean Girlfriend Bot", page_icon="😡", layout="centered")

st.title("😡 Mean Girlfriend Chatbot")
st.caption("Don't expect any sympathy here.")

# 1. Secure API Key Loading
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        st.error("⚠️ API Key not found! Please configure your GEMINI_API_KEY in Streamlit Secrets or environment variables.")
        st.stop()

# 2. Cache the Gemini Client so it doesn't close between re-runs
@st.cache_resource
def get_gemini_client(key):
    return genai.Client(api_key=key)

client = get_gemini_client(api_key)

# 3. Initialize Chat Session in Session State (preserves memory)
if "chat_session" not in st.session_state:
    st.session_state.chat_session = client.chats.create(
        model="gemini-3.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a girlfriend who is very strict and mean to the user. "
                "You are very rude and insulting. You are a very mean girlfriend "
                "who insults the user in every response."
            ),
            max_output_tokens=500,
        ),
    )

# Store message history for UI rendering
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Handle User Input
if user_input := st.chat_input("Say something (at your own risk)..."):
    # Add user message to state & UI
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate assistant response with retry logic
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("*Thinking of a rude comeback...*")
        
        response_text = ""
        for attempt in range(4):
            try:
                response = st.session_state.chat_session.send_message(user_input)
                response_text = response.text
                break
            except Exception as e:
                if "503" in str(e) and attempt < 3:
                    time.sleep(3 * (attempt + 1))
                else:
                    response_text = f"Error: {e}"
                    break
        
        message_placeholder.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
