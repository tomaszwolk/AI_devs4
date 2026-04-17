import json
import logging

import requests
from config import settings

logger = logging.getLogger(__name__)


def _json_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def call_verify_api(**kwargs) -> str:
    if "answer_payload" in kwargs:
        answer_payload = kwargs["answer_payload"]
    elif "answer" in kwargs:
        answer_payload = kwargs["answer"]
    else:
        answer_payload = kwargs

    payload = {
        "apikey": settings.api_key,
        "task": settings.task,
        "answer": answer_payload,
    }

    if not settings.verify_url:
        raise ValueError("VERIFY_URL is not set")
    try:
        response = requests.post(settings.verify_url, json=payload, timeout=30)
        data = response.json()
    except requests.exceptions.Timeout:
        return json.dumps({"error": "Timeout. Spróbuj ponownie."}, ensure_ascii=False)
    except Exception as e:
        return json.dumps(
            {"error": f"Błąd API lub parsowania: {e}"}, ensure_ascii=False
        )

    # Jeśli kod odpowiedzi jest ujemny, to znaczy, że należy zmienić zapytanie
    if data.get("code", 0) < 0:
        error_code = data.get("code")
        error_msg = data.get("message", "Nieznany błąd")
        logger.warning(f"Otrzymano kod błędu {error_code}: {error_msg}")
        return f"Otrzymano kod błędu {error_code}: {error_msg}"

    return json.dumps(data, ensure_ascii=False, indent=4, default=_json_default)


TOOLS_DICT = {
    "call_verify_api": call_verify_api,
}
