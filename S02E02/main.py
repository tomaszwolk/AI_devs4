import json
import os

from config import SYSTEM_PROMPT, TOOLS, USER_PROMPT
from dotenv import load_dotenv
from helper import get_image, reset_board, rotate_field, save_messages_to_file
from openai import OpenAI

load_dotenv()
HUB_API_KEY = os.getenv("HUB_API_KEY")
HUB_URL = os.getenv("BASE_URL")
ELECTRICITY_URL = f"{HUB_URL}/data/{HUB_API_KEY}/electricity.png"
SOLVED_ELECTRICITY_URL = f"{HUB_URL}/i/solved_electricity.png"
MODEL_ID = os.getenv("VISION_MODEL_ID")
if not MODEL_ID:
    raise ValueError("VISION_MODEL_ID is not set")


def main():
    client = OpenAI(
        base_url=os.getenv("OPENROUTER_URL"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    image_data_current = get_image(ELECTRICITY_URL)
    image_data_solved = get_image(SOLVED_ELECTRICITY_URL)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": USER_PROMPT.format(ELECTRICITY_URL=ELECTRICITY_URL),
                },
                {"type": "image_url", "image_url": {"url": image_data_current}},
                {"type": "image_url", "image_url": {"url": image_data_solved}},
            ],
        },
    ]

    print(f"Starting main loop. Model: {MODEL_ID}")
    for i in range(15):
        print(f"Iteration: {i}")
        response = client.chat.completions.create(
            model=MODEL_ID,  # type: ignore
            messages=messages,
            tools=TOOLS,  # type: ignore
            temperature=0,
        )

        if response.choices[0].message.tool_calls:
            msg = response.choices[0].message
            messages.append(msg)

            for tool_call in msg.tool_calls:  # type: ignore
                args = json.loads(tool_call.function.arguments)  # type: ignore
                tool_name = tool_call.function.name  # type: ignore
                print(f"\nTool call: {tool_name}")
                print(f"Args: {args}")
                if tool_name == "rotate_field":
                    res = rotate_field(**args)
                elif tool_name == "reset_board":
                    res = reset_board()
                elif tool_name == "get_image":
                    res = get_image(**args)
                else:
                    raise ValueError(f"Unknown function: {tool_name}")

                tool_content = (
                    res if isinstance(res, str) else json.dumps(res, ensure_ascii=False)
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content,
                    }
                )
    save_messages_to_file(messages)


if __name__ == "__main__":
    main()
    # reset_board()
