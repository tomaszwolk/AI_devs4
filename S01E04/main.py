from helper import get_content
from llm import ask_llm
from openai import OpenAI
import os
from dotenv import load_dotenv
from config import SYSTEM_PROMPT, TOOLS
from pprint import pprint

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
}

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

while queue:
    current_url = queue.pop(0)
    print(f"Current URL: {current_url}")
    if current_url in visited:
        continue
    # 1. Pobierz zawartość
    visited.add(current_url)
    content = get_content(current_url)
    # 2. Przekaż do LLM, żeby wyciągnął linki i wiedzę
    response = ask_llm(client, content["data"], content["type"])

    # Dodaj nowe znalezione linki do queue
    for url in response.get("new_urls", []):
        full_url = (url if url.startswith(("http://", "https://"))
                    else f"https:///dane/doc/{url}")
        if full_url not in visited:
            queue.append(full_url)

    # Zapisz zdobytą wiedzę w knowledge_base
    knowledge_base.update(
        response.get("extracted_knowledge", {})
    )

pprint(f"Knowledge base: {knowledge_base}")
pprint(f"Visited: {visited}")


