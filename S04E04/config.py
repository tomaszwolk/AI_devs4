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
    bonus_system_prompt: str


ROOT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ROOT_ENV_PATH)

MAIN_SYSTEM_PROMPT = ("""
    Jesteś analitykiem i inżynierem ds. integracji (Agentem AI), którego celem jest uporządkowanie notatek w wirtualnym systemie plików.
    Dane wejściowe (ogłoszenia, rozmowy, transakcje oraz schemat pomocy API) otrzymałeś w poleceniu.

    ### TWOJE ZADANIE:
    Zbuduj strukturę wirtualnego systemu plików poprzez API (za pomocą `call_verify_api`), a następnie zgłoś jej ukończenie akcją "done".

    ### ZASADY TWORZENIA SYSTEMU PLIKÓW:
    1. BRAK ROZSZERZEŃ: Nazwy plików nie mogą zawierać kropek ani rozszerzeń (np. żadnego .md, .txt). Plik ma się nazywać po prostu `/miasta/opalino`.
    2. Brak polskich znaków i małe litery: Wszystkie nazwy plików, katalogów oraz klucze w JSON i teksty nie mogą zawierać polskich znaków (ł->l, ó->o) ani wielkich liter. Wyjątkiem są wyświetlane nazwy linków w markdownie (np. `[Domatowo](/miasta/domatowo)`).
    3. Mianownik liczby pojedynczej w towarach (z wyjątkiem słowa "ziemniaki"). Używaj np: "koparka", "lopata", "wolowina", "wiertarka", "chleb", "maka", "ziemniaki".
    4. Pełne imiona i nazwiska: Jeśli notatki wspominają kogoś po imieniu i nazwisku w różnych miejscach (np. Rafał, a potem Kisiel), połącz je jako `rafal_kisiel`.

    ### STRUKTURA DO ZBUDOWANIA:
    Utwórz trzy główne katalogi: `/miasta`, `/osoby`, `/towary`.

    **Wewnątrz katalogu `/miasta`**:
    - Pliki tekstowe nazwane od miast (np. `/miasta/opalino`).
    - Zawartość pliku to format JSON opisujący zapotrzebowanie TEGO MIASTA (z `ogłoszenia.txt` po korektach z `rozmowy.txt`). Klucz to nazwa towaru (bez pl znaków), wartość to liczba całkowita. 
    - Przykład zawartości pliku: `{"chleb": 50, "ryz": 45, "wiertarka": 7}`

    **Wewnątrz katalogu `/osoby`**:
    - Pliki tekstowe nazwane od imienia i nazwiska (np. `/osoby/iga_kapecka`). Powiązania wyciągnij z rozmów.
    - Zawartość pliku to link Markdown do miasta danej osoby: `[Opalino](/miasta/opalino)`.

    **Wewnątrz katalogu `/towary` (BARDZO WAŻNE!)**:
    - Pliki nazwane od towarów (np. `/towary/ryz`, `/towary/lopata`).
    - TWORZYSZ PLIKI TYLKO DLA TOWARÓW, KTÓRE SĄ FIZYCZNIE SPRZEDAWANE w pliku `transakcje.txt`! 
    - Jeśli towaru (np. woda) NIE MA w pliku transakcji jako sprzedawanego, NIE TWORZ dla niego pliku w katalogu `/towary/`!
    - Zawartość pliku to link Markdown do miasta SPRZEDAJĄCEGO ten towar (Miasto A -> towar -> Miasto B, to Miasto A sprzedaje). Przykład dla `/towary/ryz`: `[Puck](/miasta/puck)`. Jeśli towar sprzedaje więcej miast, daj oddzielne linki jeden pod drugim (po `\\n`).

    ### INSTRUKCJA DZIAŁANIA KROK PO KROKU:
    1. Zbuduj w pamięci relacje bazując na danych.
    2. Stwórz wirtualny system plików używając `call_verify_api`. Użyj `batch_mode` (wysyłając listę akcji w `answer_payload`). Najpierw zrób reset systemu, a potem twórz katalogi i pliki.
       *Przykład Payloadu*:
       `[{"action":"reset"}, {"action":"createDirectory","path":"/miasta"}, {"action":"createFile","path":"/miasta/opalino","content":"{\\"chleb\\":45}"}]`
    3. Jeśli napotkasz błąd z API, analizuj go i napraw. Jeśli API mówi, że plik nie dotyczy towaru sprzedawanego, USUŃ TEN PLIK akcją `deleteFile`.
    4. Na koniec wyślij: `{"action": "done"}`.
""").strip()

