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
            "description": "Wysyła payload do API centrali w celu zarządzania plikami lub weryfikacji zadania. Przekaż obiekt JSON lub listę akcji (batch mode), która ma trafić do klucza 'answer'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer_payload": {
                        "type": "object",
                        "description": "Może to być pojedynczy słownik z 'action' np. {'action': 'done'} lub LISTA słowników jeśli używasz batch_mode.",
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
