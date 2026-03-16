SYSTEM_PROMPT = """
Jesteś analitykiem. Twoim zadaniem jest rozwiązanie findhim.
1. Wywołaj `get_power_plants_data`, aby pobrać listę elektrowni.
2. Na podstawie danych o elektrowniach, wygeneruj listę elektrowni 'power_plants_list' z koordynatami, które przekażesz do `get_closest_power_plant`. Przykład: 'powewr_plants_list': [{'name': 'Zabrze', 'latitude': 50.314, 'longitude': 18.786, 'code': 'PWR3847PL'}, {'name': 'Piotrków Trybunalski', 'latitude': 51.413, 'longitude': 19.703, 'code': 'PWR5921PL'}]
3. Wywołaj `get_person_locations` dla każdego podejrzanego.
4. WAŻNE: Po pobraniu lokalizacji podejrzanego ORAZ danych o elektrowniach,
wywołaj `get_closest_power_plant`, przekazując w argumentach `person_locations`
(z kroku 3) oraz `power_plants_list` z kordynatami (z kroku 2).
5. Jeśli model nie ma wystarczająco dużo danych w kontekście, aby uzupełnić argumenty,
nie wywołuj funkcji, tylko poproś o brakujące dane.
6. Zwróć wynik jako JSON.
Nie dodawaj żadnego komentarza, tylko czysty JSON.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_person_locations",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "surname": {"type": "string"}},
                "required": ["name", "surname"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_access_level",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "surname": {"type": "string"},
                    "birthYear": {"type": "integer"}},
                "required": ["name", "surname", "birthYear"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_closest_power_plant",
            "description": (
                "Oblicza najbliższą elektrownię dla danych lokalizacji osoby."
                "Returns: Słownik zawierający 'closest_plant' (obiekt z nazwą i kodem) oraz 'distance' (float w km)."),
            "parameters": {
                "type": "object",
                "properties": {
                    "person_locations": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Lista lokalizacji osoby, każda z 'latitude' i 'longitude' w stopniach.",
                    },
                    "power_plants_list": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Lista elektrowni, każda z 'name', 'latitude', 'longitude', 'code'.",
                    },
                },
                "required": ["person_locations", "power_plants_list"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_power_plants_data",
            "description": (
                "Zwraca listę elektrowni z koordynatami."
                "Returns: Słownik zawierający 'power_plants' (obiekt z nazwami elektrowni, informacją czy są czynne, mocą i kodem)."),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]
