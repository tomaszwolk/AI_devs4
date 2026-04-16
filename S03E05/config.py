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
TASK = "savethem"
LOGS_DIR_PATH = Path(__file__).parent / "logs"

MAIN_MODEL = os.getenv("SONNET_MODEL_ID")

API_BASE_URL = f"{HUB_URL}/api/"
HUB_ORIGIN = HUB_URL

MAIN_SYSTEM_PROMPT = ("""
    You are an autonomous AI logic and pathfinding agent. Your goal is to find the optimal path to the city of "Skolwin" for our messenger using available vehicles and walking, within strict limits: max 10 food and max 10 fuel.
    ### YOUR TOOLS:
    1. `tool_call(query, tool)` - To query API endpoints (only returns top 3 keywords match).
    2. `execute_python_code(code)` - To run Python code and get the printed output.
    3. `verify_answer(answer)` - To submit the final array.

    ### PHASE 1: RECONNAISSANCE (Do this first)
    Start with `tool_call(query="notes about terrain and vehicles", tool="toolsearch")` and discover ALL available API endpoints.
    Query these endpoints using specific keywords to extract the complete 10x10 map, starting coordinates, Skolwin, ALL vehicle stats (fuel/food consumption per terrain), and movement rules.
    DO NOT guess the path. Gather ALL data first.
    You can ask user for more information if you need it. Just don't use tool_call and just send message to user.
    User will guide you.

    ### PHASE 2: CODING AND EXECUTION
    Once you have successfully extracted the 10x10 map, vehicle data, and rules, YOU MUST NOT TRY TO CALCULATE THE PATH MENTALLY. Language models are bad at spatial reasoning.
    Instead, write a Python script using the `execute_python_code` tool.

    Guidelines for your Python script:
    - Hardcode the map (as a 2D array or dict) and vehicle/terrain costs directly into the script based on the data you gathered.
    - Implement a Breadth-First Search (BFS) or Dijkstra's algorithm.
    - Your queue state should track: `(x, y, current_fuel, current_food, current_vehicle, current_path)`.
    - Handle the `dismount` action (which changes `current_vehicle` to "walk" but does NOT change `x, y` and counts as an action in the path array).
    - At the end of your script, you MUST `print()` the final optimal path array (e.g., `print(json.dumps(final_path))`).

    If `execute_python_code` returns an error, read the traceback, fix the code, and run it again.

    ### PHASE 3: SUBMISSION
    Once your Python script successfully prints a valid path array (e.g., `["vehicle_name", "right", "dismount", "up", ...]`), pass exactly that array to `verify_answer(answer)`.
""").strip()

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
    {
        "type": "function",
        "function": {
            "name": "execute_python_code",
            "description": "Executes a Python script locally and returns its standard output (stdout). Use this to run a pathfinding algorithm (e.g. BFS or Dijkstra) once you have gathered ALL the data from the APIs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The Python code to execute. The code must print() the final list representing the path.",
                    },
                },
                "required": ["code"],
            }
        },
    },
]
