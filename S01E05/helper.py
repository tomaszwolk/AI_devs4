from dotenv import load_dotenv
import os
import requests

load_dotenv()
HUB_API_KEY = os.getenv("HUB_API_KEY")
VERIFY_URL = "https:///verify"
TASK = "railway"


def create_payload(
    action: str,
    route: str | None = None,
    value: str | None = None
) -> dict:
    """
    Create a payload.
    """
    payload = {
        "apikey": HUB_API_KEY,
        "task": TASK,
        "answer": {
            "action": action,
            "route": route,
            "value": value,
        }
    }
    return payload


def send_payload(payload: dict) -> tuple[int, dict]:
    """
    Send a payload to the hub.
    """
    response = requests.post(VERIFY_URL, json=payload)
    return response.status_code, response.json()