BONUS_SYSTEM_PROMPT = ("""
    Jesteś Agentem AI ds. cyberbezpieczeństwa. Twoim zadaniem jest zdobycie ukrytej, bonusowej flagi CTF z wirtualnego systemu plików.
    UWAGA KRYTYCZNA: Pod żadnym pozorem nie używaj akcji "reset"! Główna część zadania znajduje się już na serwerze i musi tam pozostać nietknięta.

    ### MECHANIKA ZAGADKI:
    Wskazówka: "print(*map(ord,'FLAG')) siedzi w /flag/"
    Centrala sprawdza ten katalog listując pliki wg kolejności alfabetycznej nazw.
    Kody ASCII dla liter słowa FLAG to: F=70, L=76, A=65, G=71.
    Musisz utworzyć pliki, których nazwy po alfabetycznym posortowaniu stworzą ciąg: plik1 -> plik2 -> plik3 -> plik4.
    Rozmiar każdego pliku (czyli długość wartości "content") musi odpowiadać dokładnie kodowi ASCII odpowiedniej litery.

    ### TWOJE ZADANIE KROK PO KROKU:

    KROK 1:
    Użyj narzędzia `call_verify_api` wysyłając w 'answer_payload' listę akcji (tryb batch_mode).
    Wykonaj w nim następujące czynności:
    1. {"action": "createDirectory", "path": "/flag"}
    2. {"action": "createFile", "path": "/flag/1", "content": "tutaj podaj dokładnie 70 dowolnych znaków, np. X"} (Rozmiar 70 to litera F)
    3. {"action": "createFile", "path": "/flag/2", "content": "tutaj podaj dokładnie 76 dowolnych znaków"} (Rozmiar 76 to litera L)
    4. {"action": "createFile", "path": "/flag/3", "content": "tutaj podaj dokładnie 65 dowolnych znaków"} (Rozmiar 65 to litera A)
    5. {"action": "createFile", "path": "/flag/4", "content": "tutaj podaj dokładnie 71 dowolnych znaków"} (Rozmiar 71 to litera G)

    *Uwaga techniczna do KROKU 1:* Musisz wygenerować fizycznie ciągi X-ów w JSON. Nie używaj mnożenia (np. "X"*70). Jeśli otrzymasz błąd z API "Directory already exists", po prostu wywołaj narzędzie jeszcze raz podając same akcje `createFile` (z pominięciem tworzenia katalogu).

    KROK 2:
    Sprawdź zawartość katalogu /flag/ za pomocą `call_verify_api` wysyłając w 'answer_payload' akcję `listFiles` z parametrem 'path': "/flag/".
    Poczekaj na decyzję użytkownika.

""").strip()

settings = Settings(
    api_key=os.getenv("HUB_API_KEY"),
    openrouter_url=os.getenv("OPENROUTER_URL"),
    hub_url=os.getenv("HUB_URL"),
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
    verify_url=os.getenv("HUB_URL") + "/verify",
    task="filesystem",
    logs_dir_path=Path(__file__).parent / "logs",
    main_model=os.getenv("MODEL_ID"),
    main_system_prompt=BONUS_SYSTEM_PROMPT,
    bonus_system_prompt=BONUS_SYSTEM_PROMPT,
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
    }
]
