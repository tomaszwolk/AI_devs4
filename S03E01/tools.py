import json
import requests
import logging
import os
import textwrap

from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI
from config import (
    VERIFY_URL, API_KEY, TASK, RANGES, BASE_URL, OPENROUTER_API_KEY, MAIN_MODEL
)

logger = logging.getLogger(__name__)
client = OpenAI(
    base_url=BASE_URL,
    api_key=OPENROUTER_API_KEY,
)


def process_files(files_dir) -> tuple[set[str], set[str], dict[str, str]]:
    """
    Process files and find anomalies.
    Returns tuple of sets: anomalies_ids, unique_notes, file_notes_mapping.
    anomalies_ids: set of file ids with anomalies.
    unique_notes: set of unique notes.
    file_notes_mapping: dictionary of file ids and their notes.
    """
    anomalies_ids = set()
    unique_notes = set()
    file_notes_mapping = {}

    for filename in os.listdir(files_dir):
        with open(os.path.join(files_dir, filename)) as f:
            data = json.load(f)
            file_id = filename.replace('.json', '')

            # Pobieramy aktywne czujniki
            active_sensors = data["sensor_type"].split('/')
            is_data_bad = False

            for sensor_name, (key, min_val, max_val) in RANGES.items():
                val = data.get(key, 0)

                if sensor_name in active_sensors:
                    # Reguła 1: Czujnik aktywny, ale wartość poza normą
                    if not (min_val <= val <= max_val):
                        is_data_bad = True
                else:
                    # Reguła 4: Czujnik nieaktywny, a zwraca wartość inną niż 0
                    if val != 0:
                        is_data_bad = True

            if is_data_bad:
                # Jeśli dane są złe, to na pewno jest anomalia
                # (niezależnie od notatki)
                anomalies_ids.add(file_id)
            else:
                # Zbieramy notatki do sprawdzenia dla plików z POPRAWNYMI
                # danymi (bo jeśli dane są poprawne, a operator mówi "ERROR",
                # to też jest anomalia)
                note = data["operator_notes"]
                unique_notes.add(note)
                file_notes_mapping[file_id] = note

    return anomalies_ids, unique_notes, file_notes_mapping


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10))
def evaluate_fragment_with_llm(fragment: str) -> str:
    user_prompt = textwrap.dedent("""Jesteś asystentem w elektrowni.
    Oceń fragment notatki operatora.
    Jeśli wskazuje na normę/brak akcji/poprawne działanie zwróć 'OK'.
    Jeśli wskazuje na awarię, odchylenie, błąd lub problem zwróć 'ERROR'.
    Zwróć tylko 'OK' lub 'ERROR', bez żadnej interpunkcji.
    """).strip()

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_prompt},
                {"type": "text", "text": f"Fragment: {fragment}"},
            ]
        }
    ]

    try:
        response = client.chat.completions.create(
            model=MAIN_MODEL,
            messages=messages,
            temperature=0.0,
            max_tokens=16
        )
        result = response.choices[0].message.content.strip()
        logger.info(f"Result from main model {MAIN_MODEL} \
            for fragment: {fragment} is: {result}")
        return result
    except Exception as e:
        raise RuntimeError(f"Error evaluating fragment with LLM: {e}") from e


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=10))
def evaluate_full_note_with_llm(full_note: str) -> str:
    system_prompt = textwrap.dedent("""
        Jesteś głównym audytorem w elektrowni. Twoim zadaniem jest ocena całych notatek operatora.
        Zwróć 'ERROR' TYLKO I WYŁĄCZNIE wtedy, gdy operator wyraźnie zgłasza awarię, niepokojące odchylenie, uszkodzenie czujnika lub prosi o interwencję.
        Zwróć 'OK', jeśli notatka wskazuje na normalne działanie, rutynowy audyt, kontynuację pracy lub brak akcji.
        Zwróć TYLKO jedno słowo: OK lub ERROR.
    """).strip()

    messages = [
        {"role": "system", "content": system_prompt},
        # Dodajemy przykłady (Few-Shot), żeby nakierować mały model Nano:
        {"role": "user", "content": "Notatka: so the shift can proceed as planned for this capture moment."},
        {"role": "assistant", "content": "OK"},
        {"role": "user", "content": "Notatka: so I logged it as routine for this routine audit."},
        {"role": "assistant", "content": "OK"},
        {"role": "user", "content": "Notatka: Temperature is exceeding the maximum threshold, needs immediate check."},
        {"role": "assistant", "content": "ERROR"},
        {"role": "user", "content": "Notatka: Everything is fine, but voltage dropped to 0."},
        {"role": "assistant", "content": "ERROR"},
        # Właściwe zapytanie
        {"role": "user", "content": f"Notatka: {full_note}"}
    ]

    try:
        response = client.chat.completions.create(
            model=MAIN_MODEL,
            messages=messages,
            temperature=0.0,
            max_tokens=16
        )
        result = response.choices[0].message.content.strip()
        logger.info(f"Full note evaluation: [{result}] for note: {full_note}")
        return result
    except Exception as e:
        raise RuntimeError(f"Error evaluating full note with LLM: {e}") from e


def send_verify_answer(recheck: list[str]) -> str:
    """
    Wyślij odpowiedź do API.
    """
    payload = {
        "apikey": API_KEY,
        "task": TASK,
        "answer": {
            "recheck": recheck,
        }
    }
    try:
        response = requests.post(VERIFY_URL, json=payload, timeout=15)
        if response.status_code == 200:
            return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"Error sending verify answer: {e}"
    return response.text
