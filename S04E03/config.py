import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


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
    e2b_api_key: str | None
    bonus_system_prompt: str


ROOT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ROOT_ENV_PATH)

MAIN_SYSTEM_PROMPT = (
    """
    Jesteś elitarnym dowódcą misji ratunkowej w zrujnowanym mieście Domatowo.
    Twoim celem jest odnalezienie rannego partyzanta i ewakuowanie go helikopterem.

    Z przechwyconego komunikatu wiemy: "Ukryłem się w jednym z najwyższych bloków."
    Z analizy mapy wynika, że są to kafelki typu "block3" (symbol B3).

    ZASADY I MECHANIKA:
    1. Komunikujesz się z serwerem używając narzędzia `call_verify_api`. Przekazujesz tam obiekt JSON (payload), który trafi pod klucz "answer".
    2. Mapa to siatka 11x11. Kolumny to A-K, wiersze to 1-11. Lewy górny róg to A1, prawy dolny to K11.
    3. Masz maksymalnie 300 Punktów Akcji (AP). Oszczędzaj je!
       - Utworzenie transportera: 5 AP + 5 AP za każdego zwiadowcę (max 4 na pojazd).
       - Utworzenie zwiadowcy (scout): 5 AP.
       - Ruch transportera: 1 AP za pole (wyłącznie po drogach "road").
       - Ruch zwiadowcy: 7 AP za pole (bardzo drogo, używaj ich tylko na krótkich dystansach!).
       - Inspekcja (inspect): 1 AP.
    4. Gra AUTOMATYCZNIE oblicza ścieżkę przy akcji "move". Podajesz tylko cel `where`.
    5. Transportery respawnują się na polach A6, B6, C6, D6 (w tej kolejności).

    LOKALIZACJE CELÓW (Bloki B3):
    Kluczowe skupiska bloków B3 na mapie to:
    - KLASTER 1 (Północ): F1, G1, F2, G2. Najbliższa ulica dla transportera to D2 lub D1.
    - KLASTER 2 (Południowy Zachód): A10, B10, C10, A11, B11, C11. Najbliższa ulica to B9, C9 lub D9.
    - KLASTER 3 (Południowy Wschód): H10, I10, H11, I11. Najbliższa ulica to H9 lub I9.

    TWOJA PROCEDURA DZIAŁANIA (Krok po kroku):
    KROK 1. Wyślij {"action": "reset"}, aby upewnić się, że plansza i AP są zresetowane.
    KROK 2. Stwórz transporter z maksymalną załogą: {"action": "create", "type": "transporter", "passengers": 4}. Zapisz jego hash!
    KROK 3. Przemieść transporter w pobliże KLASTRA 1 (np. D2): {"action": "move", "object": "HASH_TRANSPORTERA", "where": "D2"}.
    KROK 4. Wysadź zwiadowców: {"action": "dismount", "object": "HASH_TRANSPORTERA", "passengers": 4}.
    KROK 5. Pobierz listę obiektów: {"action": "getObjects"}. Zidentyfikuj hashe zwiadowców i ich nowe pozycje wokół transportera.
    KROK 6. Wydaj każdemu zwiadowcy polecenie ruchu na jedno z pól KLASTRA 1 (F1, G1, F2, G2).
    KROK 7. Po dojściu zwiadowcy, wykonaj inspekcję: {"action": "inspect", "object": "HASH_ZWIADOWCY"}.
    KROK 8. Po inspekcjach pobierz logi: {"action": "getLogs"}. Przeanalizuj czy w logach zwiadowca informuje o znalezieniu człowieka!
    KROK 9. Jeśli log potwierdza znalezienie człowieka na danym polu (np. G1), wezwij ewakuację! {"action": "callHelicopter", "destination": "G1"}. To da Ci flagę.
    KROK 10. Jeśli człowieka nie było w KLASTRZE 1, stwórz KOLEJNY transporter (zrespi się na B6), pojedź do KLASTRA 2 (np. na pole C9), wysadź zwiadowców, zbadaj bloki w KLASTRZE 2. Powtarzaj aż znajdziesz cel.

    Działaj metodycznie. Sprawdzaj odpowiedzi API. Wykonuj akcje po kolei i na bieżąco analizuj `getObjects` i `getLogs`.
"""
).strip()

BONUS_SYSTEM_PROMPT = (
    """
    Jesteś elitarnym dowódcą misji specjalnej w zrujnowanym mieście Domatowo.
    Tym razem realizujemy ukryty cel poboczny: "Take Me to Church".
    Twoim zadaniem jest dotarcie do kościoła, dokładne przeszukanie go, odczytanie logów i BEZWZGLĘDNE ZATRZYMANIE SIĘ, aby poczekać na moje rozkazy.

    LOKALIZACJA KOŚCIOŁA (KS):
    Kościół składa się z 6 kafelków i znajduje się na polach: F7, G7, H7, F8, G8, H8.
    Najbliższa droga (road), na którą może wjechać transporter, przebiega w rzędzie 6. Pola bezpośrednio sąsiadujące z kościołem od północy to: F6, G6, H6.

    TWOJA PROCEDURA DZIAŁANIA (Krok po kroku):
    1. Wyślij {"action": "reset"}, aby upewnić się, że zaczynamy z czystą planszą i pełną pulą AP.
    2. Stwórz transporter z załogą zwiadowców: {"action": "create", "type": "transporter", "passengers": 4}. Zapisz jego hash!
    3. Przemieść transporter na drogę tuż przy kościele, optymalnie na pole F6 lub G6: {"action": "move", "object": "HASH_TRANSPORTERA", "where": "F6"}.
    4. Wysadź zwiadowców: {"action": "dismount", "object": "HASH_TRANSPORTERA", "passengers": 4}.
    5. Użyj {"action": "getObjects"}, by zidentyfikować nowe pozycje zwiadowców po opuszczeniu pojazdu.
    6. Wydaj zwiadowcom polecenia ruchu (move) na pola wewnątrz kościoła (np. F7, G7, H7, F8).
    7. Gdy znajdą się na polach kościoła, wykonaj inspekcje: {"action": "inspect", "object": "HASH_ZWIADOWCY"}.
    8. Pobierz logi za pomocą {"action": "getLogs"}.
    9. BARDZO WAŻNE: Gdy tylko odczytasz logi z kościoła i poznasz ukryte tam informacje, PRZERWIJ wywoływanie narzędzi. Wypisz w treści swojej odpowiedzi, co dokładnie znalazłeś w kościele, a następnie wyraźnie poproś mnie o dalsze wytyczne.

    NIE podejmuj żadnych kolejnych działań poszukiwawczych ani ewakuacyjnych, dopóki nie wpiszę Ci w konsoli, co masz dalej zrobić. Czekaj na mój sygnał.
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
    task="domatowo",
    logs_dir_path=Path(__file__).parent / "logs",
    main_model=os.getenv("MODEL_ID"),
    main_system_prompt=MAIN_SYSTEM_PROMPT,
    bonus_system_prompt=BONUS_SYSTEM_PROMPT,
    e2b_api_key=os.getenv("E2B_API_KEY"),
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
                        "description": "Pełny słownik parametrów dla klucza answer, np. {'action': 'reset'} albo {'action': 'move', 'object': 'xyz', 'where': 'D2'}",
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
    },
]
