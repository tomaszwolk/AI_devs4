import json
import logging
from openai import OpenAI
from dotenv import load_dotenv

from tools import TOOLS_DICT
from config import TOOLS_SCHEMA, OPENROUTER_API_KEY, OPENROUTER_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

CLIENT: OpenAI = OpenAI(
    base_url=OPENROUTER_URL,
    api_key=OPENROUTER_API_KEY,
)


class MainAgent:
    def __init__(self, model: str, system_prompt: str):
        self.messages = [{"role": "system", "content": system_prompt}]
        self.model = model

    def run(self, user_prompt: str, additional_messages: list[dict] = None):
        """Uruchamia główną pętlę agenta."""
        logger.info("Rozpoczynam pracę Agenta...")
        self.messages.append({"role": "user", "content": user_prompt})
        if additional_messages:
            self.messages.extend(additional_messages)

        iteration = 0
        while iteration < 30:
            iteration += 1
            logger.info(f"Iteration: {iteration}")

            # 1. Wywołaj model OpenAI
            response = CLIENT.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
            )

            # 2. Zapisz odpowiedź asystenta do historii
            msg = response.choices[0].message
            self.messages.append(msg)

            if not msg.tool_calls:
                logger.info(f"Odpowiedź asystenta: {msg.content}")
                # Żeby uniknąć nieskończoną pętlę
                self.messages.append(
                    {
                        "role": "user",
                        "content": "Kontynuuj działanie używając dostępnych narzędzi, aż zdobędziesz flagę {FLG:...}.",
                    }
                )
                continue

            # 3. Wykonywanie narzędzi
            for tool_call in msg.tool_calls:
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                logger.info(f"Tool call: {tool_name} with args: {args}\n")
                try:
                    res = TOOLS_DICT[tool_name](**args)
                except Exception as e:
                    logger.error(f"Error calling tool {tool_name}: {e}")
                    res = f"Error calling tool {tool_name}: {str(e)}"

                logger.info(f"Tool response: {res}\n")
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(res),
                    }
                )

            # 4. Sprawdzenie flagi
            if "FLG:" in str(res):
                logger.info(f">>> Zdobyto flagę <<< {res}")
                logger.info(f"Messages: {self.messages}")
                return

        # 5. Zabezpieczenie przed nieskończoną pętlą
        logger.error("Przekroczono limit iteracji")
        logger.error(f"Messages: {self.messages}")
        return
