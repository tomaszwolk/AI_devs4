DECLARATION_SYSTEM_PROMPT = """
Jesteś analitykiem Systemu Przesyłek Konduktorskich.
Twoim zadaniem jest wypełnienie deklaracji transportowej.
Wykonaj to na podstawie wzoru deklaracji transportowej i bazy wiedzy.
Musisz spełnić następujące warunki:
- identyfikator_nadawcy: "450202122",
- punkt_nadawcy: "Gdańsk",
- punkt_docelowy: "Żarnowiec",
- waga: 2800,  # kg
- budżet: 0,  # PP - przesyłka ma być darmowa lub finansowana przez System
- zawartość: "kasety z paliwem do reaktora",
- uwagi_specjalne: "brak"
- ustal prawidłowy kod trasy - trasa Gdańsk - Żarnowiec wymaga sprawdzenia sieci połączeń i listy tras.
- Oblicz lub ustal opłatę - regulamin SPK zawiera tabelę opłat. Opłata zależy od kategorii przesyłki, jej wagi i przebiegu trasy. Budżet wynosi 0 PP - zwróć uwagę, które kategorie przesyłek są finansowane przez System.
"""

EXTRACT_SYSTEM_PROMPT = """
Jesteś analitykiem Systemu Przesyłek Konduktorskich.
Twoim zadaniem jest budowanie bazy wiedzy o przesyłce.
Docelowo musimy wypełnić deklarację transportową.
Wzór do deklaracji transportowej został Ci przekazany.
Warunki poprawnego wypełnienia deklaracji:
- Ustal prawidłowy kod trasy - trasa Gdańsk - Żarnowiec wymaga sprawdzenia sieci połączeń i listy tras.
- Oblicz lub ustal opłatę - regulamin SPK zawiera tabelę opłat. Opłata zależy od kategorii przesyłki, jej wagi i przebiegu trasy. Budżet wynosi 0 PP - zwróć uwagę, które kategorie przesyłek są finansowane przez System.
- Początkowe dane deklaracji zostały już wypełnione, są to: identyfikator nadawcy, punkt nadawcy, punkt docelowy, waga, budżet, zawartość, uwagi specjalne.
Masz dostęp do aktualnej bazy wiedzy: {kb}.
1. Analizuj dostarczony dokument/obraz.
2. Jeśli znajdziesz w nim jakiekolwiek informacje potrzebne do wypełnienia deklaracji, zaktualizuj bazę wiedzy.
3. Zwróć bazę wiedzy w formacie JSON.
"""

EXTRACT_SYSTEM_PROMPT_OLD = """
You are an AI assistant tasked with extracting data from transport documentation.
Return ALWAYS and ONLY a valid JSON object with the following structure:
{
    "new_urls": ["url1", "url2"],
    "extracted_knowledge": {"key": "value"}
}
If no links or info found, return empty lists/objects.
"""

# Empty tools, not used yet
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "",
            "description": "",
            "parameters": {
                "type": "object",
                "properties": {
                    "packageid": {"type": "string", "description": ""},
                },
                "required": [""],
            },
        },
    },
]
