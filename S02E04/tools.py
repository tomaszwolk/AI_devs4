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
        mail_payload = {"apikey": API_KEY, "action": "help", "page": 1}
        response = requests.post(MAIL_URL, json=mail_payload)
        data = response.json()
        with open(HELP_PATH, "w") as f:
            json.dump(data, f, indent=4)
        return json.dumps(data)
    else:
        with open(HELP_PATH, "r") as f:
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


def call_zmail_api(**parameters: dict) -> str:
    """
    Call the zmail api.
    """
    # Validate action
    available_actions: list[str] = get_available_actions()
    action = parameters["action"]
    if action not in available_actions:
        raise ValueError(
            f"Invalid action: {action}\nAvailable actions: {available_actions}"
        )

    # Create payload and send request
    payload = {"apikey": API_KEY}
    payload.update(parameters)
    response = requests.post(MAIL_URL, json=payload)
    time.sleep(1.5)
    return json.dumps(response.json())


def verify_answer(date: str, password: str, confirmation_code: str) -> str:
    """
    Verify the answer.
    """
    payload = create_payload(
        password=password,
        date=date,
        confirmation_code=confirmation_code,
    )
    response = requests.post(VERIFY_URL, json=payload)
    return json.dumps(response.json())


TOOLS_DICT = {
    "call_zmail_api": call_zmail_api,
    "verify_answer": verify_answer,
}
