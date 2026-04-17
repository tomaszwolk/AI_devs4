import os
from pprint import pprint

from dotenv import load_dotenv
from helper import (
    create_payload,
    extract_links_from_text,
    get_clean_urls,
    get_content,
    send_payload,
)
from llm import ask_llm, ask_llm_extract_image, ask_llm_extract_text
from openai import OpenAI

load_dotenv()
hub_url = os.getenv("HUB_URL")
# Get list of urls to visit
queue = [f"{hub_url}/dane/doc/index.md"]
extracted = extract_links_from_text(get_content(queue[0])["data"])
cleaned_urls = get_clean_urls(extracted)
queue.extend(cleaned_urls)
print(f"Queue: {queue}")

visited = set()
knowledge_base = {
    "identyfikator_nadawcy": "450202122",
    "punkt_nadawcy": "Gdańsk",
    "punkt_docelowy": "Żarnowiec",
    "waga": 2800,  # kg
    "budżet": 0,  # PP - przesyłka ma być darmowa lub finansowana przez system
    "zawartość": "kasety z paliwem do reaktora",
    "uwagi_specjalne": "brak",
}

client = OpenAI(
    base_url=os.getenv("OPENROUTER_URL"),
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
    print(f"Content type: {content['type']}")
    if content["type"] == "text":
        response = ask_llm_extract_text(client, content["data"], knowledge_base)
    elif content["type"] == "image":
        response = ask_llm_extract_image(client, content["data"], knowledge_base)
    else:
        print(f"Unknown content type: {content['type']}")
        continue

    # Zapisz zdobytą wiedzę w knowledge_base
    knowledge_base.update(response.get("extracted_knowledge", {}))

pprint(f"Knowledge base: {knowledge_base}")
pprint(f"Visited: {visited}")

declaration = ask_llm(client, knowledge_base)
print(f"Declaration: {declaration}")

payload = create_payload(declaration["declaration"])
print(f"Payload: {payload}")

status_code, response = send_payload(payload)
print(f"Status code: {status_code}")
print(f"Response: {response}")
