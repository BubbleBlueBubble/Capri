import requests

# URL
OLLAMA_URL = "http://localhost:11434/api/chat"

# Question for AI
def ask_capricorn(message):
    # response options
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen3.5:4b",
            "stream": False,
            "think": False,
            "messages": [
                {
                    "role": "system",
                    "content": "Ты Capricorn - личный ИИ-компаньон. Ты общаешься естественно, дружелюбно подшучиваешь. Ты стараешься понимать собеседника, учитывать контекст разговора и не выдавать себя за человека."
                },
                *messages
            ],
            "options": {
                            "num_predict": 512
                        },
            
        },
        timeout=120
    )

    response.raise_for_status()


    # answer
    data = response.json()

    ## DEBUG
    # print("\n--- DEBUG ---")
    # print("Полный ответ:", data)
    # print("Сообщение:", repr(data.get("message")))
    # print("Причина завершения:", data.get("done_reason"))
    # print("--- END DEBUG ---\n")
    
    return data["message"]["content"]

# Memory
messages = []

# CHAT
while True:
    user_message = input("Ask: ")

    if user_message.lower() == "выход":
        break

    # MEMORY
    messages.append({
        "role": "user",
        "content": user_message
    })

    answer = ask_capricorn(user_message)

    messages.append({
        "role": "assistant",
        "content": answer
    })

    # ANSWER
    print(f"\nCapricorn: {answer}\n")