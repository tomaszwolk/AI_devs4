import json
import logging
import re
import requests
import hashlib
import time
from config import settings

logger = logging.getLogger(__name__)
ATTEMPTS = 3

BODY_PREVIEW_LEN = 500


def _json_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _response_debug_fields(response: requests.Response) -> dict:
    """Faktyczna odpowiedź HTTP — do logów i JSON-a błędu."""
    t = response.text
    preview = t if len(t) <= BODY_PREVIEW_LEN else t[:BODY_PREVIEW_LEN] + "…"
    return {
        "http_status": response.status_code,
        "content_type": response.headers.get("Content-Type", ""),
        "body_preview": preview,
    }


def _fix_hub_malformed_json(s: str) -> str:
    """Hub zwraca celowo zepsuty JSON: mieszane ` ' \" oraz brakujące przecinki."""
    s = re.sub(r"[`'](\w+)\":", r'"\1":', s)
    s = re.sub(r'"(\w+)[`\'](\s*:)', r'"\1"\2', s)
    # "tekst',\n lub "tekst',  — zamknięcie wartości apostrofem zamiast "
    s = re.sub(r'"([^"]*?)\'(\s*,)', r'"\1"\2', s)
    s = re.sub(r'"([^"]*?)\'(\s*\n)', r'"\1"\2', s)
    # "wartość"\n    "następnyKlucz" — brak przecinka po stringu przed kolejnym polem
    s = re.sub(r'"(\s*\r?\n\s*")', r'",\1', s)
    # "key": 'wartość", lub 'wartość"\n  (pojedynczy cudzysłów na początku wartości)
    s = re.sub(r"\":\s*'([^\"]*?)\"(\s*,|\s*\n)", r'": "\1"\2', s)
    # "key": "wartość` lub wartość' przed końcem linii
    s = re.sub(r'":\s*"([^"]*?)`(\s*\n)', r'": "\1"\2', s)
    s = re.sub(r"\":\s*\"([^\"]*?)'(\s*\n)", r'": "\1"\2', s)
    # } newline "następnyKlucz" — brak przecinka między polami obiektu
    s = re.sub(r'\}\s*\n(\s*")', r'},\n\1', s)
    s = re.sub(r"(true|false|\d+)\s*\r?\n(\s*\")", r"\1,\n\2", s)
    return s


def _parse_hub_json_body(text: str):
    """Parse JSON z hubu: obiekt {…} (czasem celowo zepsuty), albo inna wartość JSON (string, tablica, itp.)."""
    stripped = text.strip()
    if not stripped:
        raise ValueError("Pusta odpowiedź (brak treści).")
    if stripped[0] == "{":
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            fixed = _fix_hub_malformed_json(stripped)
            try:
                return json.loads(fixed)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Nie udało się sparsować JSON obiektu (nawet po naprawie cudzysłowów): {e}. "
                    f"Początek odpowiedzi: {stripped[:BODY_PREVIEW_LEN]!r}"
                ) from e
    try:
        return json.loads(stripped)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Nie udało się sparsować JSON: {e}. "
            f"Początek odpowiedzi: {stripped[:BODY_PREVIEW_LEN]!r}"
        ) from e


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

    last_failure: dict = {"error": "nieznany"}
    for attempt in range(ATTEMPTS):
        response = None
        try:
            response = requests.post(settings.verify_url, json=payload, timeout=30)
            if response.status_code != 200:
                try:
                    err_data = response.json()
                except Exception:
                    err_data = None
                if err_data is not None and err_data.get("code") == -950:
                    error_code = err_data.get("code")
                    error_msg = err_data.get("message", "Nieznany błąd")
                    logger.warning(
                        "Koniec gry (code %s): %s", error_code, error_msg
                    )
                    return f"Otrzymano kod błędu {error_code}: {error_msg}"
                last_failure = {
                    "error": f"HTTP {response.status_code}",
                    **_response_debug_fields(response),
                }
                logger.error(
                    "verify próba %s/%s: %s", attempt + 1, ATTEMPTS, last_failure
                )
                time.sleep(1)
                continue
            data = response.json()
            # Jeśli kod odpowiedzi jest ujemny, to znaczy, że należy zmienić zapytanie
            if data.get("code", 0) < 0:
                error_code = data.get("code")
                error_msg = data.get("message", "Nieznany błąd")
                logger.warning(
                    "Otrzymano kod błędu %s: %s", error_code, error_msg
                )
                return f"Otrzymano kod błędu {error_code}: {error_msg}"

            return json.dumps(
                data, ensure_ascii=False, indent=4, default=_json_default
            )
        except requests.exceptions.Timeout:
            last_failure = {"error": "Timeout", "detail": "timeout 30s"}
            logger.error("verify timeout próba %s/%s.", attempt + 1, ATTEMPTS)
            time.sleep(1)
        except Exception as e:
            last_failure = {"error": str(e)}
            if response is not None:
                last_failure.update(_response_debug_fields(response))
            logger.error(
                "verify próba %s/%s: %s",
                attempt + 1,
                ATTEMPTS,
                last_failure,
            )
            time.sleep(1)

    return json.dumps(
        {
            "message": f"Nie udało się po {ATTEMPTS} próbach (verify).",
            **last_failure,
        },
        ensure_ascii=False,
    )


