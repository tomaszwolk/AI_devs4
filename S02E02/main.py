from dotenv import load_dotenv
import os
from helper import get_image, rotate_field, reset_board
from openai import OpenAI
from config import SYSTEM_PROMPT, TOOLS
import json

load_dotenv()
HUB_API_KEY = os.getenv("HUB_API_KEY")
ELECTRICITY_URL = f"https:///data/{HUB_API_KEY}/electricity.png"
SOLVED_ELECTRICITY_URL = "https:///i/solved_electricity.png"
MODEL_ID = os.getenv("MODEL_ID")


def main():
    client = OpenAI(
        base_url=os.getenv("BASE_URL"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    image_data_current = get_image(ELECTRICITY_URL)
    image_data_solved = get_image(SOLVED_ELECTRICITY_URL)

    messages = [{
        "role": "system",
        "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Oto aktualny stan planszy (pierwszy obraz) oraz docelowy stan rozwiązania (drugi obraz). Porównaj je, opisz różnice dla każdego pola, a następnie wykonaj niezbędne obroty."},
                {"type": "image_url", "image_url": {"url": image_data_current}},
                {"type": "image_url", "image_url": {"url": image_data_solved}}
            ]
        }
    ]

    print(f"Starting main loop. Model: {MODEL_ID}")
    for i in range(15):
        print(f"Iteration: {i}")
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            tools=TOOLS,
            temperature=0,
        )

        if response.choices[0].message.tool_calls:
            msg = response.choices[0].message
            messages.append(msg)

            for tool_call in msg.tool_calls:
                args = json.loads(tool_call.function.arguments)
                tool_name = tool_call.function.name
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

                tool_content = res if isinstance(res, str) else json.dumps(res, ensure_ascii=False)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content,
                    }
                )
    print(f"Messages: {messages}")


if __name__ == "__main__":
    main()
    # reset_board()
