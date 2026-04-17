"""
Konfiguracja LLM: wczytuje prompty i opisy tagów z llm_prompts.md.

Udostępnia schematy JSON (Structured Output) i gotowe wiadomości.
"""

from pathlib import Path

_PROMPTS_PATH = Path(__file__).parent / "llm_prompts.md"


def _load_sections() -> dict[str, str]:
    text = _PROMPTS_PATH.read_text(encoding="utf-8")
    sections: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_key is not None:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = line[3:].strip().lower()
            current_lines = []
        elif current_key is not None:
            current_lines.append(line)

    if current_key is not None:
        sections[current_key] = "\n".join(current_lines).strip()
    return sections


def _parse_tag_descriptions(content: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in content.splitlines():
        line_stripped = line.strip()
        if not line_stripped or ":" not in line_stripped:
            continue
        key, _, val = line_stripped.partition(":")
        key, val = key.strip(), val.strip()
        # pomiń linie opisowe (np. "Opisy tagów..." lub "Format: ...")
        if not key or key.startswith("Opisy") or "." in key or "Format" in key:
            continue
        out[key] = val
    return out


def _parse_tags_list(content: str) -> list[str]:
    tags: list[str] = []
    for line in content.splitlines():
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith(("Kolejność", "Używane")):
            continue
        tags.append(line_stripped)
    return tags


def load_prompts() -> tuple[dict[str, str], list[str], str, str, str, str]:
    """Wczytuje plik .md i zwraca (TAG_DESCRIPTIONS, TAGS, system_prompt, system_prompt_batch, user_single, user_batch)."""
    sections = _load_sections()

    tag_descriptions_content = sections.get("tag descriptions", "")
    tags_content = sections.get("tags", "")

    tag_descriptions = _parse_tag_descriptions(tag_descriptions_content)
    tags_list = _parse_tags_list(tags_content)
    if not tags_list and tag_descriptions:
        tags_list = list(tag_descriptions.keys())

    system_prompt = sections.get("system prompt", "")
    system_prompt_batch = sections.get("system prompt (batch)", system_prompt)
    user_single = sections.get("user prompt (single)", "")
    user_batch = sections.get("user prompt (batch)", "")

    return (
        tag_descriptions,
        tags_list,
        system_prompt,
        system_prompt_batch,
        user_single,
        user_batch,
    )


# Ładowanie przy imporcie
(
    TAG_DESCRIPTIONS,
    TAGS,
    SYSTEM_PROMPT,
    SYSTEM_PROMPT_BATCH,
    USER_PROMPT_SINGLE,
    USER_PROMPT_BATCH,
) = load_prompts()


def get_schema_single_job(tags: list[str]) -> dict:
    """Schemat JSON dla jednego opisu stanowiska (Structured Output)."""
    return {
        "type": "object",
        "properties": {
            "tags": {
                "type": "array",
                "description": "Lista wybranych tagów opisujących ten zawód. Wybierz tylko spośród podanych tagów.",
                "items": {"type": "string", "enum": tags},
            }
        },
        "required": ["tags"],
        "additionalProperties": False,
    }


def get_schema_batch_jobs(tags: list[str]) -> dict:
    """Schemat JSON dla batcha opisów stanowisk (Structured Output)."""
    return {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "index": {
                    "type": "integer",
                    "description": "Indeks opisu stanowiska z listy otrzymanej od użytkownika (0-based).",
                },
                "tags": {
                    "type": "array",
                    "description": "Lista wybranych tagów opisujących dany zawód. Wybierz tylko spośród podanych tagów.",
                    "items": {"type": "string", "enum": tags},
                },
            },
            "required": ["index", "tags"],
            "additionalProperties": False,
        },
    }


def build_tag_descriptions_text(tags: list[str]) -> str:
    """Składa blok tekstu 'tag: opis' do wstrzyknięcia w prompt systemowy."""
    return "\n".join(f"- {tag}: {TAG_DESCRIPTIONS.get(tag, '')}" for tag in tags)


def get_system_content(tags: list[str], *, batch: bool = False) -> str:
    template = SYSTEM_PROMPT_BATCH if batch else SYSTEM_PROMPT
    return template.format(tag_descriptions_text=build_tag_descriptions_text(tags))


def get_user_content_single(job_description: str) -> str:
    return USER_PROMPT_SINGLE.format(job_description=job_description)


def get_user_content_batch(jobs_text: str) -> str:
    return USER_PROMPT_BATCH.format(jobs_text=jobs_text)
