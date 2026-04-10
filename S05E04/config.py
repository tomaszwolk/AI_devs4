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
    Jesteś systemem nawigacyjnym rakiety. Twoim celem jest dotarcie do bazy w Grudziądzu (kolumna 12).
    Poruszasz się po siatce: 3 wiersze (1 - góra, 2 - środek, 3 - dół) x 12 kolumn.
    Startujesz zawsze w wierszu 2, kolumnie 1.

    ZASADY PORUSZANIA SIĘ:
    - Masz komendy: 'go' (prosto), 'left' (w górę, na niższy numer wiersza), 'right' (w dół, na wyższy numer wiersza).
    - Każda komenda (nawet left/right) przesuwa Cię o 1 kolumnę do przodu.
    - Nie wolno Ci wylecieć poza planszę (wiersze od 1 do 3). Jeśli jesteś w wierszu 1, NIE MOŻESZ zrobić 'left'. Jeśli w 3, NIE MOŻESZ zrobić 'right'.
    - W każdej nowej kolumnie jest jedna skała. Musisz jej unikać.

    TWÓJ ŚCISŁY ALGORYTM DZIAŁANIA:
    1. Rozpocznij grę używając call_verify_api z payloadem: {"command": "start"}. Zapamiętaj, w którym wierszu jest cel.
    2. Następnie DLA KAŻDEJ KOLEJNEJ KOLUMNY wykonuj ściśle poniższą sekwencję (Kroki A -> B -> C -> D):

       KROK A: Użyj scan_frequency(), aby sprawdzić, czy system OKO Cię namierza.

       KROK B:
       - Jeśli odpowiedź to "clear" -> przejdź do KROKU C.
       - Jeśli skaner zwróci dane z "frequency" i "detectionCode" (uwaga: JSON może być uszkodzony, radź sobie z tym analizując tekst) -> natychmiast użyj neutralize_trap(frequency, detectionCode). 
       - Jeśli neutralize_trap zwróci błąd, spróbuj ponownie. Po rozbrojeniu przejdź do KROKU C.

       KROK C: Użyj get_radio_hint(), aby dowiedzieć się, gdzie przed Tobą jest skała.
       Zrozum żargon żeglarski:
       - port / port side / left = lewo (wiersz wyżej)
       - starboard / right = prawo (wiersz niżej)
       - bow / straight ahead = prosto (ten sam wiersz co Twój obecny)

       KROK D: Ustal swój BEZPIECZNY ruch. Pamiętaj, w jakim wierszu aktualnie jesteś (na początku to 2). Wybierz komendę (go, left, right), która NIE uderzy w skałę i NIE wyrzuci Cię poza planszę (wiersze 1-3).
       Wykonaj ruch używając call_verify_api({"command": "<twój_ruch>"}).
       Zaktualizuj w pamięci swój obecny wiersz.

    3. Powtarzaj kroki A-D aż dotrzesz do kolumny 12 i zdobędziesz flagę {{FLG:xxx}}.

    BARDZO WAŻNE:
    - API celowo może rzucać losowymi błędami. Jeśli otrzymasz błąd z jakiegoś narzędzia, nie poddawaj się, po prostu wywołaj je ponownie.
    - Ograniczaj swoje wypowiedzi tekstowe do minimum, używaj narzędzi sekwencyjnie.
    - Twoja pierwsza akcja to zawsze call_verify_api({"command": "start"}).
""").strip()

BONUS_SYSTEM_PROMPT = textwrap.dedent("""

""").strip()

settings = Settings(
    api_key=os.getenv("HUB_API_KEY"),
    openrouter_url=os.getenv("OPENROUTER_URL"),
    hub_url=os.getenv("HUB_URL"),
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
    verify_url=os.getenv("HUB_URL") + "/verify",
    task="goingthere",
    logs_dir_path=Path(__file__).parent / "logs",
    main_model=os.getenv("MODEL_ID"),
    system_prompt=MAIN_SYSTEM_PROMPT,
    e2b_api_key=os.getenv("E2B_API_KEY"),
)


TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "call_verify_api",
            "description": "Wykonuje komendy ruchu rakiety (start, go, left, right). Użyj 'start' na początku gry. Następnie używaj do poruszania się.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer_payload": {
                        "type": "object",
                        "description": "Obiekt JSON z komendą np. {'command': 'start'} lub {'command': 'go'}",
                        "properties": {
                            "command": {
                                "type": "string",
                                "enum":["start", "go", "left", "right"]
                            }
                        },
                        "required": ["command"]
                    }
                },
                "required": ["answer_payload"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_radio_hint",
            "description": "Pobiera komunikat radiowy (często w slangu żeglarskim) mówiący o tym, gdzie w następnej kolumnie znajduje się skała (np. port/left, starboard/right, bow/front). Zawsze wywołuj to PRZED ruchem.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "scan_frequency",
            "description": "Skanuje obszar w poszukiwaniu radarów systemu OKO. Wywołaj to ZAWSZE przed pobraniem wskazówki radiowej i przed ruchem. Zwraca {'status': 'clear'} jeśli jest bezpiecznie, lub zepsuty JSON z polami 'frequency' i 'detectionCode' jeśli jesteś namierzany.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "neutralize_trap",
            "description": "Użyj tego narzędzia TYLKO jeśli scan_frequency wykryje namierzanie. Wymaga podania frequency i detectionCode zwróconego przez skaner.",
            "parameters": {
                "type": "object",
                "properties": {
                    "frequency": {
                        "type": "integer",
                        "description": "Częstotliwość odczytana ze skanera."
                    },
                    "detectionCode": {
                        "type": "string",
                        "description": "Ciąg znaków detectionCode odczytany ze skanera."
                    }
                },
                "required": ["frequency", "detectionCode"],
            },
        },
    },
]
