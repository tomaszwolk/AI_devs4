import logging
import sys

from agent import MainAgent
from config import MAIN_MODEL, MAIN_SYSTEM_PROMPT
from tools import run_shell_command

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    # Na wszeldki wypadek restetujemy maszynę wirtualną na starcie
    run_shell_command("reboot")
    # Pusty user message powoduje błąd 400 u niektórych providerów (Azure):
    # "messages: at least one message is required".
    user_prompt = (
        "Zacznij zadanie. Najpierw uruchom komendę `help` w powłoce, "
        "potem postępuj zgodnie z instrukcjami systemowymi."
    )
    agent = MainAgent(model=MAIN_MODEL, system_prompt=MAIN_SYSTEM_PROMPT)
    try:
        agent.run(user_prompt)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
