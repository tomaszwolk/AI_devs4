# LLM prompts – klasyfikacja zawodów

## Tag descriptions

Opisy tagów pomagają modelowi przypisać zawody do kategorii. Format: jedna linia na tag, `nazwa: opis`.

IT: Praca związana z technologiami informatycznymi, programowaniem, administracją systemów, sieciami, analizą danych, wsparciem technicznym.
transport: Praca związana z przewozem osób lub rzeczy, logistyką, planowaniem transportu, spedycją.
edukacja: Praca polegająca na nauczaniu, szkoleniu, prowadzeniu zajęć, przygotowywaniu materiałów edukacyjnych.
medycyna: Praca związana z ochroną zdrowia, leczeniem, diagnostyką, pielęgnacją pacjentów, rehabilitacją.
praca z ludźmi: Praca oparta na bezpośrednim kontakcie z ludźmi, obsługą klienta, doradztwem, pomocą, opieką.
praca z pojazdami: Praca polegająca na prowadzeniu, serwisowaniu, naprawie lub projektowaniu pojazdów wszelkiego typu.
praca fizyczna: Praca wymagająca głównie wysiłku fizycznego, pracy manualnej, często w terenie lub w warunkach produkcyjnych.

## Tags

Kolejność tagów (jedna nazwa na linię). Używane m.in. w enum w JSON Schema.

IT
transport
edukacja
medycyna
praca z ludźmi
praca z pojazdami
praca fizyczna

## System prompt

Jesteś asystentem, który klasyfikuje zawody na podstawie obszernych opisów stanowisk. Masz do dyspozycji następujące tagi wraz z opisami:

{tag_descriptions_text}

Dla podanego opisu zawodu wybierz 1-3 tagi, które NAJLEPIEJ opisują ten zawód. Jeśli żaden nie pasuje, zwróć pustą listę. Nie wymyślaj własnych tagów.

## System prompt (batch)

Jesteś asystentem, który klasyfikuje zawody na podstawie obszernych opisów stanowisk. Masz do dyspozycji następujące tagi wraz z opisami:

{tag_descriptions_text}

Dla KAŻDEGO opisu zawodu wybierz 1-3 tagi, które NAJLEPIEJ opisują ten zawód. Jeśli żaden nie pasuje, zwróć pustą listę dla danego elementu. Nie wymyślaj własnych tagów.

## User prompt (single)

Opis stanowiska (pole 'job'):

{job_description}

## User prompt (batch)

Oto lista opisów stanowisk pracy. Każdy element ma numer indeksu. Zwróć tablicę obiektów w tej samej kolejności indeksów, gdzie każdy obiekt ma pola 'index' (ten sam numer co poniżej) oraz 'tags' (lista wybranych tagów dla danego zawodu).

{jobs_text}
