import requests
from config import VERIFY_URL, API_KEY, TASK, MAIL_URL
import json
import os
from pathlib import Path
import time


def get_help_data() -> dict:
    """
    Get help data.
    """
    HELP_PATH = Path(__file__).parent / "data" / "help.json"
    if not HELP_PATH.exists():
        os.makedirs(HELP_PATH.parent, exist_ok=True)

    if not HELP_PATH.exists():
        action = "help"
        page = 1
        mail_payload = create_mail_payload(action, page)
        _, response = send_payload(mail_payload, MAIL_URL)
        with open("data/help.json", "w") as f:
            json.dump(response, f, indent=4)
        return json.dumps(response)
    else:
        with open("data/help.json", "r") as f:
            help_data = json.load(f)
    return help_data


def create_payload(
    password: str,
    date: str,
    confirmation_code: str,
) -> dict:
    """
    Create a payload.
    """
    payload = {
        "apikey": API_KEY,
        "task": TASK,
        "answer": {
            "password": password,
            "date": date,
            "confirmation_code": confirmation_code,
        }
    }
    return payload


# Not used
def create_mail_payload(
    action: str,
    page: int = 1,
    perPage: int = 5,
    threadID: int = None,
    ids: str = None,
    query: str = None,
) -> dict:
    """
    Create a payload.
    """
    available_actions: list[str] = get_available_actions()

    if action not in available_actions:
        raise ValueError(
            f"Invalid action: {action}\nAvailable actions: {available_actions}"
        )
    payload = {
        "apikey": API_KEY,
        "action": action,
        "page": page,
        "perPage": perPage,
        "threadID": threadID,
        "ids": ids,
        "query": query,
    }
    return payload


def get_available_actions() -> list[str]:
    """
    Get available actions.
    """
    help_data = get_help_data()
    return list(help_data["actions"].keys())


def send_payload(payload: dict, url: str) -> tuple[int, dict]:
    """
    Send a payload to the hub.
    """
    response = requests.post(url, json=payload)
    return response.status_code, response.json()


def call_zmail_api(**parameters: dict) -> str:
    """
    Call the zmail api.
    """
    available_actions: list[str] = get_available_actions()

    if action not in available_actions:
        raise ValueError(
            f"Invalid action: {action}\nAvailable actions: {available_actions}"
        )
    payload = {"apikey": API_KEY}
    payload.update(parameters)
    _, response = send_payload(payload, MAIL_URL)
    time.sleep(1.5)
    return json.dumps(response)


def verify_answer(date: str, password: str, confirmation_code: str) -> str:
    """
    Verify the answer.
    """
    payload = create_payload(date, password, confirmation_code)
    _, response = send_payload(payload, VERIFY_URL)
    return json.dumps(response)


TOOLS_DICT = {
    "call_zmail_api": call_zmail_api,
    "verify_answer": verify_answer,
}
