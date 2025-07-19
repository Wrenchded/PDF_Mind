import requests
import json

def ask_ollama(messages):
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={"model": "llama3.2", "messages": messages, "stream": True},
            stream=True
        )

        final_response = ""

        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    content = data.get("message", {}).get("content", "")
                    final_response += content
                except json.JSONDecodeError as e:
                    # Log or print for debugging if needed
                    print(f"JSON decode error: {e} for line: {line}")
                    continue

        return final_response if final_response.strip() else "⚠️ No response content from model."

    except Exception as e:
        return f"❌ Failed to connect to Ollama: {str(e)}"