import os
from dotenv import load_dotenv
from gigachat import GigaChat

load_dotenv()

with GigaChat(
    base_url=os.getenv("GIGACHAT_BASE_URL"),
    credentials=os.getenv("GIGACHAT_CREDENTIALS"),
    scope=os.getenv("GIGACHAT_SCOPE"),
    ca_bundle_file=os.getenv("GIGACHAT_CA_BUNDLE_FILE"),
) as client:
    models = client.get_models()

    print("Доступные модели:")
    for model in models.data:
        print("-", model.id_)