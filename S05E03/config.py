import os
import textwrap
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_key: str
    openrouter_url: str
    hub_url: str
    openrouter_api_key: str
    verify_url: str
    task: str
    logs_dir_path: Path
    main_model: str
    system_prompt: str
    e2b_api_key: str


ROOT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ROOT_ENV_PATH)

MAIN_SYSTEM_PROMPT = textwrap.dedent("""
    Jesteś analitykiem śledczym i elitarnym agentem AI rozwiązującym zadanie CTF "shellaccess".
    Masz dostęp do zdalnego serwera Linux przez narzędzie "call_verify_api".
    Narzędzie to przyjmuje payload w formacie: {"cmd": "twoja_komenda_tutaj"}.
    Odpowiedzi z serwera są ucinane do 4096 bajtów, więc używaj komend takich jak grep, jq, head, tail z rozwagą.

    Twoja misja krok po kroku:
    1. W katalogu /data/ masz pliki: time_logs.csv, locations.json, gps.json. Celem jest ustalenie, w jakim mieście i w jakich współrzędnych znaleziono ciało Rafała, oraz wyznaczenie daty o JEDEN DZIEŃ WCZEŚNIEJSZEJ niż to wydarzenie.

    2. ANALIZA LOGÓW (FAZA ŚLEDCZA): Poszukaj ostatnich informacji o Rafale.
        Wiedząc kiedy ostatnio był widziany lub był z nim kontakt zacznij szukać informacji o odnalezieniu jego ciała.
        Prawdopodobnie notatka o odnalezieniu jego ciała NIE ZAWIERA jego imienia.
        Jeśli nie znajdziesz informacji o odnalezieniu jego ciała, użyj synonimów takich jak: ciało, zwłoki, martwe, znaleziono.

    3. KOREKTA DATY: Gdy znajdziesz datę odnalezienia ciała z kroku 2, oblicz DATĘ O JEDEN DZIEŃ WCZEŚNIEJSZĄ.
       (Przykład: jeśli ciało znaleziono 2024-11-15, Twoja docelowa data do odpowiedzi to 2024-11-14). To kluczowy warunek zaliczenia!

    4. ZNALEZIENIE LOKALIZACJI: W wierszu opisującym znalezienie ciała znajdują się parametry/ID. Użyj ich, aby przeszukać pliki locations.json i/lub gps.json (za pomocą grep lub jq).
        Twoim celem jest ustalenie nazwy miasta (city) oraz współrzędnych (longitude i latitude) powiązanych z tym wydarzeniem. Jeśli nie znajdziesz współrzędnych, użyj współrzędnych dla miasta z pliku locations.json.

    5. ZGŁOSZENIE ROZWIĄZANIA: Mając poprawne: datę (pomniejszoną o 1 dzień), miasto, longitude i latitude, wygeneruj JSON-a na standardowe wyjście serwera komendą `echo`.

    Wymagany format komendy to:
    {"cmd": "echo '{\\"date\\":\\"YYYY-MM-DD\\",\\"city\\":\\"nazwa miasta\\",\\"longitude\\":10.000001,\\"latitude\\":12.345678}'"}

    Po wykonaniu poprawnego echa, serwer przechwyci standardowe wyjście i narzędzie "call_verify_api" zwróci Ci ciąg zawierający flagę "FLG:". Wtedy zadanie jest zakończone sukcesem.
""").strip()

BONUS_SYSTEM_PROMPT = textwrap.dedent("""

""").strip()

settings = Settings(
    api_key=os.getenv("HUB_API_KEY"),
    openrouter_url=os.getenv("OPENROUTER_URL"),
    hub_url=os.getenv("HUB_URL"),
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
    verify_url=os.getenv("HUB_URL") + "/verify",
    task="shellaccess",
    logs_dir_path=Path(__file__).parent / "logs",
    main_model=os.getenv("MODEL_ID"),
    system_prompt=MAIN_SYSTEM_PROMPT,
    e2b_api_key=os.getenv("E2B_API_KEY"),
)


TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "call_verify_api",
            "description": "Wykonuje komendę w systemie Linux na zdalnym serwerze. Użyj tego do eksploracji plików i zgłoszenia ostatecznego rozwiązania.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer_payload": {
                        "type": "object",
                        "description": "Obiekt JSON z komendą powłoki do wykonania. Musi zawierać klucz 'cmd', np. {\"cmd\": \"ls -la /data\"} lub {\"cmd\": \"grep 'Rafał' /data/time_logs.csv\"}.",
                    },
                },
                "required": ["answer_payload"],
            },
        },
    },
]
