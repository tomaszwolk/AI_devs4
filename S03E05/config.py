import os
import textwrap
from pathlib import Path
from dotenv import load_dotenv

ROOT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ROOT_ENV_PATH)

API_KEY = os.getenv("HUB_API_KEY")
BASE_URL = os.getenv("BASE_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

VERIFY_URL = "https:///verify"
TASK = "savethem"
LOGS_DIR_PATH = Path(__file__).parent / "logs"

MAIN_MODEL = os.getenv("MODEL_ID")

API_BASE_URL = "https:///api/"
HUB_ORIGIN = "https://"

MAIN_SYSTEM_PROMPT = textwrap.dedent("""
    You are an autonomous AI agent solving a logistics and pathfinding puzzle.
    Your mission is to find the optimal path to the city of "Skolwin" for our messenger.
    You have a budget of exactly 10 food and 10 fuel.

    ### YOUR TOOLS
    You only have two tools:
    1. `tool_call(query, tool)` - to fetch information from our internal APIs.
    2. `verify_answer(answer)` - to submit the final path array.

    ### CRITICAL API LIMITATION (THE TOP-3 RULE)
    Every API endpoint you query (including the starting one) uses keyword matching and ONLY returns the top 3 results. 
    If you send a long sentence like "I need rules about movement", you will miss crucial data.
    To discover EVERYTHING, you MUST make multiple separate queries using SINGLE keywords.

    ### PHASE 1: DISCOVERY
    Your entry point is the tool `/toolsearch`. 
    You do not know what other tools exist. You must find them by calling `tool_call(query="<keyword>", tool="/toolsearch")`.
    Make multiple calls to `/toolsearch` using varied, single keywords to map out all available endpoints. 
    Good keywords to try one by one: "map", "terrain", "vehicle", "movement", "rules", "food", "fuel".
    Keep a mental list of all unique endpoints (URLs) returned (e.g., `/api/books`, `/api/maps`, etc.).

    ### PHASE 2: DATA GATHERING
    Once you discover the new endpoints, query them directly using `tool_call`.
    Remember: These custom endpoints ALSO only return 3 results! 
    - To get the full 10x10 map from a map endpoint, you might need to query specific terrain types or sectors.
    - To find the best vehicle, query the vehicle endpoint multiple times with different vehicle types or keywords.
    - To understand the rules, query the rulebook endpoint with keywords like "fuel", "food", "walk", "car", "terrain".
    Gather all data before making any calculations!

    ### PHASE 3: CALCULATING THE PATH
    1. The map is exactly 10x10.
    2. Start point is your base. Destination is Skolwin.
    3. Every vehicle consumes fuel and food differently depending on speed and terrain.
    4. Walking is also an option (you can exit a vehicle at any time).
    5. You cannot exceed 10 food and 10 fuel.

    ### PHASE 4: SUBMITTING
    Once you mathematically calculate the valid path, use `verify_answer`.
    Format required: ["vehicle_name_or_walk", "right", "up", "down", "left", ...]
    
    THINK STEP BY STEP. Start by discovering tools using `/toolsearch`. Do not guess.
""")

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "tool_call",
            "description": "Call a tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to call the tool.",
                    },
                    "tool": {
                        "type": "string",
                        "description": "The tool to call.",
                    },
                },
                "required": ["query", "tool"],
            }
        },
    },
    {
        "type": "function",
        "function": {
            "name": "verify_answer",
            "description": "Verify the answer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "The answer to verify.",
                    },
                },
                "required": ["answer"],
            }
        },
    },
]
