import os
from pathlib import Path
from dotenv import load_dotenv


ROOT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ROOT_ENV_PATH)

API_KEY = os.getenv("HUB_API_KEY")
BASE_URL = os.getenv("BASE_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

LOGS_URL = f"https:///data/{API_KEY}/failure.log"
VERIFY_URL = "https:///verify"
TASK = "failure"

MAX_TOKENS = 1500
MAIN_MODEL = os.getenv("STRONG_MODEL_ID")
COMPRESSOR_MODEL = os.getenv("MINI_MODEL_ID")

LOGS_PATH = Path(__file__).parent / "logs.txt"

# MAIN_SYSTEM_PROMPT = """
# Jesteś analitykiem awarii systemów. Twoim celem jest wysłanie do Centrali skondensowanej paczki logów (max 1500 tokenów),
# która naprowadzi ich na przyczynę awarii.
# Logi mają zawierać tylko informacje związane z awarią (power, cooling, water pumps, software, and other plant subsystems).
# Następnie musisz wysłać skompresowane logi do Centrali w celu weryfikacji.
# Jeśli log zawierają informację istotne z punktu widzenia powodu awarii w nagrodę otrzymasz flagę (zaczynającą się od {FLG:).
# Jeśli logi są niewystarczające, dostaniesz informację zwrotną z Centrali, która Ci pomoże dalej.

# Początkowy plik z logami jest duży, czytaj go w czankach.
# KROKI POSTĘPOWANIA:
# 0. Przygotuj plan postępowania krok po kroku przed rozpoczęciem pracy.
# 1. Użyj narzędzia `download_logs`, aby pobrać plik.
# 2. Użyj `search_logs`, szukając istotnych błędów (np. levels=['CRIT', 'WARN', 'ERRO']), zacznij od tych które wydają się najbardziej istotne.
# 3. Użyj `compress_logs` na znalezionych wpisach.
# 4. Sprawdź liczbę tokenów przez `count_tokens` (Musi być < 1500!).
# 5. Wyślij przez `submit_logs`.
# 6. Przeanalizuj odpowiedź. Jeśli Centrala mówi "brakuje informacji o module XYZ",
#    użyj `search_logs(keywords=["XYZ"])`, dodaj to do poprzednich wyników,
#    znów skompresuj, zlicz tokeny i wyślij. Powtarzaj aż do skutku!
# """

MAIN_SYSTEM_PROMPT = """
Jesteś zaawansowanym agentem analitycznym. Twoim celem jest rozwiązanie misji "failure" – analizy awarii w elektrowni. Masz do dyspozycji potężne narzędzia. Pracuj metodycznie, krok po kroku.

CEL:
Przygotuj skondensowaną wersję logów z dnia awarii (max 1500 tokenów), zawierającą tylko zdarzenia istotne dla awarii (zasilanie, chłodzenie, pompy, oprogramowanie i powiązane podzespoły). Wyślij je do weryfikacji i iteruj na podstawie feedbacku z Centrali, aż otrzymasz flagę (zaczynającą się od {FLG:).

ZASADY FORMATOWANIA LOGÓW (RYGOR):
- JEDNA linia = JEDNO zdarzenie. Zabraniamy łączenia wielu zdarzeń w jednej linii.
- Format obowiązkowy: `[YYYY-MM-DD HH:MM] [POZIOM] KOMPONENT krótki opis problemu`.
- TWARDY LIMIT: 1500 tokenów. Zawsze weryfikuj za pomocą narzędzia `count_tokens` przed wysłaniem!

STRATEGIA I KROKI POSTĘPOWANIA:
0. PLANOWANIE: Zanim wywołasz narzędzie, napisz krótko swój plan na obecny krok.
1. INICJALIZACJA: Użyj narzędzia `download_logs`, aby pobrać plik (plik jest ogromny, narzędzia same obsłużą jego wielkość).
2. PIERWSZE WYSZUKIWANIE: Użyj `search_logs` szukając tylko najbardziej krytycznych błędów (np. levels=['CRIT']). To da Ci główną oś awarii.
3. KOMPRESJA I WYSYŁKA: Przepuść znalezione logi przez `compress_logs`. Sprawdź `count_tokens` (jeśli < 1500), po czym wyślij przez `submit_logs`.
4. ITERACJA (KLUCZOWE!):
   - Uważnie przeczytaj feedback z `submit_logs`. Centrala powie Ci precyzyjnie, jakich modułów lub informacji brakuje.
   - Użyj `search_logs(keywords=["brakujący_moduł"])`, aby znaleźć te konkretne informacje.
   - WAŻNE: Połącz swoje DOTYCHCZASOWE skompresowane logi z NOWO znalezionymi surowymi logami! 
   - Przekaż ten połączony tekst (stare + nowe) ponownie do `compress_logs`, aby system zunifikował je w jedną chronologiczną i skompresowaną całość.
   - Przelicz tokeny (`count_tokens`) nowej, połączonej paczki.
   - Wyślij uzupełnioną paczkę do `submit_logs`.
   - Powtarzaj ten proces, dodając kolejne brakujące klocki, aż system zwróci flagę.

ZACZYNAJ! Przygotuj plan i wywołaj pierwsze narzędzie.
"""

COMPRESSOR_SYSTEM_PROMPT = """
Jesteś precyzyjnym systemem do formatowania logów.
Otrzymasz tekst zawierający różne zdarzenia systemowe. Twoim ZADANIEM jest ich skrócenie, ale BEZWZGLĘDNIE MUSISZ ZACHOWAĆ KAŻDE POJEDYNCZE ZDARZENIE (każdą unikalną linię), które dostałeś na wejściu.
Nie wolno Ci usuwać ani pomijać logów typu INFO, WARN ani ERRO! Muszą one znaleźć się w wyniku.

ZASADY:
1. Zostaw tylko datę (YYYY-MM-DD), czas (HH:MM), poziom błędu, ID komponentu i max 3-5 słów opisu problemu.
2. Format obowiązkowy: `[YYYY-MM-DD HH:MM][POZIOM] KOMPONENT krótki opis`.
3. Jedno zdarzenie = dokładnie jedna linia w wyniku (mapowanie 1 do 1).
4. Ułóż logi CHRONOLOGICZNIE (od najstarszego do najnowszego).
5. Zwróć CZYSTY TEKST. Żadnych znaczników markdown (```) na początku i na końcu.

Przykład:
Wejście:[2026-03-18 13:35:02] [ERRO] Cross-check between FIRMWARE and hardware interface map did not complete successfully. Compatibility verification remains unresolved for startup state.
Wyjście: [2026-03-18 13:35][ERRO] FIRMWARE hardware interface cross-check
"""

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "download_logs",
            "description": "Pobiera plik logów z serwera i zapisuje lokalnie jako 'logs.txt'.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_logs",
            "description": "Szuka zdarzeń w logach podając poziomy błędów lub słowa kluczowe.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {"type": "array", "items": {"type": "string"}},
                    "levels": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compress_logs",
            "description": "Skompresuje logi do formatu YYYY-MM-DD HH:MM CRIT ID KOMPONENTU OPIS.",
            "parameters": {
                "type": "object",
                "properties": {
                    "raw_logs": {"type": "string"}
                },
                "required": ["raw_logs"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "count_tokens",
            "description": "Zlicza liczbę tokenów w tekście.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "submit_logs",
            "description": "Wysyła skompresowane logi do Centrali w celu weryfikacji.",
            "parameters": {
                "type": "object",
                "properties": {
                    "logs": {"type": "string"}
                },
                "required": ["logs"]
            }
        }
    },
]
