import json
import os
from openai import OpenAI
from config import EXTRACT_SYSTEM_PROMPT, TOOLS

# Zakładamy, że klient jest zdefiniowany globalnie lub przekazywany
# client = OpenAI(
#     base_url=os.getenv("BASE_URL"),
#     api_key=os.getenv("OPENROUTER_API_KEY"),
# )


def ask_llm(client: OpenAI, content_data: str, content_type: str) -> dict:
    """
    Wysyła dane do LLM i oczekuje poprawnego JSONa.
    client: klient OpenAI.
    content_data: treść tekstowa lub string base64 dla obrazu.
    content_type: 'text' lub 'image'.
    """

    # System prompt definiujący strukturę odpowiedzi
    messages = [{"role": "system", "content": EXTRACT_SYSTEM_PROMPT}]

    if content_type == "text":
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Extract links and knowledge from this text."
                },
                {
                    "type": "text",
                    "text": content_data
                }
            ]
        })

    elif content_type == "image":
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Extract links and knowledge from this image."
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{content_data}"}
                }
            ]
        })

    try:
        response = client.chat.completions.create(
            model=os.getenv("MODEL_ID"),
            messages=messages,
            response_format={"type": "json_object"}  # Wymusza JSON od modelu
        )

        # Parsowanie odpowiedzi
        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        print(f"Błąd komunikacji z LLM: {e}")
        return {"new_urls": [], "extracted_knowledge": {}}