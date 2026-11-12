import requests

OLLAMA_URL = "http://localhost:11434/api/chat"

# Question for AI
def ask_capricorn(message):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen3.5:4b",
            "messages": messages,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()
    return data["message"]["content"]

messages = []

while True:
    user_message = input("Ask: ")

    if user_message.lower() == "выход":
        break

    messages.append({
        "role": "user",
        "content": user_message
    })

    answer = ask_capricorn(user_message)

    messages.append({
        "role": "assistant",
        "content": answer
    })

    print(f"\nCapricorn: {answer}\n")