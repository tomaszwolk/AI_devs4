import logging
import textwrap
import os
import json
import sys
from config import settings
from agent import SpecializedAgent
from tools import (
    download_data, call_verify_api, BACKEND_TOOLS_DICT,
    FRONTEND_TOOLS_DICT,
)

logger = logging.getLogger(__name__)


def main():
    if not os.path.exists("data/timetravel.md"):
        logger.info("Downloading timetravel data...")
        download_data()
    if not os.path.exists("data/help.json"):
        logger.info("Downloading help data...")
        response = call_verify_api(answer_payload={"action": "help"})
        with open("data/help.json", "w", encoding="utf-8") as f:
            json.dump(json.loads(response), f, indent=4)

    # Odczytanie dokumentacji do zmiennej
    try:
        with open("data/timetravel.md", "r", encoding="utf-8") as f:
            documentation_content = f.read()
    except Exception as e:
        logger.error(f"Nie udało się wczytać dokumentacji: {e}")
        sys.exit(1)

    FULL_BACKEND_PROMPT = f"{settings.backend_system_prompt}\n\n\
        --- DOKUMENTACJA URZĄDZENIA ---\n{documentation_content}"

    backend_agent = SpecializedAgent(
        model=settings.main_model,
        name="backend",
        system_prompt=FULL_BACKEND_PROMPT,
        tools_schema=settings.backend_tools_schema,
        tools_dict=BACKEND_TOOLS_DICT,
    )
    frontend_agent = SpecializedAgent(
        model=settings.main_model,
        name="frontend",
        system_prompt=settings.frontend_system_prompt,
        tools_schema=settings.frontend_tools_schema,
        tools_dict=FRONTEND_TOOLS_DICT,
    )

    # Orkiestrator zarządza kto zaczyna
    current_turn = "backend"

    # bonus mission prompt
    current_message = textwrap.dedent("""
        ZACZYNAMY MISJĘ BONUSOWĄ (Back to the Future). Twoim zadaniem jest wykonanie 4 skoków w czasie w ścisłej kolejności. 
        Dla każdego skoku wykonuj twardą procedurę: standby -> konfiguracja API (oblicz syncRatio, pobierz PWR i tryb) -> ui state -> timeTravel.
        Zawsze po udanym skoku wchodź w tryb 'standby' dla kolejnego.

        Oto lista celów do odwiedzenia po kolei:
        1. Najpierw zdobądź nowe baterie. Data: 5 listopada 2238.
        2. Następnie skocz do daty z artykułu o zegarze na ratuszu. Data: 12 listopada 1955.
        3. Potem wróć do początku filmowej historii. Data: 26 października 1985.
        4. Na końcu leć po almanach sportowy. Data: 21 października 2015.

        Po każdym udanym skoku, wiesz w jakim jesteś roku. Na tej podstawie sam zdecyduj, czy następny skok jest w przyszłość (PTB=True) czy w przeszłość (PTA=True).
        Wszystkie podróże to zwykłe skoki, NIE używaj trybu tunelu. Powodzenia!
    """).strip()

    call_verify_api(answer_payload={"action": "reset"})

    agents = {
        "backend": backend_agent,
        "frontend": frontend_agent,
    }

    mission_running = True

    while mission_running:
        active_agent = agents[current_turn]
        status, next_turn, output_msg = active_agent.run_turn(current_message)

        if status == "SUCCESS":
            logger.info("Misja zakończona sukcesem!")
            mission_running = False
            break

        elif status == "HANDOFF":
            current_turn = next_turn
            current_message = (
                f"[{active_agent.name.upper()}] przekazuje kontrolę:\n\
                {output_msg}")

        elif status == "ERROR":
            logger.error("Błąd w trakcie przetwarzania.")
            mission_running = False


if __name__ == "__main__":
    main()
