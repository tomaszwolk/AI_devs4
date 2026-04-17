import logging
import sys

from agent import MainAgent
from config import MAIN_MODEL, MAIN_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def main():
    user_prompt = "Rozpocznij zadanie"
    if not MAIN_MODEL:
        raise ValueError("MAIN_MODEL is not set")
    agent = MainAgent(model=MAIN_MODEL, system_prompt=MAIN_SYSTEM_PROMPT)
    try:
        agent.run(user_prompt)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
