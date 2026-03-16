from dotenv import load_dotenv
import json
import os
import pandas as pd
import chardet
import datetime
from pathlib import Path

import requests
from openai import OpenAI

from llm_config import (
    TAGS,
    get_schema_single_job,
    get_schema_batch_jobs,
    get_system_content,
    get_user_content_single,
    get_user_content_batch,
)


# 1. Pobierz dane z hubu - plik people.csv. Strona  - DONE
# 2. Przefiltruj dane, zostaw osoby spełniające kryteria:
# płeć (gender): mężczyzna,
# wiek (birthDate): 20-40 lat w 2026 roku
# miejsce urodzenia (birthPlace): Grudziądz


def filter_data(
    in_path: Path,
    out_path: Path,
    gender: str,
    birth_date: list[int],
    birth_place: str,
    sep: str,
) -> pd.DataFrame:
    with open(in_path, "rb") as f:
        result = chardet.detect(f.read(10000))
    encoding = result["encoding"]
    df = pd.read_csv(
        in_path,
        sep=sep,
        encoding=encoding,
        parse_dates=["birthDate"],
        date_format={"birthDate": "%d.%m.%Y"},
    )

    birth_start = datetime.datetime(birth_date[0], 1, 1)
    birth_end = datetime.datetime(birth_date[1], 12, 31)
    mask = (
        (df["gender"].str.upper() == gender.upper())
        & (df["birthDate"].between(birth_start, birth_end))
        & (df["birthPlace"].str.lower() == birth_place.lower())
    )
    df_filtered = df.loc[
        mask,
        ["name", "surname", "gender", "birthDate", "birthPlace", "birthCountry", "job"],
    ]

    return df_filtered


# 3. Otaguj zawody (prompty i schematy w llm_prompts.md / llm_config.py)
def tag_job_with_llm(
    job_description: str, tags: list[str], model_id: str, client: OpenAI
) -> list[str]:
    """Wysyła opis stanowiska do LLM przez OpenRouter i zwraca listę tagów z TAGS."""
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": get_system_content(tags, batch=False)},
            {"role": "user", "content": get_user_content_single(job_description)},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "job_tags",
                "strict": True,
                "schema": get_schema_single_job(tags),
            },
        },
    )

    message = response.choices[0].message

    # Preferowany sposób przy Structured Output: użyj sparsowanego obiektu
    data = getattr(message, "parsed", None)

    # Fallback: sparsuj ręcznie z content, jeśli parsed nie jest dostępne
    if data is None:
        content = message.content
        if isinstance(content, list):
            # jeśli SDK zwróci listę części – sklej tekstowe fragmenty
            content = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        if isinstance(content, str):
            text = content.strip()
            if text.startswith("```"):
                # usuń ewentualne znaczniki ```json ... ```
                text = text.strip("`")
                # po odcięciu backticków może zostać prefiks "json\n"
                if text.lower().startswith("json"):
                    text = text[4:].lstrip()
            data = json.loads(text)
        else:
            raise ValueError(
                f"Nieoczekiwany typ content w odpowiedzi modelu: {type(content)}"
            )

    returned_tags = data.get("tags", [])
    # Upewnij się, że są tylko dozwolone tagi (na wszelki wypadek)
    return [t for t in returned_tags if t in tags]


def tag_jobs_batch_with_llm(
    jobs: list[str],
    tags: list[str],
    model_id: str,
    client: OpenAI,
    start_index: int = 0,
) -> dict[int, list[str]]:
    """Taguje wiele opisów stanowisk w jednym wywołaniu. Zwraca dict: index -> lista tagów."""
    jobs_text = "\n".join(f"{i}: {job}" for i, job in enumerate(jobs))
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": get_system_content(tags, batch=True)},
            {"role": "user", "content": get_user_content_batch(jobs_text)},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "job_tags_batch",
                "strict": True,
                "schema": get_schema_batch_jobs(tags),
            },
        },
    )

    message = response.choices[0].message
    data = getattr(message, "parsed", None)

    if data is None:
        content = message.content
        if isinstance(content, list):
            content = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )
        if isinstance(content, str):
            text = content.strip()
            if text.startswith("```"):
                text = text.strip("`")
                if text.lower().startswith("json"):
                    text = text[4:].lstrip()
            data = json.loads(text)
        else:
            raise ValueError(
                f"Nieoczekiwany typ content w odpowiedzi modelu: {type(content)}"
            )

    result: dict[int, list[str]] = {}
    for item in data:
        idx = int(item.get("index"))
        item_tags = item.get("tags", [])
        valid_tags = [t for t in item_tags if t in tags]
        result[start_index + idx] = valid_tags

    # print(f"From tag_jobs_batch_with_llm: {result}")  # For testing
    return result


def tag_jobs_in_dataframe(
    df: pd.DataFrame,
    tags: list[str],
    model_id: str,
    client: OpenAI,
    batch_size: int = 10,
) -> pd.DataFrame:
    """
    Dla każdej osoby w df wywołuje LLM (w batchach) i dopisuje kolumnę 'tags' (lista tagów).
    """
    df = df.copy()
    jobs = df["job"].tolist()
    all_tags: list[list[str]] = [[] for _ in range(len(jobs))]

    for start in range(0, len(jobs), batch_size):
        batch_jobs = jobs[start: start + batch_size]
        batch_result = tag_jobs_batch_with_llm(
            batch_jobs,
            tags=tags,
            model_id=model_id,
            client=client,
            start_index=start
        )
        for idx, tlist in batch_result.items():
            if 0 <= idx < len(all_tags):
                all_tags[idx] = tlist

    df["tags"] = all_tags
    return df


