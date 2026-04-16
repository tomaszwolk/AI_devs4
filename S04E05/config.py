import os
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
    main_system_prompt: str
    e2b_api_key: str


ROOT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ROOT_ENV_PATH)

SYSTEM_PROMPT = ("""
Jesteś rygorystycznym systemem logistycznym. Twoim zadaniem jest zrealizowanie zamówień dla miast z pliku food4cities.json i zdobycie flagi.
Cała komunikacja z API odbywa się WYŁĄCZNIE poprzez 'call_verify_api' i parametr 'answer_payload'.

ZASADY:
1. ZAKAZ UŻYWANIA PYTHON DO HASHOWANIA. Sygnatury pobieraj TYLKO za pomocą: {"tool": "signatureGenerator", "action": "generate", "login": "...", "birthday": "...", "destination": <ID>}.
2. Pamiętaj, że baza SQLite obcina wyniki. Jeśli potrzebujesz kolejnych wyników, używaj LIMIT i OFFSET (np. LIMIT 30 OFFSET 30).
3. ZAWSZE na samym początku wykonaj {"tool": "reset"}, aby usunąć wszelkie "resztki" z poprzednich prób.

PROCEDURA KROK PO KROKU:

KROK 1: Wyślij {"tool": "reset"}, aby wyczyścić stan bazy do zera. To krytyczne!

KROK 2: Ustalenie ID miast.
- Wyślij: {"tool": "database", "query": "SELECT * FROM destinations LIMIT 30"}
- Wyślij: {"tool": "database", "query": "SELECT * FROM destinations LIMIT 30 OFFSET 30"}
Zapisz w pamięci, jakie destination_id ma np. Domatowo i pozostałe miasta.

KROK 3: Ustalenie właściwego użytkownika.
Użytkownik musi mieć rolę odpowiedzialną za "transport".
- Wyślij: {"tool": "database", "query": "SELECT * FROM roles"}. Zobacz, jakie 'id' ma rola transportowa.
- Wyślij: {"tool": "database", "query": "SELECT * FROM users WHERE role = <id_roli_transportowej> LIMIT 10"}. 
Wybierz JEDNEGO użytkownika z tej listy. Zanotuj jego 'user_id' (to Twoje 'creatorID'), 'login' oraz 'birthday'.

KROK 4: Składanie zamówień (Dla KAŻDEGO z 8 miast w food4cities.json z osobna):
A) Pobierz sygnaturę wysyłając: {"tool": "signatureGenerator", "action": "generate", "login": "<wybrany_login>", "birthday": "<wybrana_data>", "destination": <destination_id_miasta>}
B) Utwórz zamówienie wysyłając: {"tool": "orders", "action": "create", "title": "Dostawa dla <nazwa_miasta>", "creatorID": <wybrany_user_id>, "destination": <destination_id_miasta>, "signature": "<otrzymany_podpis>"}
C) Odczytaj z odpowiedzi ID nowo utworzonego zamówienia.
D) Dodaj towary (batch mode) wysyłając: {"tool": "orders", "action": "append", "id": "<id_zamowienia_z_kroku_B>", "items": {<JSON_zapotrzebowania_z_food4cities>}}

KROK 5: Po wykonaniu punktu 4 dla wszystkich miast (gdy jesteś absolutnie pewien, że nie ma błędnych zamówień z poprzednich prób), wyślij: {"tool": "done"}.
""").strip()

BONUS_SYSTEM_PROMPT = ("""

""").strip()

settings = Settings(
    api_key=os.getenv("HUB_API_KEY"),
    openrouter_url=os.getenv("OPENROUTER_URL"),
    hub_url=os.getenv("HUB_URL"),
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
    verify_url=os.getenv("HUB_URL") + "/verify",
    task="foodwarehouse",
    logs_dir_path=Path(__file__).parent / "logs",
    main_model=os.getenv("MODEL_ID"),
    main_system_prompt=SYSTEM_PROMPT,
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
