from helper import get_urls, get_content
from openai import OpenAI
import os
from dotenv import load_dotenv
from config import SYSTEM_PROMPT, TOOLS
import json
load_dotenv()

queue = ["https:///dane/doc/index.md"]
visited = set()
knowledge_base = {
    "identyfikator_nadawcy": "450202122",
    "punkt_nadawcy": "Gdańsk",
    "punkt_docelowy": "Żarnowiec",
    "waga": 2800,  # kg
    "budżet": 0,  # PP
    "zawartość": "kasety z paliwem do reaktora",
    "uwagi_specjalne": "brak"
} # Tu będziesz zbierać dane do budowy deklaracji
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

while queue:
    current_url = queue.pop(0)
    if current_url in visited:
        continue
    # 1. Pobierz zawartość
    visited.add(current_url)
    content = get_content(current_url)
    # 2. Jeśli tekst -> przekaż do LLM, żeby wyciągnął linki i wiedzę
    if content["type"] == "text":
        response = client.chat.completions.create(
            model=os.getenv("MODEL_ID"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content["data"]}
            ],
            tools=TOOLS,
        )
    # 3. Jeśli obraz -> przekaż do LLM (Vision), żeby opisał zawartość
    if content["type"] == "image":
        response = client.chat.completions.create(
            model=os.getenv("MODEL_ID"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {
                        "type": "text",
                        "text": "Analyze this image and extract information and links."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{content['data']}"}
                    }
                ]}
            ],
            tools=TOOLS,
        )

    # Dodaj nowe znalezione linki do queue
    new_urls = json.loads(response.choices[0].message.content)["new_urls"]
    queue.extend(new_urls)
    # Zapisz zdobytą wiedzę w knowledge_base
    knowledge_base.update(
        json.loads(response.choices[0].message.content)["extracted_knowledge"]
    )
    print(f"Knowledge base: {knowledge_base}")

print(f"Knowledge base: {knowledge_base}")
print(f"Queue: {queue}")
print(f"Visited: {visited}")
print(f"Current URL: {current_url}")
print(f"Content: {content}")
print(f"Response: {response}")
print(f"New URLs: {new_urls}")
