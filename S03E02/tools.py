import json
import requests
import logging
import time
import textwrap

from config import (VERIFY_URL, API_KEY, TASK, SHELL_URL)

logger = logging.getLogger(__name__)


def run_shell_command(command: str) -> str:
    """
    Wyślij polecenie do shell.
    """
    logger.info(f"Running shell command: {command}")

    payload = {
        "apikey": API_KEY,
        "cmd": command,
    }
    try:
        response = requests.post(SHELL_URL, json=payload, timeout=15)
        data = response.json()
        if "ban" in data:
            ban_info = data["ban"]
            wait_time = ban_info.get(
                "ttl_seconds", ban_info.get("seconds_left", 20)) + 1
            reason = ban_info.get("reason", "Nieznany powód")

            logger.warning(f"Shell command blocked: {reason}. \
            Waiting {wait_time} seconds.")
            time.sleep(wait_time)
            # Zwracamy LLMowi informację o tym, co się stało.
            return textwrap.dedent(
                f"""SYSTEM ERROR:
                Wykonanie komendy '{command}' zakończyło się banem.
                Powód: '{reason}'. Odczekałem karę czasową automatycznie.
                UWAGA: Maszyna wirtualna została przywrócona do stanu początkowego (reboot)!
                Zacznij od nowa i NIE POWTARZAJ tej samej komendy, która złamała zasady."""
            ).strip()

        if response.status_code == 200:
            return json.dumps(data)
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Error sending shell command: {e}"})
    # str(data) dawało repr Pythona (pojedyncze cudzysłowy) — invalid JSON dla json.loads
    return json.dumps(data)


def send_verify_answer(confirmation_code: str) -> str:
    """
    Wyślij odpowiedź do API.
    """
    logger.info(f"Sending verify answer: {confirmation_code}")
    payload = {
        "apikey": API_KEY,
        "task": TASK,
        "answer": {
            "confirmation": confirmation_code,
        }
    }
    try:
        response = requests.post(VERIFY_URL, json=payload, timeout=15)
        data = response.json()
        if response.status_code == 200:
            return json.dumps(data)
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Error sending verify answer: {e}"})
    return json.dumps(data)


TOOLS_DICT = {
    "run_shell_command": run_shell_command,
    "send_verify_answer": send_verify_answer,
}
