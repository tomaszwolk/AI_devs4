from dotenv import load_dotenv
import os
import requests
import base64
import json
from datetime import datetime

load_dotenv()
HUB_API_KEY = os.getenv("HUB_API_KEY")
HUB_URL = os.getenv("HUB_URL")
VERIFY_URL = HUB_URL + "/verify"
TASK = "electricity"


def create_payload(
    rotate: str,
) -> dict:
    """
    Create a payload.
    """
    payload = {
        "apikey": HUB_API_KEY,
        "task": TASK,
        "answer": {
            "rotate": rotate,
        }
    }
    return payload


def send_payload(payload: dict) -> tuple[int, dict]:
    """
    Send a payload to the hub.
    """
    response = requests.post(VERIFY_URL, json=payload)
    return response.status_code, response.json()


def get_image(url: str) -> str:
    """
    Get image from hub.
    """
    response = requests.get(url)
    if url.lower().endswith(('.png', '.jpg', '.jpeg')):
        mime = "image/png" if url.lower().endswith(".png") else "image/jpeg"
        b64 = base64.b64encode(response.content).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    return base64.b64encode(response.content).decode("utf-8")


def rotate_field(rotate: str) -> str:
    """
    Rotate field.
    """
    payload = create_payload(rotate)
    status_code, response = send_payload(payload)
    return status_code, response


def reset_board() -> str:
    """
    Reset board.
    """
    url = VERIFY_URL + "?reset=1"
    response = requests.get(url)
    return response.status_code, response.json()


def analyze_board(image_base64: str) -> str:
    """
    Analizuje obraz i zwraca tekstowy opis stanu pól 1x1 do 3x3.
    """
    # Ta funkcja w kodzie jest "stubem" (zaślepką),
    # ponieważ to LLM ma ją wykonać.
    # W praktyce, w system prompt, musisz powiedzieć LLM-owi:
    # "Jeśli nie znasz stanu planszy, wywołaj get_image, a potem analyze_board".
    return "ANALIZA_POTRZEBNA"


def save_messages_to_file(messages):
    # Generujemy timestamp w formacie: RRRR-MM-DD_HH-MM-SS
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"logs/history_{timestamp}.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Przygotowujemy listę słowników
    serializable_messages = []

    for msg in messages:
        # Konwersja obiektu modelu na słownik, jeśli to konieczne
        if hasattr(msg, 'model_dump'):  # Obsługa obiektów OpenAI/Pydantic
            serializable_messages.append(msg.model_dump())
        elif isinstance(msg, dict):
            serializable_messages.append(msg)
        else:
            serializable_messages.append(str(msg))

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(serializable_messages, f, ensure_ascii=False, indent=4)
    print(f"\nHistoria zapisana do {filename}")
