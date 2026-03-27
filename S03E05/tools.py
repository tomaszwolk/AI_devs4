import requests
import json

from config import API_KEY, TASK, VERIFY_URL, API_BASE_URL, HUB_ORIGIN


def tool_call(query: str, tool: str) -> str:
    """
    Call a tool.
    """
    payload = {
            "apikey": API_KEY,
            "query": query,
        }

    if tool.startswith("/api"):
        url = HUB_ORIGIN + tool
    else:
        url = API_BASE_URL + tool.lstrip("/")

    response = requests.post(url, json=payload)
    return json.dumps(response.json())


def verify_answer(answer: list[str]) -> str:
    """
    Verify the answer.
    """
    payload = {
            "apikey": API_KEY,
            "task": TASK,
            "answer": answer,
        }
    response = requests.post(VERIFY_URL, json=payload)
    return json.dumps(response.json())


TOOLS_DICT = {
    "tool_call": tool_call,
    "verify_answer": verify_answer,
}
