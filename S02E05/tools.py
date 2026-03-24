import base64
import json
import requests
import logging
from openai import OpenAI

from config import (
    VERIFY_URL, API_KEY, TASK, BASE_URL,
    OPENROUTER_API_KEY, VISION_SYSTEM_PROMPT, VISION_MODEL
)

logger = logging.getLogger(__name__)


def get_image_as_base64(url: str) -> str | None:
    """
    Get image as base64.
    """
    try:
        response = requests.get(url, timeout=10)
        # Rzucamy błąd jeśli status nie jest 200
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")
    except Exception as e:
        logger.error(f"Error getting image as base64: {e}")
        return None


def send_drone_instructions(instructions: list[str]) -> str:
    """
    Wyślij instrukcje drona do API.
    """
    payload = {
        "apikey": API_KEY,
        "task": TASK,
        "answer": {
            "instructions": instructions,
        }
    }
    try:
        response = requests.post(VERIFY_URL, json=payload, timeout=15)
        if response.status_code == 200:
            return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"Error sending drone instructions: {e}"
    return response.text


def analyze_map_for_target(url: str) -> str:
    """Narzędzie dla agenta: analizuje mapę i zwraca koordynaty X,Y."""
    logger.info(f"Analyzing map for target {url}")

    base64_image = get_image_as_base64(url)
    if not base64_image:
        return "Error getting image as base64. Check the url."

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": VISION_SYSTEM_PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ]
        }
    ]

    client = OpenAI(
        base_url=BASE_URL,
        api_key=OPENROUTER_API_KEY,
    )

    try:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=messages,
        )
        result = response.choices[0].message.content
        logger.info(f"Result from vision model {VISION_MODEL}: {result}")
        return result
    except Exception as e:
        logger.error(f"Error analyzing map for target: {e}")
        return f"Error analyzing map for target: {e}"


TOOLS_DICT = {
    "send_drone_instructions": send_drone_instructions,
    "analyze_map_for_target": analyze_map_for_target,
}
