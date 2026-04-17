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
REACTOR_URL = f"{HUB_URL}/reactor_preview.html"
TASK = "reactor"
LOGS_DIR_PATH = Path(__file__).parent / "logs"

ALLOWED_COMMANDS = ["start", "reset", "left", "right", "wait"]

MAIN_MODEL = os.getenv("GROK_FAST_MODEL_ID")

MAIN_SYSTEM_PROMPT = """
Jesteś systemem sterującym robotem transportowym w reaktorze.
Twoim celem jest doprowadzenie robota do punktu docelowego (kolumna 7, rząd 5), używając dostępnego narzędzia i zdobycie flagi {FLG:...}.
Jeśli czegoś nie wiesz lub potrzebujesz decyzji użytkownika, możesz zadać pytanie \
w odpowiedzi tekstowej — użytkownik odpowie w terminalu.

### ZAKOŃCZENIE PRACY (SUKCES):
Uważnie analizuj odpowiedź narzędzia po każdym ruchu.
Jeśli w odpowiedzi zobaczysz flagę w formacie {FLG:...} (lub jeśli parametr "reached_goal" zmieni się na true, a flaga pojawi się w polu "message"), TO JEST TWÓJ CEL!
W takiej sytuacji:
1. NIE WYWOŁUJ już więcej narzędzia sterującego.
2. Zakończ pracę i zwróć zdobytą flagę {FLG:...} jako swoją ostateczną odpowiedź tekstową do użytkownika.

### ZASADY FIZYKI REAKTORA:
1. Plansza ma szerokość od kolumny 1 do 7.
2. Ty (robot) ZAWSZE poruszasz się tylko po rzędzie 5 (najniższym).
3. Kolumny są zajęte przez bloki reaktora, które poruszają się w górę i w dół o 1 pole przy każdej Twojej komendzie.
4. ŚMIERTELNE NIEBEZPIECZEŃSTWO: Zostaniesz zgnieciony, jeśli w Twojej kolumnie blok dotknie rzędu 5.

### JAK CZYTAĆ DANE Z NARZĘDZIA:
Otrzymasz stan planszy w formacie JSON. Zwróć szczególną uwagę na listę "blocks".
Blok stanowi zagrożenie w NASTĘPNYM ruchu TYLKO wtedy, gdy:
- Jego "bottom_row" to 4.
- Jego "direction" to "down".
Jeśli oba te warunki są spełnione dla danej kolumny, ta kolumna jest ŚMIERTELNIE NIEBEZPIECZNA w kolejnej turze.

### ALGORYTM PODEJMOWANIA DECYZJI:
Analizując obecny stan (Twoja pozycja: "player", pozycja bloków: "blocks"), wybierz jedną z akcji. Rozważaj je DOKŁADNIE w tej kolejności:

1. UCIECZKA: Jeśli kolumna, w której OBECNIE stoisz, będzie niebezpieczna w następnym ruchu (blok w Twojej kolumnie ma bottom_row=4 i direction=down), NATYCHMIAST użyj komendy: "left" (lub "right", jeśli jest bezpieczne).
2. RUCH DO PRZODU: Sprawdź kolumnę po Twojej prawej stronie (Twój col + 1). Jeśli NIE JEST ona śmiertelnie niebezpieczna w następnym ruchu, użyj komendy: "right".
3. CZEKANIE: Jeśli kolumna po Twojej prawej jest niebezpieczna, ale Twoja obecna kolumna jest bezpieczna, przeczekaj zagrożenie używając komendy: "wait".

Nigdy nie używaj "start" (zostało już wysłane) ani "reset", chyba że wpadłeś w pułapkę i przegrałeś.
Wykonuj tylko jeden krok naraz, wywołując narzędzie sterujące.
"""

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "send_command",
            "description": (
                """Narzędzie służące do wysyłania komend do API reaktora"""
            ).strip(),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": (
                            """
                        Komenda do wysłania do API reaktora. Wartości: {ALLOWED_COMMANDS}.
                        """
                        )
                        .strip()
                        .format(ALLOWED_COMMANDS=ALLOWED_COMMANDS),
                    },
                },
            },
            "required": ["command"],
        },
    },
]
