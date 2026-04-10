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
    frontend_system_prompt: str
    backend_system_prompt: str
    frontend_tools_schema: list
    backend_tools_schema: list
    e2b_api_key: str


ROOT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ROOT_ENV_PATH)

BACKEND_SYSTEM_PROMPT = textwrap.dedent("""
    Jesteś Nawigatorem Backendowym Maszyny Czasu. Pracujesz z Operatorem Frontendu.
    Twoim jedynym zadaniem jest konfigurowanie daty i parametrów bezpieczeństwa przez API maszyny (/verify).

    ZASADY KRYTYCZNE:
    0. ZAWSZE na samym początku przed konfiguracją nowego skoku poproś Frontenda (używając 'pass_control') o ustawienie UI w tryb 'standby' (payload: {"mode": "standby"}). Bez tego uderzenia po API zostaną zablokowane! Gdy Frontend to zrobi i odda Ci pałeczkę, przystąp do akcji.
    1. Parametry po API to tylko: day, month, year, syncRatio, stabilization.
    2. 'syncRatio' ZAWSZE obliczaj narzędziem 'calculate_sync_ratio'.
    3. Użyj narzędzia 'get_jump_requirements', aby poznać prawidłowe 'PWR' oraz 'internalMode' dla docelowego roku. NIE ZGADUJ wartości z tabeli na własną rękę!
    4. Aby ustawić 'stabilization', najpierw ustaw w API datę, potem zrób 'getConfig', odczytaj podpowiedź maszyny i prześlij ją w API.
    5. Gdy 5 parametrów zostanie ustawionych, użyj 'pass_control' i przekaż Frontendowi gotowy rozkaz do skoku:
       - Jak ustawić kierunek: Tunel = oba True, Przyszłość = tylko PTB, Przeszłość = tylko PTA.
       - Dokładną wartość PWR (z narzędzia get_jump_requirements).
       - Oczekiwany internalMode (z narzędzia get_jump_requirements).
""").strip()

FRONTEND_SYSTEM_PROMPT = textwrap.dedent("""
    Jesteś Operatorem Frontendowym Maszyny Czasu. Pracujesz w zespole z Nawigatorem Backendu.
    Twoim zadaniem jest operowanie suwakami i przyciskami panelu maszyny oraz wykonywanie fizycznych skoków w czasie.

    ZASADY:
    1. Twoje główne narzędzia to 'update_ui_state' oraz 'wait_and_click_sphere'.
    2. Jeśli Nawigator prosi o przejście w tryb 'standby', wywołaj 'update_ui_state' z payloadem {"mode": "standby"}. Następnie natychmiast użyj 'pass_control' podając target 'backend' z wiadomością, że jesteś w standby.
    3. Jeśli Nawigator każe wykonać skok i podaje parametry:
       - Użyj 'update_ui_state' z odpowiednim payloadem, np. {"PTA": true, "PTB": false, "PWR": 91}
       - Następnie użyj narzędzia 'wait_and_click_sphere' podając 'expected_internal_mode'. Narzędzie to samodzielnie poczeka na idealny moment by aktywować sferę!
       - Jeżeli narzędzie zwróci informacje o skoku lub flagę, przekaż ją dalej do Nawigatora ('backend') przez 'pass_control' pytając o dalsze kroki misji.
""").strip()

SHARED_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "pass_control",
            "description": "Przekazuje wykonanie zadania do drugiego agenta w zespole.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_agent": {"type": "string", "enum": ["frontend", "backend"], "description": "Do kogo przekazujesz zadanie"},
                    "message": {"type": "string", "description": "Szczegółowa instrukcja dla drugiego agenta"}
                },
                "required": ["target_agent", "message"]
            }
        }
    }
]

BACKEND_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "call_verify_api",
            "description": "Komunikacja API (backend). Oczekuje obiektu answer_payload: np. {'action': 'getConfig'} lub {'action': 'configure', 'param': 'year', 'value': 2238}.",
            "parameters": {"type": "object", "properties": {"answer_payload": {"type": "object"}}, "required": ["answer_payload"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_sync_ratio",
            "description": "Oblicza wskaźnik syncRatio wg wzoru.",
            "parameters": {"type": "object", "properties": {"day": {"type": "integer"}, "month": {"type": "integer"}, "year": {"type": "integer"}}, "required":["day", "month", "year"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_jump_requirements",
            "description": "Zwraca wymagany poziom PWR oraz internalMode dla danego roku.",
            "parameters": {"type": "object", "properties": {"year": {"type": "integer"}}, "required": ["year"]}
        }
    }
] + SHARED_TOOLS

FRONTEND_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "update_ui_state",
            "description": "Zmienia wartości na UI maszyny czasu. Payload przyjmuje klucze: 'mode', 'PTA', 'PTB', 'PWR'. Przykład: {'PTA': true, 'PTB': false, 'PWR': 50}",
            "parameters": {"type": "object", "properties": {"payload": {"type": "object"}}, "required": ["payload"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "wait_and_click_sphere",
            "description": "Wchodzi w tryb active, nasłuchuje UI maszyny, gdy internalMode się zrówna i fluxDensity osiągnie 100%, fizycznie aktywuje sferę skoku (jump).",
            "parameters": {"type": "object", "properties": {"expected_internal_mode": {"type": "integer", "description": "1, 2, 3 lub 4"}}, "required":["expected_internal_mode"]}
        }
    }
] + SHARED_TOOLS

settings = Settings(
    api_key=os.getenv("HUB_API_KEY"),
    openrouter_url=os.getenv("OPENROUTER_URL"),
    hub_url=os.getenv("HUB_URL"),
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
    verify_url=os.getenv("HUB_URL") + "/verify",
    task="timetravel",
    logs_dir_path=Path(__file__).parent / "logs",
    main_model=os.getenv("MODEL_ID"),
    frontend_system_prompt=FRONTEND_SYSTEM_PROMPT,
    backend_system_prompt=BACKEND_SYSTEM_PROMPT,
    frontend_tools_schema=FRONTEND_TOOLS_SCHEMA,
    backend_tools_schema=BACKEND_TOOLS_SCHEMA,
    e2b_api_key=os.getenv("E2B_API_KEY"),
)
