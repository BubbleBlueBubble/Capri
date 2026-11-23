import json
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3.5:4b"

EXTRACTOR_PROMPT = """Ты модуль долговременной памяти ИИ-ассистента.
Извлекай из нового сообщения пользователя ТОЛЬКО важные долгосрочные факты о самом пользователе (имя, возраст, город, учёба/работа, техника и софт, проекты, увлечения, предпочтения, цели).

Правила:
1. Игнорируй приветствия, вопросы, просьбы, шутки и временные состояния.
2. Если факт обновляет уже известный — используй ТОТ ЖЕ key из списка известных фактов.
3. category выбирай строго из: profile, preferences, projects, tech, other.
4. key пиши коротко на английском в snake_case (например: name, city, gpu, main_project).
5. value пиши кратко и по сути.
6. Верни СТРОГО JSON-объект формата:
{"facts": [{"category": "...", "key": "...", "value": "..."}]}
Если новых важных фактов нет, верни: {"facts": []}"""


def extract_facts(user_message, existing_facts=None):
    if existing_facts:
        facts_text = "\n".join(
            f"- [{fact['category']}] {fact['key']}: {fact['value']}"
            for fact in existing_facts
        )
    else:
        facts_text = "пока нет"

    user_content = (
        f"Уже известные факты:\n{facts_text}\n\n"
        f"Новое сообщение пользователя:\n{user_message}"
    )

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "stream": False,
            "think": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": EXTRACTOR_PROMPT},
                {"role": "user", "content": user_content},
            ],
            "options": {
                "temperature": 0,
                "num_predict": 256,
            },
        },
        timeout=120,
    )
    response.raise_for_status()

    data = response.json()

    try:
        result = json.loads(data["message"]["content"])
    except (json.JSONDecodeError, KeyError, TypeError):
        return []

    return result.get("facts", [])


if __name__ == "__main__":
    tests = [
        (
            "У меня ноутбук с RTX 4050 и я разрабатываю ИИ-компаньона Capricorn на Python.",
            None,
        ),
        (
            "Привет! Объясни, чем список отличается от кортежа?",
            None,
        ),
        (
            "Кстати, я обновил видеокарту на RTX 4070.",
            [{"category": "tech", "key": "gpu", "value": "RTX 4050"}],
        ),
    ]

    for message, facts in tests:
        print(f"\nСообщение: {message}")
        print("Результат:", extract_facts(message, facts))