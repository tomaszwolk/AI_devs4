import os
from dotenv import load_dotenv
from helper import create_send_payload, reset_prompt, get_data
from openai import OpenAI
from config import SYSTEM_PROMPT, TOOLS
import json


def main():
    load_dotenv()

    # Stwórz folder data/ jeśli nie istnieje
    if not os.path.exists("data"):
        os.makedirs("data")
    # Pobierz dane z hubu
    data = get_data()
    print(data)

    client = OpenAI(
        base_url=os.getenv("OPENROUTER_URL"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    user_prompt = """
        Pobierz dane z hubu i wyślij prompt do hubu w celu klasyfikacji.
        """
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    for i in range(25):
        print(f"Iteration: {i}")
        response = client.chat.completions.create(
            model=os.getenv("STRONG_MODEL_ID"),
            messages=messages,
            tools=TOOLS,
            temperature=0,
        )

        if response.choices[0].message.tool_calls:
            msg = response.choices[0].message
            messages.append(msg)

            for tool_call in msg.tool_calls:
                print(f"Tool call: {tool_call}\n")
                args = json.loads(tool_call.function.arguments)
                print(f"Args: {args}\n")
                tool_name = tool_call.function.name
                if tool_name == "create_send_payload":
                    res = create_send_payload(**args)
                elif tool_name == "reset_prompt":
                    res = reset_prompt()
                elif tool_name == "get_data":
                    res = get_data()
                else:
                    raise ValueError(f"Unknown function: {tool_name}")
                print(f"Response: {res}\n")
                if tool_name == "get_data":
                    content = res
                else:
                    content = json.dumps(res)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": content,
                    }
                )
        else:
            print(f"Response: {response.choices[0].message.content}")
            break

    print(f"Messages: {messages}")

    # for index, row in df.iterrows():
    #     print(f"Processing item {index}, ID: {row['code']}")
    #     print(f"Opis: {row['description']}")
    #     prompt = f"Classify if item is dangerous DNG or NEU. \
    #         Return only classification. \
    #         ID {row['code']}. Description {row['description']}."
    #     payload = create_payload(prompt)
    #     status_code, response = send_payload(payload)
    #     print(f"Status code: {status_code}")
    #     print(f"Response: {response}")

    # # reset prompt
    # print("Resetting prompt")
    # payload = create_payload("reset")
    # status_code, response = send_payload(payload)
    # print(f"Status code: {status_code}")
    # print(f"Response: {response}")


if __name__ == "__main__":
    main()
