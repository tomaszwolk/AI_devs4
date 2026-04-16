from agent import MainAgent
from config import (
    MAIN_MODEL, MAIN_SYSTEM_PROMPT, POWER_STATION_ID,
    DRONE_INSTRUCTIONS_PATH, POWER_STATION_MAP_URL
)


def main():
    with open(DRONE_INSTRUCTIONS_PATH, "r") as file:
        DRONE_INSTRUCTIONS = file.read()

    user_prompt = (f"""Wyślij drona do elektrowni, na podstawie mapy ustal koordynaty.
    Na podstawie dokumentacji API drona wykonaj odpowiednie instrukcje.
    - lokalizacja elektrowni (cel misji): {POWER_STATION_ID}
    - dokumentacja API drona: {DRONE_INSTRUCTIONS}
    - link do obrazu z mapą podzieloną na siatkę: {POWER_STATION_MAP_URL}
    """).strip()

    agent = MainAgent(model=MAIN_MODEL, system_prompt=MAIN_SYSTEM_PROMPT)
    try:
        agent.run(user_prompt)
    except Exception as e:
        print(f"Wystąpił błąd krytyczny: {e}")


if __name__ == "__main__":
    main()
