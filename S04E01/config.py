import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ROOT_ENV_PATH)

API_KEY = os.getenv("HUB_API_KEY")
OPENROUTER_URL = os.getenv("OPENROUTER_URL")
HUB_URL = os.getenv("HUB_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

VERIFY_URL = HUB_URL + "/verify"
OKO_URL = os.getenv("OKO_URL")
TASK = "okoeditor"
LOGS_DIR_PATH = Path(__file__).parent / "logs"

MAIN_MODEL = os.getenv("MODEL_ID")

MAIN_SYSTEM_PROMPT = ("""
    Jesteś zaawansowanym asystentem AI ds. cyberbezpieczeństwa i operacji w systemie OKO.
    Twoim celem jest wykonanie precyzyjnych aktualizacji bazy danych za pomocą dostępnego narzędzia (API).
    Naszym nadrzędnym celem jest uratowanie miasta Skolwin przed atakiem, poprzez zmianę klasyfikacji zagrożeń,
    oraz odwrócenie uwagi operatorów na niezamieszkane miasto Komarowo.

    ZASADY KORZYSTANIA Z API (call_oko_editor_api):
    - Akcja "update": wymaga pól 'page' (incydenty|notatki|zadania), 'record_id' oraz co najmniej 'content' lub 'title'.
    - Pole 'is_done' (YES/NO) jest dozwolone TYLKO dla tabeli 'zadania'.
    - Akcja "done": używana bez dodatkowych argumentów na samym końcu, by sprawdzić, czy warunki zadania zostały spełnione (zwraca flagę).

    ZASADY KODOWANIA INCYDENTÓW:
    Kody zawsze wpisujemy NA SAMYM POCZĄTKU tytułu incydentu (np. "MOVE01 Wykryto ruch...").
    Pierwsze cztery znaki to typ, a dwa ostatnie to podtyp.
    - RECO (rekonesans): 01 (broń), 02 (prowiant), 03 (pojazd), 04 (inne).
    - PROB (badanie próbki): 01 (radiowa), 02 (internetowa), 03 (fizyczny nośnik).
    - MOVE (wykryto ruch): 01 (człowiek), 02 (pojazd), 03 (pojazd + człowiek), 04 (zwierzęta).
""").strip()

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "call_oko_editor_api",
            "description": "Wysyła zapytanie do API edytora OKO. Pozwala na aktualizację danych ('update') lub zakończenie zadania ('done').",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["update", "done"],
                        "description": "Akcja do wykonania. 'update' aby zaktualizować wpis, 'done' aby sprawdzić flagę."
                    },
                    "page": {
                        "type": "string",
                        "enum": ["incydenty", "notatki", "zadania"],
                        "description": "Tabela, w której dokonujemy zmiany (tylko dla akcji 'update')."
                    },
                    "record_id": {
                        "type": "string",
                        "description": "32-znakowy identyfikator hex wpisu (tylko dla akcji 'update')."
                    },
                    "content": {
                        "type": "string",
                        "description": "Nowa treść wpisu."
                    },
                    "title": {
                        "type": "string",
                        "description": "Nowy tytuł wpisu (jeśli wymagany)."
                    },
                    "is_done": {
                        "type": "string",
                        "enum": ["YES", "NO"],
                        "description": "Oznaczenie zadania jako wykonane (używaj tylko dla page='zadania')."
                    }
                },
                "required": ["action"]
            }
        }
    }
]
