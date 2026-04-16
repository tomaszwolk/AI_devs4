import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ROOT_ENV_PATH)

API_KEY = os.getenv("HUB_API_KEY")
OPENROUTER_URL = os.getenv("OPENROUTER_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
HUB_URL = os.getenv("HUB_URL")

VERIFY_URL = HUB_URL + "/verify"
TASK = "evaluation"

DATA_PATH = Path(__file__).parent / "data" / "sensors"
BAD_SENSORS_PATH = Path(__file__).parent / "data" / "bad_sensors"
GOOD_SENSORS_PATH = Path(__file__).parent / "data" / "good_sensors"

MAIN_MODEL = os.getenv("NANO_MODEL_ID")

MAIN_SYSTEM_PROMPT = """

"""

TOOLS_SCHEMA = [
]

RANGES = {
    "temperature": ("temperature_K", 553, 873),
    "pressure": ("pressure_bar", 60, 160),
    "water": ("water_level_meters", 5.0, 15.0),
    "voltage": ("voltage_supply_v", 229.0, 231.0),
    "humidity": ("humidity_percent", 40.0, 80.0)
}
