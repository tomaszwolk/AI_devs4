import json
import logging
import sys

from agent import MainAgent
from config import MAIN_MODEL, MAIN_SYSTEM_PROMPT
from tools import send_command

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    # Wysyłamy na początek komendę start do API reaktora
    response = send_command("start")
    print(json.dumps(response, ensure_ascii=False))
    if response.get("code") != 100:
        logger.error(f"Error: {response.get('message')}")
        sys.exit(1)

    board_json = json.dumps(response, ensure_ascii=False)
    user_prompt = (
        f"""Zacznij zadanie. Postępuj zgodnie z instrukcjami systemowymi.
        Początkowy stan planszy: {board_json}"""
    )
    agent = MainAgent(model=MAIN_MODEL, system_prompt=MAIN_SYSTEM_PROMPT)
    try:
        agent.run(user_prompt)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
