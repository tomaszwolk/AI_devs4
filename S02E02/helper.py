from dotenv import load_dotenv
import os
import requests
import base64
load_dotenv()
HUB_API_KEY = os.getenv("HUB_API_KEY")
VERIFY_URL = "https:///verify"
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
