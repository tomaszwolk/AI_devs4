import sys
import logging

from config import MAIN_MODEL, MAIN_SYSTEM_PROMPT
from agent import MainAgent

logger = logging.getLogger(__name__)


def main():
    user_prompt = ("Rozpocznij zadanie")
    agent = MainAgent(model=MAIN_MODEL, system_prompt=MAIN_SYSTEM_PROMPT)
    try:
        agent.run(user_prompt)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
