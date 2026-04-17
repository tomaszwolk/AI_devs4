import json
import os
from pathlib import Path

import pandas as pd
from config import SYSTEM_PROMPT, TOOLS
from dotenv import load_dotenv
from helper import (
    create_report,
    get_access_level,
    get_closest_power_plant,
    get_person_locations,
    get_power_plants_data,
    get_save_data_from_hub,
    send_report,
)
from openai import OpenAI

load_dotenv()
hub_api_key = os.getenv("HUB_API_KEY")
if not hub_api_key:
    raise ValueError("HUB_API_KEY is not set")
client = OpenAI(
    base_url=os.getenv("OPENROUTER_URL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
)
# Pobieranie danych osób i elektrowni
people_path = Path(__file__).parent / "data" / "people_transport.csv"
df = pd.read_csv(people_path, sep=";")
plants_path = Path(__file__).parent / "data" / "findhim_locations.json"
plants = get_save_data_from_hub(hub_api_key, plants_path.name)


def extract_birth_year(value: str) -> int:
    parsed = pd.to_datetime(value)
    if isinstance(parsed, pd.Timestamp):
        return int(parsed.year)
    raise ValueError(f"Invalid birthDate value: {value!r}")


# Tworzenie listy osób
people = [
    {
        "name": row["name"],
        "surname": row["surname"],
        "birthYear": extract_birth_year(str(row["birthDate"])),
    }
    for _, row in df.iterrows()
]

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {
        "role": "user",
        "content": f"Osoby do sprawdzenia: {people}. Elektrownie: {plants}. Znajdź osobę, która była najbliżej dowolnej elektrowni z dostarczonej listy.",
    },
]
model = os.getenv("MODEL_ID")
if not model:
    raise ValueError("MODEL_ID is not set")
for i in range(25):
    print(f"Iteration: {i}")
    response = client.chat.completions.create(
        model=model,
        messages=messages,  # type: ignore
        tools=TOOLS,  # type: ignore
        temperature=0,
    )

    if response.choices[0].message.tool_calls:
        msg = response.choices[0].message
        print(f"Msg: {msg}\n")
        messages.append(msg)  # type: ignore
        print(f"Msg tool calls: {msg.tool_calls}\n")
        for tool_call in msg.tool_calls:  # type: ignore
            print(f"Tool call: {tool_call}\n")
            args = json.loads(tool_call.function.arguments)  # type: ignore
            print(f"Args: {args}\n")
            tool_name = tool_call.function.name.split("<")[0]  # type: ignore
            if tool_name == "get_person_locations":
                res = get_person_locations(**args)
            elif tool_name == "get_access_level":
                res = get_access_level(**args)
            elif tool_name == "get_closest_power_plant":
                res = get_closest_power_plant(**args)
            elif tool_name == "get_power_plants_data":
                res = get_power_plants_data()
            else:
                raise ValueError(f"Unknown function: {tool_name}")
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(res),
                }
            )
    else:
        print(f"\nResponse content: {response.choices[0].message.content}")
        print(f"\nResponse: {response}")
        break

report_data = json.loads(response.choices[0].message.content)  # type: ignore
report = create_report(
    hub_api_key,
    "findhim",
    report_data["name"],
    report_data["surname"],
    report_data["access_level"],
    report_data["closest_plant"]["code"],
)
print(f"Report: {report}")
status_code, response = send_report(report)

print(f"Status code: {status_code}")
print(f"Response: {response}")
