import requests
import os
from dotenv import load_dotenv
import base64

load_dotenv()
hub_api_key = os.getenv("HUB_API_KEY")
verify_url = "https:///verify"
TASK = "sendit"


def create_payload(
    declaration: str
) -> dict:
    """
    Create a payload.
    """
    payload = {
        "apikey": hub_api_key,
        "task": TASK,
        "answer": {
            "declaration": declaration,
        }
    }
    return payload


def send_payload(payload: dict) -> tuple[int, dict]:
    """
    Send a payload to the hub.
    """
    url = "https:///verify"
    response = requests.post(url, json=payload)
    return response.status_code, response.json()


def get_content(url):
    response = requests.get(url)
    if url.lower().endswith(('.png', '.jpg', '.jpeg')):
        # Zwróć dane w formie gotowej dla Vision (np. base64)
        return {"type": "image", "data": base64.b64encode(response.content).decode('utf-8')}
    else:
        # Zwróć tekst
        return {"type": "text", "data": response.text}


def get_urls() -> list[str]:
    """
    Get urls from the hub.
    """
    url = "https:///dane/doc/index.md"
    url_base = "https:///dane/doc/"
    url_list = []

    index_data = get_content(url)
    index_data = index_data["data"]
    if index_data["type"] == "text":
        for line in index_data.split("\n"):
            if line.startswith("[include file="):
                url_list.append(get_url_from_line(line))

    return [url_base + url if not url.startswith(("http://", "https://")) else url for url in url_list]


def get_url_from_line(line: str) -> str:
    """
    Get url from line.
    """
    return line.strip().split("=")[1].strip().replace('"', '').replace(']', '').strip()
