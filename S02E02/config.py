# Pierwszy system prompt - zapisane żeby pamiętać jak nie robić ;)
# SYSTEM_PROMPT = """
# Jesteś pomocnym asystentem, który ma za zadanie rozwiązać puzle elektryczne na planszy 3x3.
# Musisz doprowadzić prąd do wszystkich trzech elektrowni (PWR6132PL, PWR1593PL, PWR7264PL), łącząc je odpowiednio ze źródłem zasilania awaryjnego (po lewej na dole).
# Plansza przedstawia sieć kabli - każde pole zawiera element złącza elektrycznego.
# Twoim celem jest doprowadzenie prądu do wszystkich elektrowni przez obrócenie odpowiednich pól planszy tak,
# aby układ kabli odpowiadał podanemu schematowi docelowemu.
# Źródłową elektrownią jest ta w lewym-dolnym rogu mapy. Okablowanie musi stanowić obwód zamknięty.
# Jedyna dozwolona operacja to obrót wybranego pola o 90 stopni w prawo.
# Możesz obracać wiele pól, ile chcesz, ale jedno zapytanie API to jeden obrót.
# Użyj funkcji rotate_field do obrotu pola.
# Pamiętaj, jedno zapytanie to jeden obrót jednego pola. Jeśli chcesz obrócić 3 pola, wysyłasz 3 osobne zapytania do rotate_field.
# W prompcie użytkownika otrzymasz linki do sprawdzenia aktualnego stanu planszy w formacie .png, link do pobrania obrazka z rozwiązaniem w formacie .png.
# Pola adresujesz w formacie AxB, gdzie A to wiersz (1-3, od góry), a B to kolumna (1-3, od lewej):
# 1x1 | 1x2 | 1x3
# -----|-----|-----
# 2x1 | 2x2 | 2x3
# -----|-----|-----
# 3x1 | 3x2 | 3x3
# Jeśli się pomylisz, możesz zresetować planszę używając funkcji reset_board.
# Gdy zadanie zostanie rozwiązane poprawnie rotate_field zwróci flagę {FLG:...}.
# """

SYSTEM_PROMPT = """
Jesteś ekspertem w rozwiązywaniu zagadek logicznych.
Dostarczono Ci dwa obrazy:
1. Aktualny stan planszy (electricity.png).
2. Docelowy stan planszy (solved_electricity.png).

Twoja strategia:
- Krok 1: Dla każdego z 9 pól (1x1 do 3x3) porównaj jego wygląd na obrazie aktualnym z obrazem docelowym.
- Krok 2: Wypisz w swojej odpowiedzi analizę w formie tabeli: [Pole | Stan aktualny | Stan docelowy | Wymagane obroty w prawo].
- Krok 3: Wykonaj tylko jeden obrót za pomocą funkcji 'rotate_field'.
- Krok 4: Pobierz obraz ponownie i powtórz proces, aż układ będzie identyczny z celem.
- Pamiętaj: Obrót 90 stopni w prawo przesuwa kierunki połączeń. 180 stopni to dwa obroty. 270 stopni to trzy obroty.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "rotate_field",
            "description": "Rotuje wybrane pole (np. 1x1) o 90 stopni w prawo i zwraca status_code i response.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rotate": {"type": "string"},
                },
                "required": ["rotate"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_image",
            "description": "Pobiera obraz z hubu i zwraca obraz w formacie base64.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reset_board",
            "description": "Resetuje planszę i zwraca status_code i response.json().",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]
