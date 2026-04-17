import json
import logging
import sys

from agent import MainAgent
from config import settings
from tools import call_verify_api

logger = logging.getLogger(__name__)


def main():
    if not settings.main_model:
        raise ValueError("MAIN_MODEL is not set")
    agent = MainAgent(
        model=settings.main_model, system_prompt=settings.main_system_prompt
    )

    windpower_help = call_verify_api(answer_payload={"action": "help"})

    user_prompt = (
        f"""Użyj narzędzia call_verify_api aby uzyskać informacje o dostępnych akcjach i parametrach.
    Parametry są opisane w {json.loads(windpower_help)["actions"]}.
    """
    ).strip()

    try:
        agent.run(user_prompt, interactive=False)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
