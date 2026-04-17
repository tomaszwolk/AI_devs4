import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ROOT_ENV_PATH)

API_KEY = os.getenv("HUB_API_KEY")
OPENROUTER_URL = os.getenv("OPENROUTER_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

HUB_URL = os.getenv("HUB_URL")
VERIFY_URL = f"{HUB_URL}/verify" if HUB_URL else None
TASK = "negotiations"
LOGS_DIR_PATH = Path(__file__).parent / "logs"

MAIN_MODEL = os.getenv("MINI_MODEL_ID")

CITIES_PATH = Path(__file__).parent / "data" / "cities.csv"
CONNECTIONS_PATH = Path(__file__).parent / "data" / "connections.csv"
ITEMS_PATH = Path(__file__).parent / "data" / "items.csv"

# URL from pinggy
MY_TOOL_URL = "https://ziuao-194-4-61-117.a.free.pinggy.link/api/search"

MAIN_SYSTEM_PROMPT = (
    """
Jesteś precyzyjnym asystentem.
Użytkownik przekaże Ci opis przedmitu, a Twoim zadaniem jest dopasować go do
DOKŁADNIE JEDNEJ nazwy z poniższej bazy.
Zwróć TYLKO DOKŁADNĄ NAZWĘ, bez znaków interpunkcyjnych i dodatkowych słów.
Baza przedmiotów: {all_items_str}
"""
).strip()

TOOLS_SCHEMA = []
