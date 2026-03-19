import requests
import tiktoken
from config import (
    LOGS_URL, VERIFY_URL, API_KEY, TASK, COMPRESSOR_MODEL,
    LOGS_PATH, COMPRESSOR_SYSTEM_PROMPT
)
from openai import OpenAI
import os
import json
import re


def download_logs() -> str:
    """
    Pobiera plik logów z serwera i zapisuje lokalnie jako 'logs.txt'.
    Zwraca komunikat o sukcesie lub błędzie.
    """
    # 1. Wykonaj GET na LOGS_URL
    response = requests.get(LOGS_URL)
    # 2. Zapisz zawartość do pliku "logs.txt"
    with open(LOGS_PATH, "w") as f:
        f.write(response.text)
    # 3. Policz ile linii ma plik (dla informacji agenta)
    lines = len(response.text.splitlines())
    return f"Logi pobrane pomyślnie. Zapisano {lines} linii do {LOGS_PATH}"


def search_logs(keywords: list[str] = None, levels: list[str] = None) -> str:
    """
    Przeszukuje lokalny plik 'logs.txt'.
    Przyjmuje listę słów kluczowych (np. ['PWR01', 'VALVE']) 
    oraz/lub poziomów (np.['CRIT', 'WARN']).
    Zwraca surowe linie logów pasujące do kryteriów.
    """
    keywords = keywords or []
    levels = levels or []

    # 1. Otwórz "logs.txt"
    try:
        with open(LOGS_PATH, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return "Plik logs.txt nie znaleziony.\
        Użyj narzędzia 'download_logs' aby go pobrać."

    # 2. Przejdź pętlą linia po linii.
    #   Jeśli linia zawiera którykolwiek element z `levels` LUB `keywords`:
    #    - Dodaj do listy znalezionych wyników
    results = []
    for line in lines:
        if any(level in line for level in levels) or any(keyword in line for keyword in keywords):
            results.append(line.strip())

    # 3. Złączenie wstępnych wyników i użycie filtra
    raw_results_str = "\n".join(results)
    filtered_logs = filter_unique_logs(raw_results_str)

    # 5. Zwróć tekst jako połączone linie stringów.
    return filtered_logs


def compress_logs(raw_logs: str) -> str:
    """
    Narzędzie do kompresji. Przyjmuje surowe logi i używa tańszego modelu LLM,
    aby skrócić je do niezbędnego formatu (Data Czas Poziom Komponent - krótki opis).
    """
    # 0. Dla pewności filtrujemy duplikaty
    filtered_logs = filter_unique_logs(raw_logs)
    # 1. Stwórz prompt systemowy z wytycznymi z zadania:
    #    - "Oto logi. Skompresuj je. Zostaw tylko datę (YYYY-MM-DD), czas (HH:MM),
    #       poziom błędu, id komponentu i max 3-4 słowa opisu."
    #    - "Zachowaj format jedno zdarzenie = jedna linia."
    # 2. Wyślij zapytanie do OpenAI.
    client = OpenAI(
        base_url=os.getenv("BASE_URL"),
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

    messages = [
        {"role": "system", "content": COMPRESSOR_SYSTEM_PROMPT},
        {"role": "user", "content": filtered_logs}
    ]

    response = client.chat.completions.create(
        model=COMPRESSOR_MODEL,
        messages=messages,
        temperature=0.1
    )
    # 3. Zwróć wygenerowany, skompresowany tekst.
    return response.choices[0].message.content


def count_tokens(text: str) -> int:
    """Zwraca liczbę tokenów w tekście na podstawie encodera OpenAI."""
    # 1. Zainicjalizuj tiktoken.encoding_for_model("")
    try:
        encoding = tiktoken.encoding_for_model("gpt-5")
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    # 2. Policz tokeny i zwróć ich ilość
    return len(encoding.encode(text))


def create_payload(logs: str) -> dict:
    """
    Create a payload.
    """
    payload = {
        "apikey": API_KEY,
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


def submit_logs(logs: str) -> str:
    """
    Wysyła skompresowane logi do Centrali w celu weryfikacji.
    Zwraca dokładny feedback od techników (JSON) lub flagę.
    """
    # 1. Zbuduj payload: {"apikey": API_KEY, "task": "failure", "answer": {"logs": compressed_logs}}
    payload = create_payload(logs)
    # 2. Wykonaj POST na VERIFY_URL
    status_code, response = send_payload(payload)
    # 3. Pobierz odpowiedź JSON i zwróć ją jako string, by Agent ją przeczytał.
    return json.dumps(response)


def filter_unique_logs(logs: str) -> str:
    # Zbiór na fragmenty komunikatów, które już widzieliśmy
    seen_messages = set()
    unique_logs = []
    # Regex: [data] [level] reszta_komunikatu
    # Grupa (.*) wyłapie wszystko po "[LEVEL] "
    log_pattern = re.compile(r'\[.*?\] \[(?:.*?)\] (.*)')

    for line in logs.splitlines():
        match = log_pattern.search(line)
        if match:
            # Wyciągamy sam komunikat (np. "ECCS8 reported runaway...")
            message_content = match.group(1).strip()

            # Jeśli jeszcze tego komunikatu nie widzieliśmy
            if message_content not in seen_messages:
                seen_messages.add(message_content)
                unique_logs.append(line)

    return "\n".join(unique_logs)


TOOLS_DICT = {
    "download_logs": download_logs,
    "search_logs": search_logs,
    "compress_logs": compress_logs,
    "count_tokens": count_tokens,
    "submit_logs": submit_logs,
}
