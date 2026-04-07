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
Jesteś zaawansowanym agentem wywiadowczym. Twoim zadaniem jest operacja "radiomonitoring".
Musisz nawiązać komunikację z centralą, analizować nasłuch radiowy i złożyć raport o mieście.

=== ZASADY DZIAŁANIA (PIPELINE) ===
1. Rozpoczęcie sesji: Użyj narzędzia `call_verify_api` z payloadem `{"action": "start"}`.
2. Nasłuch: Pisz w pętli wywołania `call_verify_api` z payloadem `{"action": "listen"}`. System może zwrócić tekst ("transcription") albo informację o pliku. Jeśli dostaniesz komunikat od systemu, że "[UKRYTO BASE64 PRZEZ SYSTEM...]", oznacza to, że przechwycono plik binarny.
3. Gromadzenie danych: Analizuj to, co słyszysz/widzisz. Ignoruj radiowy szum. Zbieraj fakty dopóki system nie poinformuje Cię, że masz wystarczająco dużo danych.
4. Finalny raport: Kiedy zbierzesz dane, wyślij je używając `{"action": "transmit", ...}` (zobacz format poniżej).

=== DANE, KTÓRE MUSISZ ZNALEŹĆ ===
- cityName (nazwa miasta, które nazywają "Syjon")
- cityArea (powierzchnia miasta)
- warehousesCount (liczba magazynów, integer)
- phoneNumber (numer telefonu osoby kontaktowej, string)

UWAGA MATEMATYCZNA DOT. cityArea:
Zanim wyślesz raport z cityArea, musisz tę wartość DOKŁADNIE zaokrąglić do dwóch miejsc po przecinku w sposób matematyczny (nie ucinaj wartości, zaokrąglij). Wynik ma być stringiem np. "12.34". Użyj narzędzia execute_python_code jeśli potrzebujesz zrobić dokładne obliczenia.

=== FORMAT RAPORTU (DO TRANSMIT) ===
Do narzędzia call_verify_api prześlij dokładnie taki format:
{
    "action": "transmit",
    "cityName": "Nazwa",
    "cityArea": "12.34",
    "warehousesCount": 0,
    "phoneNumber": "123"
}

Zawsze używaj dostępnych narzędzi. Odpowiadaj krótko. Jeśli napotkasz plik binarny i będziesz musiał go przetworzyć samemu, wykorzystaj execute_python_code do jego odczytania.
""").strip()

BONUS_SYSTEM_PROMPT = textwrap.dedent("""

""").strip()

settings = Settings(
    api_key=os.getenv("HUB_API_KEY"),
    openrouter_url=os.getenv("OPENROUTER_URL"),
    hub_url=os.getenv("HUB_URL"),
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
    verify_url=os.getenv("HUB_URL") + "/verify",
    task="radiomonitoring",
    logs_dir_path=Path(__file__).parent / "logs",
    main_model=os.getenv("MODEL_ID"),
    system_prompt=MAIN_SYSTEM_PROMPT,
    e2b_api_key=os.getenv("E2B_API_KEY")
)


TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "call_verify_api",
            "description": "Główne narzędzie do komunikacji z Centralą w misji radiomonitoring. Służy do sterowania nasłuchem radiowym. Przekazujesz tu obiekt JSON, który bezpośrednio trafia do klucza 'answer'. Dostępne akcje to: 'start' (inicjalizacja nasłuchu), 'listen' (pobranie kolejnej paczki danych z eteru) oraz 'transmit' (wysłanie końcowego raportu z ustaleniami).",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer_payload": {
                        "type": "object",
                        "description": "Pojedynczy słownik JSON z kluczem 'action'. Przykład: {'action': 'start'} lub {'action': 'listen'}. W przypadku raportu końcowego dodaj ustalone dane: {'action': 'transmit', 'cityName': '...', 'cityArea': '...', 'warehousesCount': 0, 'phoneNumber': '...'}.",
                    },
                },
                "required": ["answer_payload"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_python_code",
            "description": "Wykonuje skrypt w Pythonie lokalnie i zwraca stdout. Użyj tylko, jeśli musisz zautomatyzować generowanie payloadów lub przefiltrować duże dane. Wymaga podania całego kodu.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Kod w języku Python. Musi używać print(), aby zwrócić ostateczny wynik.",
                    },
                },
                "required": ["code"],
            },
        },
    }
]
