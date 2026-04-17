import base64
import json
import logging

import requests
from config import (
    API_KEY,
    OPENROUTER_API_KEY,
    OPENROUTER_URL,
    TASK,
    VERIFY_URL,
    VISION_MODEL,
    VISION_SYSTEM_PROMPT,
)
from openai import OpenAI

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
        },
    }
    try:
        if not VERIFY_URL:
            raise ValueError("VERIFY_URL is not set")
        response = requests.post(VERIFY_URL, json=payload, timeout=15)
        if response.status_code == 200:
            return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"Error sending drone instructions: {e}"
    return response.text


def analyze_map_for_target(url: str) -> str | None:
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
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                },
            ],
        }
    ]

    client = OpenAI(
        base_url=OPENROUTER_URL,
        api_key=OPENROUTER_API_KEY,
    )
    if not VISION_MODEL:
        raise ValueError("VISION_MODEL is not set")
    try:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=messages,  # type: ignore
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
