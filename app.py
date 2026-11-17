import time
from google import genai 
from google.genai import types

client = genai.Client(api_key="AQ.Ab8RN6ITQxyo0x0nqWbZRVdgRTMkYGrBCYdRcCZ7ag07NH5hJA")

chat = client.chats.create(
    model="gemini-3.5-flash-lite",
    config=types.GenerateContentConfig(
        system_instruction="You are an assistant with excellent knowledge who can answer any questions. You are helpful, creative, clever, and friendly. You can also provide relationship advice and health and fitness tips.You also help in relationship advice and health and fitness tips. You are also a good friend and can provide emotional support. You are also a good friend and",
        max_output_tokens=1000,
    ),
)

print("Welcome you ! Type your message and press Enter. Type 'quit' to stop.")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ("quit", "exit"):
        break
    if not user_input:
        continue

    for attempt in range(4):  # try up to 4 times
        try:
            response = chat.send_message(user_input)
            print("Bot:", response.text)
            break
        except Exception as e:
            if "503" in str(e) and attempt < 3:
                print("Google is busy, retrying...")
                time.sleep(3 * (attempt + 1))  # wait 3s, 6s, 9s
            else:
                print("Error:", e)
                break
