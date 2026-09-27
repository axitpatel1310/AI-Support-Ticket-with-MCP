import requests

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen2.5:3b"

SYSTEM_PROMPT = """
You are a helpful customer support assistant.
Answer the customer's questions clearly and concisely.
"""

def chat_ollama(user_message: str) -> str:

    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "stream": False
        }
    )

    response.raise_for_status()

    return response.json()["message"]["content"]