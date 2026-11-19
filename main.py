import requests
from memory.database import init_db, save_message, get_last_messages, clear_messages

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3.5:4b"
CONTEXT_LIMIT = 20

SYSTEM_PROMPT = (
    "Ты Capricorn — личный ИИ-компаньон. "
    "Ты общаешься естественно, дружелюбно подшучиваешь. "
    "Ты стараешься понимать собеседника, учитывать контекст разговора "
    "и не выдавать себя за человека."
)


def ask_capricorn(messages):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "stream": False,
            "think": False,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                *messages,
            ],
            "options": {
                "num_predict": 512,
            },
        },
        timeout=120,
    )
    response.raise_for_status()

    data = response.json()
    return data["message"]["content"].strip()


def main():
    init_db()
    messages = get_last_messages(CONTEXT_LIMIT)

    print(f"Loaded {len(messages)} messages from memory.")
    print("Commands: /clear — очистить память, /e (или 'выход') — выйти.\n")

    while True:
        try:
            user_message = input("Ask: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nВыход.")
            break

        if not user_message:
            continue

        command = user_message.lower()

        if command in ("выход", "/e"):
            break

        if command == "/clear":
            clear_messages()
            messages.clear()
            print("Память очищена.\n")
            continue

        user_data = {"role": "user", "content": user_message}

        try:
            answer = ask_capricorn([*messages, user_data])
        except requests.RequestException as error:
            print(f"\nОшибка запроса к Ollama: {error}\n")
            continue

        assistant_data = {"role": "assistant", "content": answer}

        save_message("user", user_message)
        save_message("assistant", answer)

        messages.append(user_data)
        messages.append(assistant_data)
        messages = messages[-CONTEXT_LIMIT:]

        print(f"\nCapricorn: {answer}\n")


if __name__ == "__main__":
    main()