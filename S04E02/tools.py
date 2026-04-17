import json
import time
from typing import Any

import requests
from config import settings


def call_verify_api(answer_payload: dict[str, Any]) -> str:
    """
    Verify the answer.
    """
    if isinstance(answer_payload, str):
        answer_payload = {"action": answer_payload}

    payload = {
        "apikey": settings.api_key,
        "task": settings.task,
        "answer": answer_payload,
    }
    if not settings.verify_url:
        raise ValueError("VERIFY_URL is not set")
    response = requests.post(settings.verify_url, json=payload)
    data = response.json()

    # Automatyczny polling dla getResult
    if answer_payload.get("action") == "getResult":
        print("Waiting for result...")
        max_retries = 40
        attempts = 0
        while data.get("code") == 11 and attempts < max_retries:
            time.sleep(0.5)
            response = requests.post(settings.verify_url, json=payload)
            data = response.json()
            attempts += 1
            print(f"Attempt {attempts} of {max_retries}")

    return json.dumps(data)


TOOLS_DICT = {
    "call_verify_api": call_verify_api,
}