def get_radio_hint() -> str:
    payload = {
        "apikey": settings.api_key,
    }

    url = settings.hub_url + "/api/getmessage"
    last_failure: dict = {"error": "nieznany"}
    for attempt in range(ATTEMPTS):
        response = None
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code != 200:
                last_failure = {
                    "error": f"HTTP {response.status_code}",
                    **_response_debug_fields(response),
                }
                logger.error(
                    "getmessage próba %s/%s: %s",
                    attempt + 1,
                    ATTEMPTS,
                    last_failure,
                )
                time.sleep(1)
                continue
            data = response.json()
            return json.dumps(
                data, ensure_ascii=False, indent=4, default=_json_default
            )
        except requests.exceptions.Timeout:
            last_failure = {"error": "Timeout", "detail": "timeout 30s"}
            logger.error(
                "getmessage timeout próba %s/%s.", attempt + 1, ATTEMPTS
            )
            time.sleep(1)
        except Exception as e:
            last_failure = {"error": str(e)}
            if response is not None:
                last_failure.update(_response_debug_fields(response))
            logger.error(
                "getmessage próba %s/%s: %s",
                attempt + 1,
                ATTEMPTS,
                last_failure,
            )
            time.sleep(1)

    return json.dumps(
        {
            "message": f"Nie udało się po {ATTEMPTS} próbach (getmessage).",
            **last_failure,
        },
        ensure_ascii=False,
    )


def scan_frequency() -> str:
    key = settings.api_key
    url = settings.hub_url + "/api/frequencyScanner"
    last_failure: dict = {"error": "nieznany"}
    for attempt in range(ATTEMPTS):
        response = None
        try:
            response = requests.get(url, params={"key": key}, timeout=30)
            if response.status_code != 200:
                last_failure = {
                    "error": f"HTTP {response.status_code}",
                    **_response_debug_fields(response),
                }
                reason = (response.reason or "").strip()
                logger.error(
                    "frequencyScanner próba %s/%s: Error %s %s",
                    attempt + 1,
                    ATTEMPTS,
                    response.status_code,
                    reason,
                )
                time.sleep(1)
                continue
            data = _parse_hub_json_body(response.text)
            return json.dumps(data, ensure_ascii=False, indent=4, default=_json_default)
        except requests.exceptions.Timeout:
            last_failure = {"error": "Timeout", "detail": "timeout 30s"}
            logger.error(
                "frequencyScanner próba %s/%s: Error timeout",
                attempt + 1,
                ATTEMPTS,
            )
            time.sleep(1)
        except Exception as e:
            last_failure = {"error": str(e)}
            if response is not None:
                last_failure.update(_response_debug_fields(response))
            logger.error(
                "frequencyScanner próba %s/%s: %s",
                attempt + 1,
                ATTEMPTS,
                last_failure,
            )
            time.sleep(1)

    return json.dumps(
        {
            "message": f"Nie udało się po {ATTEMPTS} próbach (frequencyScanner).",
            **last_failure,
        },
        ensure_ascii=False,
    )


def neutralize_trap(frequency: int, detectionCode: str) -> str:
    disarmHash = hashlib.sha1((detectionCode + "disarm").encode('utf-8')).hexdigest()

    payload = {
        "apikey": settings.api_key,
        "frequency": frequency,
        "disarmHash": disarmHash,
    }

    url = settings.hub_url + "/api/frequencyScanner"
    last_failure: dict = {"error": "nieznany"}
    for attempt in range(ATTEMPTS):
        response = None
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code != 200:
                last_failure = {
                    "error": f"HTTP {response.status_code}",
                    **_response_debug_fields(response),
                }
                logger.error(
                    "neutralize próba %s/%s: %s",
                    attempt + 1,
                    ATTEMPTS,
                    last_failure,
                )
                time.sleep(1)
                continue
            data = _parse_hub_json_body(response.text)
            return json.dumps(
                data, ensure_ascii=False, indent=4, default=_json_default
            )
        except requests.exceptions.Timeout:
            last_failure = {"error": "Timeout", "detail": "timeout 30s"}
            logger.error(
                "neutralize timeout próba %s/%s.", attempt + 1, ATTEMPTS
            )
            time.sleep(1)
        except Exception as e:
            last_failure = {"error": str(e)}
            if response is not None:
                last_failure.update(_response_debug_fields(response))
            logger.error(
                "neutralize próba %s/%s: %s",
                attempt + 1,
                ATTEMPTS,
                last_failure,
            )
            time.sleep(1)

    return json.dumps(
        {
            "message": f"Nie udało się po {ATTEMPTS} próbach (neutralize).",
            **last_failure,
        },
        ensure_ascii=False,
    )


TOOLS_DICT = {
    "call_verify_api": call_verify_api,
    "get_radio_hint": get_radio_hint,
    "scan_frequency": scan_frequency,
    "neutralize_trap": neutralize_trap,
}
