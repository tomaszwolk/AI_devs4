import logging
from config import DATA_PATH
from tools import (
    process_files,
    evaluate_fragment_with_llm,
    send_verify_answer,
    evaluate_full_note_with_llm,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    # Process files and find anomalies
    anomalies_ids, unique_notes, file_notes_mapping = process_files(DATA_PATH)

    fragment_cache = {}
    bad_notes_set = set()

    for note in unique_notes:
        # Rozbijamy notatkę na fragmenty i usuwamy spacje z brzegów
        fragments = [f.strip() for f in note.split(",")]

        is_note_bad = False

        for frag in fragments:
            # Pytamy LLM tylko o fragmenty, których jeszcze nie znamy!
            if frag not in fragment_cache:
                fragment_cache[frag] = evaluate_fragment_with_llm(frag)

            # Jeśli jakikolwiek fragment notatki to ERROR,
            # cała notatka jest zgłoszeniem błędu
            if fragment_cache[frag] == "ERROR":
                is_note_bad = True
                break  # Nie sprawdzamy reszty fragmentów w tym zdaniu

        if is_note_bad:
            bad_notes_set.add(note)

    logger.info(f"Wygenerowano cache dla {len(fragment_cache)} unikalnych fragmentów.")
    logger.info(f"Znaleziono {len(bad_notes_set)} notatek zgłaszających błąd.")

    # Etap 2: Ocena całej notatki
    confirmed_bad_notes = set()
    for note in bad_notes_set:
        full_note_result = evaluate_full_note_with_llm(note)
        if full_note_result == "ERROR":
            confirmed_bad_notes.add(note)

    logger.info(
        f"Zakończono etap 2. \
        Znaleziono {len(confirmed_bad_notes)} notatek zgłaszających błąd."
    )

    # Łączymy wyniki
    for file_id, note in file_notes_mapping.items():
        if note in confirmed_bad_notes:
            anomalies_ids.add(file_id)

    recheck = list(anomalies_ids)
    logger.info(f"Re-check: {recheck}")
    response = send_verify_answer(recheck)
    logger.info(f"Response: {response}")


if __name__ == "__main__":
    main()
