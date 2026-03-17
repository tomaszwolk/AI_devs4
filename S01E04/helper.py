import requests
import os
import re
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
        return {
            "type": "image",
            "data": base64.b64encode(response.content).decode('utf-8'),
        }
    else:
        # Zwróć tekst
        return {"type": "text", "data": response.text}


def extract_links_from_text(text: str) -> list[str]:
    """
    Extract links from text.
    """
    pattern = r'(?:\[include file=|\]\()([^\]\)]+)(?:\)|\])'
    return re.findall(pattern, text)


def get_clean_urls(raw_links: list[str]) -> list[str]:
    """
    Get clean urls from the hub.
    """
    cleaned_urls = []
    for raw_link in raw_links:
        clean_link = raw_link.strip().replace('"', '').replace("'", "").strip()
        if clean_link.startswith(("http://", "https://")):
            cleaned_urls.append(clean_link)
        elif clean_link.startswith("#") or not clean_link:
            continue
        elif clean_link.endswith((".md", ".png", ".jpg", ".jpeg")):
            cleaned_urls.append(
                f"https:///dane/doc/{clean_link}"
            )
    return list[str](set[str](cleaned_urls))
