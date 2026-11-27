import os
from dotenv import load_dotenv
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

load_dotenv()

chat = Chat(
    model="GigaChat-3-Ultra",
    messages=[
        Messages(
            role=MessagesRole.USER,
            content="Ответь коротко: подключение к Capricorn работает?",
        )
    ],
)

with GigaChat(
    base_url=os.getenv("GIGACHAT_BASE_URL"),
    credentials=os.getenv("GIGACHAT_CREDENTIALS"),
    scope=os.getenv("GIGACHAT_SCOPE"),
    ca_bundle_file=os.getenv("GIGACHAT_CA_BUNDLE_FILE"),
) as client:
    response = client.chat(chat)
    print(response.choices[0].message.content)