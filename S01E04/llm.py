import json
import os

from config import DECLARATION_SYSTEM_PROMPT, EXTRACT_SYSTEM_PROMPT
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion import ChatCompletion

DECLARATION_TEMPLATE = """
SYSTEM PRZESYŁEK KONDUKTORSKICH - DEKLARACJA ZAWARTOŚCI
======================================================
DATA: [YYYY-MM-DD]
PUNKT NADAWCZY: [miasto nadania]
------------------------------------------------------
NADAWCA: [identyfikator płatnika]
PUNKT DOCELOWY: [miasto docelowe]
TRASA: [kod trasy]
------------------------------------------------------
KATEGORIA PRZESYŁKI: A/B/C/D/E
------------------------------------------------------
OPIS ZAWARTOŚCI (max 200 znaków): [...]
------------------------------------------------------
DEKLAROWANA MASA (kg): [...]
------------------------------------------------------
WDP: [liczba]
------------------------------------------------------
UWAGI SPECJALNE: [...]
------------------------------------------------------
KWOTA DO ZAPŁATY: [PP]
------------------------------------------------------
OŚWIADCZAM, ŻE PODANE INFORMACJE SĄ PRAWDZIWE.
BIORĘ NA SIEBIE KONSEKWENCJĘ ZA FAŁSZYWE OŚWIADCZENIE.
======================================================
"""


def ask_llm(client: OpenAI, knowledge_base: dict) -> dict:
    """
    Wysyła dane do LLM i oczekuje poprawnego JSONa.
    client: klient OpenAI.
    content_data: treść tekstowa lub string base64 dla obrazu.
    content_type: 'text' lub 'image'.
    """
    model_id = os.getenv("MODEL_ID")
    if not model_id:
        raise ValueError("MODEL_ID is not set")

    # System prompt definiujący strukturę odpowiedzi
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": DECLARATION_SYSTEM_PROMPT}
    ]

    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Wypełnij deklarację transportową na podstawie dostarczonej bazy wiedzy i zwróć wypełnioną deklarację w formacie JSON.",
                },
                {"type": "text", "text": f"Baza wiedzy: {knowledge_base}"},
                {"type": "text", "text": f"Wzór deklaracji: {DECLARATION_TEMPLATE}"},
            ],
        }
    )

    try:
        response: ChatCompletion = client.chat.completions.create(
            model=model_id,
            messages=messages,
            response_format={"type": "json_object"},  # Wymusza JSON od modelu
        )

        # Parsowanie odpowiedzi
        result = (
            json.loads(response.choices[0].message.content)
            if response.choices[0].message.content
            else {}
        )
        return result

    except Exception as e:
        print(f"Błąd komunikacji z LLM: {e}")
        return {"new_urls": [], "extracted_knowledge": {}}


def ask_llm_extract_text(client: OpenAI, content_data: str, current_kb: dict) -> dict:
    """
    Wysyła dane do LLM i oczekuje poprawnego JSONa.
    client: klient OpenAI.
    """
    model_id = os.getenv("MODEL_ID")
    if not model_id:
        raise ValueError("MODEL_ID is not set")

    # System prompt definiujący strukturę odpowiedzi
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": EXTRACT_SYSTEM_PROMPT}
    ]

    messages.append(
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Uzupełnij bazę wiedzy na podstawie tekstu."},
                {"type": "text", "text": content_data},
                {"type": "text", "text": f"Baza wiedzy: {current_kb}"},
                {"type": "text", "text": f"Wzór deklaracji: {DECLARATION_TEMPLATE}"},
            ],
        }
    )

    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
            response_format={"type": "json_object"},  # Wymusza JSON od modelu
        )

        # Parsowanie odpowiedzi
        result = (
            json.loads(response.choices[0].message.content)
            if response.choices[0].message.content
            else {}
        )
        return result

    except Exception as e:
        print(f"Błąd komunikacji z LLM: {e}")
        return {"new_urls": [], "extracted_knowledge": {}}


def ask_llm_extract_image(client: OpenAI, content_data: str, current_kb: dict) -> dict:
    """
    Wysyła dane do LLM i oczekuje poprawnego JSONa.
    client: klient OpenAI.
    """
    model_id = os.getenv("MODEL_ID")
    if not model_id:
        raise ValueError("MODEL_ID is not set")

    # System prompt definiujący strukturę odpowiedzi
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": EXTRACT_SYSTEM_PROMPT}
    ]

    messages.append(
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Uzupełnij bazę wiedzy na podstawie obrazu."},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{content_data}"},
                },
                {"type": "text", "text": f"Baza wiedzy: {current_kb}"},
                {"type": "text", "text": f"Wzór deklaracji: {DECLARATION_TEMPLATE}"},
            ],
        }
    )

    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
            response_format={"type": "json_object"},  # Wymusza JSON od modelu
        )

        # Parsowanie odpowiedzi
        result = (
            json.loads(response.choices[0].message.content)
            if response.choices[0].message.content
            else {}
        )
        return result

    except Exception as e:
        print(f"Błąd komunikacji z LLM: {e}")
        return {"new_urls": [], "extracted_knowledge": {}}
