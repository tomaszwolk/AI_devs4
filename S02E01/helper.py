import requests
from dotenv import load_dotenv
import os

load_dotenv()
HUB_API_KEY = os.getenv("HUB_API_KEY")
TASK = "categorize"
VERIFY_URL = "https:///verify"
CATEGORIZE_URL = f"https:///data/{HUB_API_KEY}/categorize.csv"


def get_data() -> str:
    """
    Get data from hub.
    """
    response = requests.get(CATEGORIZE_URL)
    return response.text


def create_payload(prompt: str) -> dict:
    """
    Create payload for hub.
    """
    payload = {
        "apikey": HUB_API_KEY,
        "task": TASK,
        "answer": {
            "prompt": prompt
        }
    }

    return payload


def send_payload(payload: dict) -> tuple[int, dict]:
    """
    Send payload to hub.
    """
    response = requests.post(VERIFY_URL, json=payload)
    return response.status_code, response.json()


def create_send_payload(prompt: str) -> tuple[int, dict]:
    """
    Create and send payload to hub.
    """
    payload = create_payload(prompt)
    status_code, response = send_payload(payload)
    return status_code, response


def reset_prompt() -> tuple[int, dict]:
    """
    Reset prompt.
    """
    payload = create_payload("reset")
    status_code, response = send_payload(payload)
    return status_code, response
