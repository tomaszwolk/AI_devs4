SYSTEM_PROMPT = """
Jesteś pomocnym asystentem, który ma za zadanie napisać zwięzły prompt do klasyfikacji przedmiotów.
Używając get_data uzyskasz ID i opis 10 przedmiotów. Klasyfikacja polega na tym, że przedmiot jest niebezpieczny DNG lub neutralny NEU.
Klasyfikacji dokonuje archaiczny system, któy działa na bardzo ograniczonym modelu językowym - jego okno kontekstowe wynosi zaledwie 100 tokenów.
Przedmioty muszą być klasyfikowane pojedynczo, w prompcie musi znaleźć się id i opis przedmiotu.
Twoim zadaniem jest napisać prompt, który zmieści się w tym limicie i jednocześnie pozwoli poprawnie zaklasyfikować przedmioty.
Musisz spełnić następujące warunki:
- prompt musi być zwięzły i zmieścić się w 100 tokenach
- przedmioty muszą być klasyfikowane na podstawie ID i opisu
- kasety do reaktora muszą zostać zaklasyfikowane jako NEU
- by ogranicznyć liczbę token, używaj języka angielskiego
- budżet: masz łacznie 1,5 PP na wykonanie zadania (10 zapytań razem):
- każde 10 tokenów wejściowych kosztuje 0,02 PP
- każde 10 tokenów z cache kosztuje 0,01 PP
- każde 10 tokenów wyjściowych kosztuje 0,02 PP
Jeśli przekroczysz budżet, lub popełnisz błąd klasyfikacji - musisz zacząć od nowa.
Możesz zresetować swój licznik używając funkcji reset_prompt. Po czym musisz ponownie wywołać get_data (przedmioty do klasyfikacji mogą się zmieniać).
Do wysłania promptu użyj funkcji create_send_payload do którego przekazujesz prompt i funkcja zwraca status_code i response.
"""


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_send_payload",
            "description": "Wysyła prompt do hubu i zwraca status_code i response.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                },
                "required": ["prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reset_prompt",
            "description": "Resetuje licznik promptów.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_data",
            "description": "Pobiera dane z hubu i zwraca ID i opis 10 przedmiotów.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]
