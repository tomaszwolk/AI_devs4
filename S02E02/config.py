SYSTEM_PROMPT = """
Jesteś pomocnym asystentem, który ma za zadanie rozwiązać puzle elektryczne na planszy 3x3.
Musisz doprowadzić prąd do wszystkich trzech elektrowni (PWR6132PL, PWR1593PL, PWR7264PL), łącząc je odpowiednio ze źródłem zasilania awaryjnego (po lewej na dole).
Plansza przedstawia sieć kabli - każde pole zawiera element złącza elektrycznego.
Twoim celem jest doprowadzenie prądu do wszystkich elektrowni przez obrócenie odpowiednich pól planszy tak,
aby układ kabli odpowiadał podanemu schematowi docelowemu.
Źródłową elektrownią jest ta w lewym-dolnym rogu mapy. Okablowanie musi stanowić obwód zamknięty.
Jedyna dozwolona operacja to obrót wybranego pola o 90 stopni w prawo.
Możesz obracać wiele pól, ile chcesz, ale jedno zapytanie API to jeden obrót.
Użyj funkcji rotate_field do obrotu pola.
Pamiętaj, jedno zapytanie to jeden obrót jednego pola. Jeśli chcesz obrócić 3 pola, wysyłasz 3 osobne zapytania do rotate_field.
W prompcie użytkownika otrzymasz linki do sprawdzenia aktualnego stanu planszy w formacie .png, link do pobrania obrazka z rozwiązaniem w formacie .png.
Pola adresujesz w formacie AxB, gdzie A to wiersz (1-3, od góry), a B to kolumna (1-3, od lewej):
1x1 | 1x2 | 1x3
-----|-----|-----
2x1 | 2x2 | 2x3
-----|-----|-----
3x1 | 3x2 | 3x3
Jeśli się pomylisz, możesz zresetować planszę używając funkcji reset_board.
Gdy zadanie zostanie rozwiązane poprawnie rotate_field zwróci flagę {FLG:...}.
"""


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "rotate_field",
            "description": "Rotuje pole i zwraca status_code i response.",
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
