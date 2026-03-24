import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ROOT_ENV_PATH)

API_KEY = os.getenv("HUB_API_KEY")
BASE_URL = os.getenv("BASE_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

POWER_STATION_ID = "PWR6132PL"
DRONE_DATA = "https:///dane/drone.html"
VERIFY_URL = "https:///verify"
TASK = "drone"
DRONE_INSTRUCTIONS_PATH = Path(__file__).parent / "data" / "drone_instructions.md"
POWER_STATION_MAP_URL = f"https:///data/{API_KEY}/drone.png"

MAIN_MODEL = os.getenv("NANO_MODEL_ID")
VISION_MODEL = os.getenv("STRONG_MODEL_ID")

MAIN_SYSTEM_PROMPT = """
Jesteś operatorem drona bojowego.
Twoim celem jest zbombardowanie tamy (set(destroy)) w pobliżu elektrowni.
Sterujesz dronem używając API drona (tool: send_drone_instructions).
Używając narzędzia 'analyze_map_for_target' otrzymasz współrzędne tamy - nasz cel.
Poprzez user prompt otrzymasz:
- link do obrazu z mapą podzieloną na siatkę
- lokalizacja elektrowni (cel misji)
- dokumentacja API drona

Zasady działania:
1. Używasz narzędzia 'send_drone_instructions', podając listę komend (np. ["setDestinationObject(PWR6132PL)", "set(destroy)", "set(1,1)"]).
2. Po wysłaniu instrukcji dokładnie czytaj zwrócony komunikat błędu z API.
3. Jeśli API narzeka na brak określonego parametru (np. "silnik nie jest włączony"), znajdź odpowiednią funkcję w dokumentacji, dopisz ją do swojej listy komend i wyślij ponownie.
4. Działaj iteracyjnie - modyfikuj i rozszerzaj listę instrukcji na podstawie feedbacku.
5. Jeśli zablokujesz się w dziwnym błędzie stanu, pamiętaj, że na początku listy komend możesz użyć "hardReset".
6. Twoim zadaniem jest doprowadzić do momentu, w którym odpowiedź API zwróci {FLG: ...}.
"""

VISION_SYSTEM_PROMPT = """
Jesteś analitykiem obrazów satelitarnych.
Otrzymujesz mapę podzieloną na siatkę.
Oblicz dokładnie ile jest kolumn i wierszy.
Zlokalizuj sektor, w którym znajduje się tama (woda ma tam celowo podbity, bardzo intensywny kolor).
Zwróć wyłącznie numer kolumny i wiersza w formacie 'X,Y' (indeksowane od 1), np. lewy górny róg to "1,1".
"""

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "send_drone_instructions",
            "description": "Wywołuje API drona i zwraca wynik w formacie JSON.",
            "parameters": {
                "type": "object",
                "properties": {
                    "instructions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lista instrukcji do wykonania przez drona.",
                    },
                },
                "required": ["instructions"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_map_for_target",
            "description": "Użyj tego narzędzia na początku misji. Podaj URL mapy, a narzędzie przeanalizuje obraz i zwróci Ci precyzyjne współrzędne (X,Y) celu (tamy).",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                },
                "required": ["url"],
            },
        },
    },
]
