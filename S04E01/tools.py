import requests
import json
from config import API_KEY, TASK, VERIFY_URL


def call_oko_editor_api(
    action: str,
    page: str = None,
    record_id: str = None,
    content: str = None,
    title: str = None,
    is_done: str = None
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

    try:
        response = requests.post(VERIFY_URL, json=payload)
        try:
            data = response.json()
            return json.dumps(data, ensure_ascii=False)
        except ValueError:
            return json.dumps({
                "http_status_code": response.status_code,
                "raw_response_text": response.text
            }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "status": "exception",
            "message": str(e)
        }, ensure_ascii=False)


def call_verify_api(action: str) -> str:
    """
    Verify the answer.
    """
    payload = {
        "apikey": API_KEY,
        "task": TASK,
        "answer": {
            "action": action
        },
    }
    response = requests.post(VERIFY_URL, json=payload)
    return json.dumps(response.json())


TOOLS_DICT = {
    "call_oko_editor_api": call_oko_editor_api,
}
