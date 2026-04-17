import json

import requests
from config import API_KEY, TASK, VERIFY_URL


def call_oko_editor_api(
    action: str,
    page: str | None = None,
    record_id: str | None = None,
    content: str | None = None,
    title: str | None = None,
    is_done: str | None = None,
) -> str:
    """
    Uniwersalne narzędzie do uderzania w endpoint /verify.
    Zbuduje odpowiedni payload w zależności od akcji ('update', 'done').
    """
    answer = {"action": action}

    # Budujemy payload dla akcji update
    if action == "update":
        if page:
            answer["page"] = page
        if record_id:
            answer["id"] = record_id
        if content:
            answer["content"] = content
        if title:
            answer["title"] = title
        if is_done:
            answer["done"] = is_done

    payload = {
        "apikey": API_KEY,
        "task": TASK,
        "answer": answer,
    }

    if not VERIFY_URL:
        raise ValueError("VERIFY_URL is not set")
    try:
        response = requests.post(VERIFY_URL, json=payload)
        try:
            data = response.json()
            return json.dumps(data, ensure_ascii=False)
        except ValueError:
            return json.dumps(
                {
                    "http_status_code": response.status_code,
                    "raw_response_text": response.text,
                },
                ensure_ascii=False,
            )

    except Exception as e:
        return json.dumps(
            {"status": "exception", "message": str(e)}, ensure_ascii=False
        )


def call_verify_api(action: str) -> str:
    """
    Verify the answer.
    """
    payload = {
        "apikey": API_KEY,
        "task": TASK,
        "answer": {"action": action},
    }
    if not VERIFY_URL:
        raise ValueError("VERIFY_URL is not set")
    try:
        response = requests.post(VERIFY_URL, json=payload)
        return json.dumps(response.json())
    except Exception as e:
        return json.dumps(
            {"status": "exception", "message": str(e)}, ensure_ascii=False
        )


TOOLS_DICT = {
    "call_oko_editor_api": call_oko_editor_api,
}
