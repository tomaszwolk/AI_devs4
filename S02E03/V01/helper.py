from dotenv import load_dotenv
import os
import requests
import json
from datetime import datetime
from pathlib import Path
import re

load_dotenv()
HUB_API_KEY = os.getenv("HUB_API_KEY")
VERIFY_URL = "https:///verify"
LOGS_URL = f"https:///data/{HUB_API_KEY}/failure.log"
TASK = "failure"
MODEL_ID = os.getenv("MODEL_ID")


def get_logs() -> str:
    """
    Get logs from the hub.
    """
    response = requests.get(LOGS_URL)
    return response.text


def save_data(data: str, path: Path) -> None:
    """
    Save data to a file.
    """
    with open(path, "w") as f:
        f.write(data)


def create_payload(
    logs: str,
) -> dict:
    """
    Create a payload.
    Pole logs to string - wiersze oddzielone znakiem \n. Każdy wiersz to jedno zdarzenie.
    """
    payload = {
        "apikey": HUB_API_KEY,
        "task": TASK,
        "answer": {
            "logs": logs,
        }
    }
    return payload


def send_payload(payload: dict) -> tuple[int, dict]:
    """
    Send a payload to the hub.
    """
    response = requests.post(VERIFY_URL, json=payload)
    return response.status_code, response.json()


def save_messages_to_file(messages):
    # Generujemy timestamp w formacie: RRRR-MM-DD_HH-MM-SS
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"logs/history_{timestamp}.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Przygotowujemy listę słowników
    serializable_messages = []

    for msg in messages:
        # Konwersja obiektu modelu na słownik, jeśli to konieczne
        if hasattr(msg, 'model_dump'):  # Obsługa obiektów OpenAI/Pydantic
            serializable_messages.append(msg.model_dump())
        elif isinstance(msg, dict):
            serializable_messages.append(msg)
        else:
            serializable_messages.append(str(msg))

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(serializable_messages, f, ensure_ascii=False, indent=4)
    print(f"\nHistoria zapisana do {filename}")


def filter_logs(input_file: Path, output_file: Path, levels: list[str]) -> None:
    """
    Filter logs.
    """
    # Tworzymy wzorzec regex, np.: r"\[WARN\]|\[CRIT\]"
    # re.escape zabezpiecza znaki specjalne, jeśli logi zawierają nawiasy
    pattern = re.compile('|'.join([re.escape(level) for level in levels]))

    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:

        for line in infile:
            # Sprawdzamy, czy w linii występuje którykolwiek z poszukiwanych poziomów
            if pattern.search(line):
                outfile.write(line)


def find_unique_log_levels(file_path):
    # Wzorzec: szukamy tekstu w nawiasach kwadratowych, np. [INFO]
    # \[ dopasowuje znak [, .*? dopasowuje dowolny tekst (niezachłannie), \] dopasowuje ]
    level_pattern = re.compile(r'\[([^\]0-9]+)\]')

    unique_levels = set()

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = level_pattern.search(line)
            if match:
                # match.group(0) zwróci całe dopasowanie, np. "[WARN]"
                unique_levels.add(match.group(0))

    return unique_levels


def filter_unique_logs(input_path, output_path):
    # Zbiór na fragmenty komunikatów, które już widzieliśmy
    seen_messages = set()

    # Regex: [data] [level] reszta_komunikatu
    # Grupa (.*) wyłapie wszystko po "[LEVEL] "
    log_pattern = re.compile(r'\[.*?\] \[(?:.*?)\] (.*)')

    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:

        for line in infile:
            match = log_pattern.search(line)
            if match:
                # Wyciągamy sam komunikat (np. "ECCS8 reported runaway...")
                message_content = match.group(1)

                # Jeśli jeszcze tego komunikatu nie widzieliśmy
                if message_content not in seen_messages:
                    outfile.write(line)
                    seen_messages.add(message_content)
