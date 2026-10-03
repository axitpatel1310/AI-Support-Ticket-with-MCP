import requests
from tools.warranty import check_warranty

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen2.5:3b"

SYSTEM_PROMPT = """
You are a customer support assistant.

Rules:

1. If the customer asks about repair, warranty, free repair,
   paid repair, or warranty coverage, ask for their warranty number.

2. If the customer says they lost their warranty number,
   don't have it, or cannot find it, tell them:
   "No problem. A human support agent will reach out to you."

3. If the customer provides a warranty number, use the
   check_warranty tool.

4. Never guess warranty status yourself.

5. If the tool says the warranty is active, tell the customer
   that their warranty is active and they are eligible for
   warranty repair.

6. If the tool says expired or completed, tell the customer
   that the warranty is no longer active and a human support
   agent will reach out to them.

7. If the warranty number is not found, tell the customer
   that a human support agent will reach out to them.
"""


def chat_ollama(user_message: str) -> str:
    messages = [
        {"role": "system","content": SYSTEM_PROMPT},
        {"role": "user","content": user_message}
        ]
    tools = [{"type": "function",
              "function": {
                "name": "check_warranty",
                "description": "Check warranty status using a warranty number.",
                "parameters": {
                    "type": "object",
                    "properties": {"warranty_number": {"type": "string"}},
                    "required": ["warranty_number"]
            }}}]
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={"model": MODEL,"messages": messages,"stream": False,"tools": tools})
    response.raise_for_status()
    data = response.json()
    assistant_message = data["message"]
    tool_calls = assistant_message.get("tool_calls", [])
    if not tool_calls:
        return assistant_message["content"]
    messages.append(assistant_message)
    for tool_call in tool_calls:
        function_name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]
        if function_name == "check_warranty":
            warranty_number = arguments["warranty_number"]
            tool_result = check_warranty(warranty_number)
            messages.append({
                "role": "tool",
                "content": str(tool_result)
            })
    final_response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={"model": MODEL,"messages": messages,"stream": False,"tools": tools})
    final_response.raise_for_status()
    return final_response.json()["message"]["content"]