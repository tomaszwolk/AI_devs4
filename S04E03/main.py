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
    with open("data/map.json", "r") as f:
        map_data = json.load(f)

    user_prompt = (
        f"""Rozpocznij wykonanie zadania.
    - informacje o dostępnych akcjach i parametrach są opisane w {help_data}.
    - mapa jest opisana w {map_data}.
    """
    ).strip()

    try:
        agent.run(user_prompt)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
