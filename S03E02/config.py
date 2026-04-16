import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ROOT_ENV_PATH)

API_KEY = os.getenv("HUB_API_KEY")
OPENROUTER_URL = os.getenv("OPENROUTER_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

HUB_URL = os.getenv("HUB_URL")
VERIFY_URL = HUB_URL + "/verify"
SHELL_URL = f"{HUB_URL}/api/shell"
TASK = "firmware"
LOGS_DIR_PATH = Path(__file__).parent / "logs"

MAIN_MODEL = os.getenv("SONNET_MODEL_ID")

MAIN_SYSTEM_PROMPT = """
Jesteś zaawansowanym agentem AI, specjalistą ds. cyberbezpieczeństwa i systemów Linux.
Twoim zadaniem jest naprawienie i uruchomienie zepsutego oprogramowania na zdalnej maszynie wirtualnej
w celu zdobycia kodu potwierdzającego (w formacie `ECCS-xxxx...`) i przesłania go do centrali w celu uzyskania flagi {FLG:...}.

Oto Twoje narzędzia:
1. `run_shell_command` - do interakcji z niestandardową powłoką Linux.
2. `send_verify_answer` - do przesłania kodu (ECCS-...) do centrali w celu uzyskania flagi {FLG:...}.

## ZASADY BEZPIECZEŃSTWA (KRYTYCZNE)
Działasz na koncie zwykłego użytkownika z surowymi restrykcjami.
Załamanie poniższych reguł skutkuje banem, utratą postępu i resetem maszyny (reboot):
1. ZABRONIONE KIERUNKI: Absolutnie NIGDY nie sprawdzaj, nie odczytuj i nie przechodź do katalogów: `/etc`, `/root`, `/proc/`.
2. PLIKI .gitignore: Jeśli podczas przeglądania katalogów znajdziesz plik `.gitignore`,
natychmiast sprawdź jego zawartość. Nigdy nie odczytuj ani nie edytuj plików wymienionych w `.gitignore`.

Jeśli otrzymasz odpowiedź z systemu o nałożonym BANIE, oznacza to, że złamałeś zasady.
Skrypt automatycznie odczeka karę czasową, ale maszyna wirtualna zostanie zresetowana.
Będziesz musiał dostosować plan i nigdy więcej nie próbować komendy, za którą dostałeś bana.

## PLAN DZIAŁANIA I ZALECENIA
1. **Zrozumienie środowiska:** To NIE JEST standardowy Linux.
Zawsze zaczynaj od komendy `help`, aby zrozumieć, jakie komendy są dostępne.
Szczególną uwagę zwróć na to, jak czyta się i EDYTUJE pliki (standardowe edytory jak vim/nano mogą nie działać).
2. **Rekonesans:** Zbadaj folder, w którym się znajdujesz, poszukaj ukrytych haseł w systemie (pamiętając o katalogach zabronionych i gitignore).
3. **Analiza aplikacji:** Główny plik binarny to `/opt/firmware/cooler/cooler.bin`.
Aplikacja posiada plik konfiguracyjny (np. `settings.ini`).
Twoim zadaniem jest zdobycie hasła i odpowiednia zmiana konfiguracji tak, aby binarka poprawnie wystartowała.
4. **Uzyskanie kodu pośredniego:** Po prawidłowej rekonfiguracji i uruchomieniu `cooler.bin`
powinieneś zobaczyć na ekranie kod zaczynający się od `ECCS-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`.
5. **Weryfikacja (KROK KRYTYCZNY):** Sam kod `ECCS-...` TO JESZCZE NIE JEST KONIEC ZADANIA! Gdy go zdobędziesz, musisz wywołać narzędzie `verify_flag` i przekazać mu ten kod.
6. **Sprawdzenie wyniku weryfikacji:**
   - Jeśli w odpowiedzi od `verify_flag` otrzymasz string zawierający `FLG:...`, ZADANIE JEST ZAKOŃCZONE SUKCESEM.
   - Jeśli `verify_flag` zwróci błąd lub informację o nieprawidłowym kodzie, oznacza to, że Twoja konfiguracja w `settings.ini` nie była w 100% poprawna. Musisz wrócić do edycji konfiguracji, wygenerować nowy kod `ECCS-...` i ponownie wysłać go do weryfikacji.

Myśl na głos. Analizuj wynik każdej komendy przed podjęciem następnego kroku. Wykonuj tylko jedną komendę w jednym kroku agenta.
"""

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": ("""
            Wykonuje pojedynczą komendę powłoki w zdalnym systemie
            Linux maszyny wirtualnej. Użyj 'help' na początku, aby
            poznać dostępne komendy, ponieważ system jest niestandardowy.""").strip(),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Polecenie do wykonania, np. 'help', 'ls [path]', 'cat <path>'.",
                    },
                },
                "required": ["command"],
            },
            "required": ["command"],
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_verify_answer",
            "description": ("""Narzędzie służące do wysłania końcowej odpowiedzi.
            Użyj go TYLKO wtedy, gdy zdobędziesz ostateczny kod potwierdzający (w formacie ECCS-...).""").strip(),
            "parameters": {
                "type": "object",
                "properties": {
                    "confirmation_code": {
                        "type": "string",
                        "description": ("""
                        Ostateczny kod potwierdzający (w formacie
                        ECCS-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx).""").strip(),
                    },
                },
            },
            "required": ["confirmation_code"],
        },
    },
]
