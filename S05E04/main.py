import sys
import logging
import textwrap
from config import settings
from agent import MainAgent

logger = logging.getLogger(__name__)


def main():
    agent = MainAgent(model=settings.main_model, system_prompt=settings.system_prompt, max_iterations=100)

    user_prompt = textwrap.dedent("""
    Rozpocznij wykonanie zadania.
    """).strip()

    try:
        agent.run(user_prompt)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
