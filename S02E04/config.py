import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ROOT_ENV_PATH)

API_KEY = os.getenv("HUB_API_KEY")
BASE_URL = os.getenv("BASE_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MAIL_URL = "https:///api/zmail"
VERIFY_URL = "https:///verify"
TASK = "mailbox"

MAIN_MODEL = os.getenv("VISION_MODEL_ID")

MAIN_SYSTEM_PROMPT = """
Jesteś autonomicznym badaczem cyberbezpieczeństwa. Twoim zadaniem jest przeszukanie skrzynki pocztowej operatora w celu znalezienia trzech informacji:
1. date - data ataku na elektrownię (format YYYY-MM-DD)
2. password - hasło do systemu pracowniczego
3. confirmation_code - kod potwierdzenia (format: SEC- + 28 znaków)

ZASADY DZIAŁANIA:
1. Użytkownik dostarczy Ci instrukcję help. zawierającą obsługiwane komendy API zmail, które możesz wywołać używając narzędzia 'call_zmail_api'.
2. Wiemy, że donosiciel Wiktor (nie znamy jego nazwiska) wysłał maila z domeny 'proton.me'. Przeszukaj skrzynkę używając API by znaleźć wszytkie 3 informacje.
3. API zwraca maile w dwóch krokach. Najpierw wyszukuj (poznasz ID), a potem pobieraj pełną treść używając odpowiedniej akcji i ID. Nigdy nie zgaduj treści po samym temacie.
4. Skrzynka jest aktywna. Jeśli czegoś nie ma, nowe maile mogą właśnie przychodzić. Spróbuj odczekać chwilę i sprawdzić ponownie.
5. Zbieraj informacje krok po kroku. Jeśli znajdziesz choćby jedną poszlakę, użyj jej do kolejnych wyszukiwań.
6. API działa jak wyszukiwarka Gmail. Obsługuje operatory: from:, to:,subject:, OR, AND.
7. Gdy uważasz, że masz dane, wywołaj 'verify_answer' z danymi date, password i confirmation_code. Jeśli system zwróci błąd, przeanalizuj go i szukaj dalej. Jeśli system zwróci flagę - zakończ zadanie.
"""

BONUS_SYSTEM_PROMPT = """
Przeszukaj całą zawartość skrzynki (używaj getInbox i czytaj wszystkie maile po kolei).
Szukasz maila, który jest zapisany szyfrem. Zwróć szczególną uwagę na maile o dziwnych tytułach.
Jeśli znajdziesz zaszyfrowany tekst, użyj szyfru harcerskiego GA-DE-RY-PO-LU-KI, aby odczytać zawartość i znaleźć bonusową flagę w formacie FLG{...}.
"""
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "call_zmail_api",
            "description": "Wywołuje API zmail i zwraca wynik w formacie JSON. Parametry są opisane w help.json.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "page": {"type": "integer"},
                    "perPage": {"type": "integer"},
                    "threadID": {"type": "integer"},
                    "ids": {"type": "string"},
                    "query": {"type": "string"},
                },
                "required": ["action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "verify_answer",
            "description": "Wywołuje API verify i zwraca wynik w formacie JSON.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string"},
                    "password": {"type": "string"},
                    "confirmation_code": {"type": "string"}
                },
                "required": ["date", "password", "confirmation_code"],
            },
        },
    }
]
