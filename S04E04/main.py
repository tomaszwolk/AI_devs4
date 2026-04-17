import json
import logging
import sys

from agent import MainAgent
from config import settings

logger = logging.getLogger(__name__)


def main():
    if not settings.main_model:
        raise ValueError("MAIN_MODEL is not set")
    agent = MainAgent(
        model=settings.main_model, system_prompt=settings.main_system_prompt
    )

    with open("data/help.json", "r") as f:
        help_data = json.load(f)
    with open("data/natan_notes/ogłoszenia.txt", "r") as f:
        ogłoszenia_data = f.read()
    with open("data/natan_notes/rozmowy.txt", "r") as f:
        rozmowy_data = f.read()
    with open("data/natan_notes/transakcje.txt", "r") as f:
        transakcje_data = f.read()

    user_prompt = (
        f"""
    Rozpocznij wykonanie zadania.
    - informacje o dostępnych akcjach i parametrach są opisane w {help_data}.
    - wzmianki o zapotrzebowaniu różnych miast spisane z kartek znalezionych przy Natanie są opisane w {ogłoszenia_data}.
    - Natan spisywał z kim i o czym rozmawiał w {rozmowy_data}.
    - informacje, które miasto sprzedało jaki towar innemu miastu są zapisane w {transakcje_data}.
    """
    ).strip()

    try:
        agent.run(user_prompt)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
