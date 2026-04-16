import logging
import time
from typing import Any

import requests

from config import (VERIFY_URL, API_KEY, TASK, ALLOWED_COMMANDS)

logger = logging.getLogger(__name__)


def send_command(command: str) -> dict[str, Any]:
    """
    Wyślij komendę do API reaktora.
    Zwraca słownik (odpowiedź JSON z API lub błąd).
    """
    logger.info("Sending command: %s", command)
    if command not in ALLOWED_COMMANDS:
        return {
            "error": "Invalid command",
            "allowed_commands": list(ALLOWED_COMMANDS),
        }

    payload = {
        "apikey": API_KEY,
        "task": TASK,
        "answer":
        {
            "command": command
        },
    }
    try:
        response = requests.post(VERIFY_URL, json=payload, timeout=15)
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {e}"}

    try:
        data = response.json()
    except ValueError:
        preview = (response.text or "")[:500]
        return {
            "error": "Response body is not valid JSON",
            "status_code": response.status_code,
            "body_preview": preview,
        }

    if response.status_code != 200:
        logger.warning("Verify HTTP %s: %s", response.status_code, data)
    time.sleep(1)
    return data


TOOLS_DICT = {
    "send_command": send_command,
}
