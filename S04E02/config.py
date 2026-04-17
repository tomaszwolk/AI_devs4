import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_key: str | None
    openrouter_url: str | None
    hub_url: str | None
    openrouter_api_key: str | None
    verify_url: str | None
    task: str
    logs_dir_path: Path
    main_model: str | None
    main_system_prompt: str


ROOT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ROOT_ENV_PATH)

MAIN_SYSTEM_PROMPT = (
    """Jesteś agentem AI. Ratujesz elektrownię konfigurując turbinę wiatrową.
    MASZ KRYTYCZNY LIMIT CZASU: 40 SEKUND! Odpowiadaj BŁYSKAWICZNIE. Zero tekstu opisowego. Zawsze używaj Parallel Tool Calling.

    === KRYTYCZNE ZASADY ===
    1. POGODA JEST DYNAMICZNA: Pogoda generuje się od nowa przy każdym `start`. Jeśli dostaniesz "Service window timeout exceeded" lub "signature mismatch", MUSISZ rozpocząć nową sesję (`start`), PONOWNIE pobrać pogodę i ZAPOMNIEĆ daty z poprzedniej sesji!
    2. WICHURY (windMs >= 14): Niszczą turbinę (Zwykle ok. 3 momentów). Ustaw: pitchAngle: 90, turbineMode: "idle".
    3. PRODUKCJA PRĄDU: Turbina potrzebuje minimum 4.0 m/s! Wybierz 1 punkt >= 4.0 m/s. Ustaw: pitchAngle: 0, turbineMode: "production".

    === STRUKTURY DANYCH (SZABLON) ===
    Akcja unlockCodeGenerator (wywołuj dla każdego punktu osobno):
    {"action": "unlockCodeGenerator", "startDate": "YYYY-MM-DD", "startHour": "HH:00:00", "windMs": 25.0, "pitchAngle": 90}

    Akcja config (wszystkie kody w jednym):
    {"action": "config", "configs": {"2026-04-01 18:00:00": {"pitchAngle": 90, "turbineMode": "idle", "unlockCode": "hash"}, "2026-04-03 20:00:00": {"pitchAngle": 0, "turbineMode": "production", "unlockCode": "hash"}}}

    === ŚCISŁY ALGORYTM KROK PO KROKU ===

    KROK 1: Wywołaj RÓWNOLEGLE 2 narzędzia: `start` oraz `get` (param: "weather").
    KROK 2: Wywołaj narzędzie `getResult` (pobranie pogody z kolejki).
    KROK 3: Wywołaj RÓWNOLEGLE `unlockCodeGenerator` dla WSZYSTKICH punktów z pogody naraz (np. 3 wichury i 1 produkcja = 4 wywołania w jednym kroku!).
    KROK 4: Wywołaj RÓWNOLEGLE `getResult` tyle razy, ile generujesz kodów (aby odebrać je wszystkie naraz).
    KROK 5: Wywołaj RÓWNOLEGLE 2 narzędzia (kompresja czasu):
            - Wyślij przygotowany `config`
            - Wyślij `get` z parametrem `turbinecheck`
    KROK 6: Wywołaj RÓWNOLEGLE 2 narzędzia (muszą być w tej kolejności w JSONie tool_calls):
            - `getResult` (aby odebrać wynik testu)
            - `done` (aby zakończyć i odebrać flagę)
"""
).strip()

settings = Settings(
    api_key=os.getenv("HUB_API_KEY"),
    openrouter_url=os.getenv("OPENROUTER_URL"),
    hub_url=os.getenv("HUB_URL"),
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
    verify_url=(
        f"{hub_url}/verify" if (hub_url := os.getenv("HUB_URL")) is not None else None
    ),
    task="windpower",
    logs_dir_path=Path(__file__).parent / "logs",
    main_model=os.getenv("SONNET_MODEL_ID"),
    main_system_prompt=MAIN_SYSTEM_PROMPT,
)


TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "call_verify_api",
            "description": "Wysyła payload do API centrali. Przekaż cały obiekt JSON, który ma trafić do klucza 'answer'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer_payload": {
                        "type": "object",
                        "description": "Pełny słownik parametrów dla klucza answer, np. {'action': 'start'} albo {'action': 'get', 'param': 'weather'}",
                    },
                },
                "required": ["answer_payload"],
            },
        },
    },
]


# KROK 6: TEST TURBINY PRZED ZAKOŃCZENIEM
# - Wywołaj `{"action": "get", "param": "turbinecheck"}`.
# - Następnie wywołaj `{"action": "getResult"}`, aby odebrać wynik testu.

# KROK 7: ZAKOŃCZENIE
# Po poprawnym turbinecheck, wywołaj `{"action": "done"}`. To zwróci flagę {{FLG:XXX}}.
