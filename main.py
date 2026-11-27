import requests, os
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from memory.database import (
    init_db,
    save_message,
    get_last_messages,
    clear_messages,
    get_all_facts,
    save_fact,
)
from memory.extractor import extract_facts

load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3.5:4b"
CONTEXT_LIMIT = 20

SYSTEM_PROMPT = (
    "Ты Capricorn — личный ИИ-компаньон. "
    "Ты общаешься естественно, дружелюбно подшучиваешь. "
    "Ты стараешься понимать собеседника, учитывать контекст разговора "
    "и не выдавать себя за человека."
)



def build_system_prompt(facts):
    if not facts:
        return SYSTEM_PROMPT

    facts_text = "\n".join(
        f"- [{fact['category']}] {fact['key']}: {fact['value']}"
        for fact in facts
    )
    return (
        f"{SYSTEM_PROMPT}\n\n"
        "Известные факты о собеседнике "
        "(используй их естественно, когда они относятся к разговору):\n"
        f"{facts_text}"
    )


def ask_gigachat(messages, facts):
    role_map = {
        "user": MessagesRole.USER,
        "assistant": MessagesRole.ASSISTANT,
    }

    giga_messages = [
        Messages(
            role=MessagesRole.SYSTEM,
            content=build_system_prompt(facts),
        )
    ]

    for message in messages:
        giga_messages.append(
            Messages(
                role=role_map[message["role"]],
                content=message["content"],
            )
        )

    chat = Chat(
        model="GigaChat-3-Ultra",
        messages=giga_messages,
    )

    with GigaChat(
        base_url=os.getenv("GIGACHAT_BASE_URL"),
        credentials=os.getenv("GIGACHAT_CREDENTIALS"),
        scope=os.getenv("GIGACHAT_SCOPE"),
        ca_bundle_file=os.getenv("GIGACHAT_CA_BUNDLE_FILE"),
    ) as client:
        response = client.chat(chat)

    return response.choices[0].message.content.strip()


def ask_ollama(messages, facts):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "stream": False,
            "think": False,
            "messages": [
                {"role": "system", "content": build_system_prompt(facts)},
                *messages,
            ],
            "options": {
                "num_predict": 512,
            },
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"].strip()


def ask_capricorn(messages, facts):
    provider = os.getenv("LLM_PROVIDER", "gigachat").strip().lower()

    if provider == "ollama":
        print("\n[Провайдер] Основной чат: Ollama.")
        return ask_ollama(messages, facts)

    if provider != "gigachat":
        raise ValueError(
            f"Неизвестный LLM_PROVIDER: {provider}. Используй gigachat или ollama."
        )

    try:
        answer = ask_gigachat(messages, facts)
        print("\n[Провайдер] Ответ получен от GigaChat.")
        return answer
    except Exception as error:
        print(
            f"\n[Провайдер] GigaChat не сработал: {error}\n"
            "Переключаюсь на Ollama."
        )
        answer = ask_ollama(messages, facts)
        print("[Провайдер] Ответ получен от Ollama (резервный вариант).")
        return answer



def main():
    init_db()
    messages = get_last_messages(CONTEXT_LIMIT)
    print("Commands: /clear — очистить память, /facts — показать факты, /e (или 'выход') — выйти.\n")

    while True:
        try:
            user_message = input("Ask: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nВыход.")
            break

        if not user_message:
            continue

        command = user_message.lower()

        if command in ("выход", "/e", "/exit"):
            break

        if command == "/clear":
            clear_messages()
            messages.clear()
            print("Память очищена.\n")
            continue

        if command == "/facts":
            print(get_all_facts())
            continue

        user_data = {"role": "user", "content": user_message}

                # Пытаемся извлечь долгосрочные факты из сообщения
        try:
            existing_facts = get_all_facts()
            new_facts = extract_facts(user_message, existing_facts)

            for fact in new_facts:
                save_fact(
                    fact["category"],
                    fact["key"],
                    fact["value"],
                )
                print(f"Запомнила: {fact['key']} — {fact['value']}")

        except requests.RequestException as error:
            print(f"\nНе удалось обновить факты памяти: {error}\n")

        try:
            answer = ask_capricorn([*messages, user_data], get_all_facts())
        except Exception as error:
            print(f"\nОшибка запроса к моделям: {error}\n")
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