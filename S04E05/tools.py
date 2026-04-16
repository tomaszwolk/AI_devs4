import requests
import logging
import json
import os
from pathlib import Path
from config import settings
from e2b_code_interpreter import Sandbox

logger = logging.getLogger(__name__)


def call_verify_api(**kwargs) -> str:
    """
    Verify the answer.
    """
    # Szukamy właściwego payloadu niezależnie od tego, jak model go nazwał
    if "answer_payload" in kwargs:
        answer_payload = kwargs["answer_payload"]
    elif "answer" in kwargs:
        answer_payload = kwargs["answer"]
    else:
        # Jeśli model pominął nadrzędny klucz i przesłał od razu np. {"action": "reset"}
        answer_payload = kwargs

    payload = {
        "apikey": settings.api_key,
        "task": settings.task,
        "answer": answer_payload
    }
    response = requests.post(settings.verify_url, json=payload)
    data = response.json()

    return json.dumps(data)


def execute_python_code(code: str) -> str:
    """Zwraca: Stdout z konsoli Python w bezpiecznym sandboxie."""
    logger.debug("E2B: run_code (len=%d)", len(code))
    # Sandbox() bez .create() nie tworzy połączenia — wymagane jest Sandbox.create()
    with Sandbox.create() as sandbox:
        execution = sandbox.run_code(code)
        if execution.error:
            return f"Błąd: {execution.error.value}"
        return execution.logs.stdout


def get_help_data():
    HELP_PATH = Path(__file__).parent / "data" / "help.json"
    if not HELP_PATH.exists():
        os.makedirs(HELP_PATH.parent, exist_ok=True)

    if not HELP_PATH.exists():
        help_payload = {
            "apikey": settings.api_key,
            "task": settings.task,
            "answer": {
                "tool": "help"
            }
        }
        response = requests.post(settings.verify_url, json=help_payload)
        data = response.json()
        with open(HELP_PATH, "w") as f:
            json.dump(data, f, indent=4)
        return json.load(f)


TOOLS_DICT = {
    "call_verify_api": call_verify_api,
    "execute_python_code": execute_python_code,
}
