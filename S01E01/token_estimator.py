import os
from pathlib import Path

import pandas as pd
import tiktoken
from dotenv import load_dotenv

from llm_config import TAGS, get_system_content, get_user_content_batch


def count_tokens_for_model(model: str, text: str) -> int:
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))


def main() -> None:
    load_dotenv()

    # Model jak w .env (np. openai/gpt-4o-mini) – do tiktoken używamy nazwy openai'owej
    model_id = os.getenv("MODEL_ID", "openai/gpt-4o-mini")
    # Jeśli w .env jest nazwa w stylu "openai/gpt-4o-mini", tiktoken oczekuje "gpt-4o-mini"
    model_for_tiktoken = model_id.split("/", 1)[-1]

    base_path = Path(__file__).parent
    people_filtered_path = base_path / "data" / "people_filtered.csv"

    if not people_filtered_path.exists():
        raise FileNotFoundError(
            f"Nie znaleziono pliku {people_filtered_path}. Uruchom najpierw main.py, aby go wygenerować."
        )

    df = pd.read_csv(people_filtered_path, sep=";")

    # Ile wierszy chcesz testowo brać do batcha
    batch_size = 10
    jobs = df["job"].astype(str).tolist()[:batch_size]

    system_content = get_system_content(TAGS, batch=True)
    jobs_text = "\n".join(f"{i}: {job}" for i, job in enumerate(jobs))
    user_content = get_user_content_batch(jobs_text)

    system_tokens = count_tokens_for_model(model_for_tiktoken, system_content)
    user_tokens = count_tokens_for_model(model_for_tiktoken, user_content)
    total_tokens = system_tokens + user_tokens

    print(f"Model (tiktoken): {model_for_tiktoken}")
    print(f"Liczba opisów w batchu: {len(jobs)}")
    print(f"Tokeny w system_content: {system_tokens}")
    print(f"Tokeny w user_content:   {user_tokens}")
    print(f"Suma tokenów (system + user): {total_tokens}")

    if jobs:
        avg_per_job = user_tokens / len(jobs)
        print(f"Średnio tokenów user_content na jeden opis job: ~{avg_per_job:.2f}")


if __name__ == "__main__":
    main()
