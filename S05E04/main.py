import logging
import sys

from agent import MainAgent
from config import settings

logger = logging.getLogger(__name__)


def main():
    if not settings.main_model:
        raise ValueError("MAIN_MODEL is not set")
    agent = MainAgent(
        model=settings.main_model,
        system_prompt=settings.system_prompt,
        max_iterations=100,
    )

    user_prompt = ("""Rozpocznij wykonanie zadania.""").strip()

    try:
        agent.run(user_prompt)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
