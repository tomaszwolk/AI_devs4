import sys
import logging
import json
from tools import get_help_data
from config import settings
from agent import MainAgent

logger = logging.getLogger(__name__)


def main():
    agent = MainAgent(
        model=settings.main_model,
        system_prompt=settings.main_system_prompt
    )

    help_data = get_help_data()
    with open("data/food4cities.json", "r") as f:
        food4cities_data = json.load(f)

    user_prompt = (f"""Rozpocznij wykonanie zadania.
    - informacje o dostępnych akcjach i parametrach są opisane w {help_data}.
    - informacje o zamówieniach dla miast są opisane w {food4cities_data}.
    """).strip()

    try:
        agent.run(user_prompt)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