# 4. Wybierz osoby z tagiem transport.
def parse_tags(value: object) -> list[str]:
    if isinstance(value, list):
        return value
    if not isinstance(value, str):
        return []
    text = value.strip()
    if not text:
        return []
    # próbuj sparsować jak JSON – po zamianie '' na ""
    try:
        candidate = text
        if "'" in candidate and '"' not in candidate:
            candidate = candidate.replace("'", '"')
        parsed = json.loads(candidate)
        if isinstance(parsed, list):
            return [str(t) for t in parsed]
    except Exception:
        pass
    # fallback: ręczne rozdzielenie po przecinkach z usunięciem nawiasów
    inner = text.strip("[]")
    parts = [p.strip().strip("'\"") for p in inner.split(",") if p.strip()]
    return parts


# 5. Wyślij odpowiedź - prześlij tablicę obiektów na adres
# https:///verify w formacie
# {
#       "apikey": "tutaj-twój-klucz-api",
#       "task": "people",
#       "answer": [
#         {
#           "name": "Jan",
#           "surname": "Kowalski",
#           "gender": "M",
#           "born": 1987,
#           "city": "Warszawa",
#           "tags": ["tag1", "tag2"]
#         },
#         {
#           "name": "Anna",
#           "surname": "Nowak",
#           "gender": "F",
#           "born": 1993,
#           "city": "Grudziądz",
#           "tags": ["tagA", "tagB", "tagC"]
#         }
#       ]
#     }
# 6. Zdobycie flagi - jeśli wysłane dane będą poprawne, Hub w odpowiedzi
# odeśle flagę w formacie {FLG:JAKIES_SLOWO} - flagę należy wpisać pod adresem:
# https:/// (wejdź na tą stronę w swojej przeglądarce,
# zaloguj się kontem którym robiłeś zakup kursu i wpisz flagę w odpowiednie
# pole na stronie)


def main():
    # Załaduj zmienne z .env
    load_dotenv()
    # Wczytaj zmienne
    api_key = os.getenv("OPENROUTER_API_KEY")
    model_id = os.getenv("MODEL_ID")
    base_url = os.getenv("BASE_URL")
    hub_api_key = os.getenv("HUB_API_KEY")

    if not api_key or not model_id or not base_url:
        raise RuntimeError(
            "Brak jednej z wymaganych zmiennych środowiskowych: \
            OPENROUTER_API_KEY / MODEL_ID / BASE_URL"
        )
    if not hub_api_key:
        raise RuntimeError(
            "Brak HUB_API_KEY w .env – dodaj klucz API do huba, \
                aby wykonać krok 5 (verify)."
        )
    client = OpenAI(api_key=api_key, base_url=base_url)

    # 2. Przefiltruj dane
    out_path = Path(__file__).parent / "people_filtered.csv"
    if not os.path.exists(out_path):
        in_path = Path(__file__).parent / "people.csv"
        df = filter_data(in_path, out_path, "M", [1986, 2006], "Grudziądz", ";")
        df.to_csv(out_path, sep=";")
        print(f"Zapisano wyfiltrowane pozycje w: {out_path}")

    # 3. Otaguj zawody modelem językowym
    df_filtered = pd.read_csv(out_path, sep=";")
    # df_filtered = df_filtered.iloc[[1,5]]  # For testing
    tagged_path = Path(__file__).parent / "people_tagged.csv"
    tags = TAGS

    if not os.path.exists(tagged_path):
        df_tagged = tag_jobs_in_dataframe(
            df_filtered, tags, model_id, client, batch_size=10
        )
        df_tagged.to_csv(tagged_path, sep=";")
        print(df_tagged.head())
        print(f"Zapisano otagowane pozycje w: {tagged_path}")

    # 4. Wybierz osoby z tagiem 'transport'
    df_tagged = pd.read_csv(tagged_path, sep=";")

    df_tagged["tags"] = df_tagged["tags"].apply(parse_tags)

    mask_transport = df_tagged["tags"].apply(
        lambda ts: isinstance(ts, list) and "transport" in ts
    )
    df_transport = df_tagged.loc[mask_transport].copy()
    print(f"From df_transport: \n{df_transport}")  # For testing
    transport_path = Path(__file__).parent / "people_transport.csv"
    df_transport.to_csv(transport_path, sep=";")
    print(f"Liczba osób z tagiem 'transport': {len(df_transport)}")

    # 5. Wyślij odpowiedź do huba
    answer_payload = []
    for _, row in df_transport.iterrows():
        # urodzony rok na podstawie birthDate
        born_year: int
        bd = row.get("birthDate")
        if isinstance(bd, str):
            # oczekujemy formatu YYYY-MM-DD lub podobnego – weź pierwsze 4 cyfry
            digits = "".join(ch for ch in bd if ch.isdigit())
            born_year = int(digits[:4]) if len(digits) >= 4 else 0
        else:
            try:
                born_year = int(pd.to_datetime(bd).year)
            except Exception:
                born_year = 0

        answer_payload.append(
            {
                "name": row.get("name"),
                "surname": row.get("surname"),
                "gender": row.get("gender"),
                "born": born_year,
                "city": row.get("birthPlace"),
                "tags": row.get("tags", []),
            }
        )

    verify_url = "https:///verify"
    body = {
        "apikey": hub_api_key,
        "task": "people",
        "answer": answer_payload,
    }

    response = requests.post(verify_url, json=body, timeout=30)
    print("Status verify:", response.status_code)
    print("Odpowiedź verify:", response.text)


if __name__ == "__main__":
    main()
