import json
import logging
import os
import textwrap
from openai import OpenAI
from dotenv import load_dotenv

from tools import TOOLS_DICT
from config import TOOLS_SCHEMA, OPENROUTER_API_KEY, BASE_URL, LOGS_DIR_PATH

os.makedirs(LOGS_DIR_PATH, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            LOGS_DIR_PATH / "agent_logs.log",
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

load_dotenv()

CLIENT: OpenAI = OpenAI(
    base_url=BASE_URL,
    api_key=OPENROUTER_API_KEY,
)


def _assistant_message_to_dict(msg) -> dict:
    """ChatCompletionMessage nie jest serializowalny przez json.dump
    konwersja do dict."""
    if hasattr(msg, "model_dump"):
        return msg.model_dump()
    # Starsze wersje SDK / obiekty bez model_dump
    d: dict = {"role": "assistant", "content": msg.content}
    if getattr(msg, "tool_calls", None):
        d["tool_calls"] = [
            {
                "id": tc.id,
                "type": getattr(tc, "type", "function") or "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in msg.tool_calls
        ]
    return d


class MainAgent:
    def __init__(self, model: str, system_prompt: str):
        self.messages = [{"role": "system", "content": system_prompt}]
        self.model = model

    def save_history(self, filename="history.json"):
        """Zapisuje całą historię rozmowy do ładnego pliku JSON."""
        filepath = LOGS_DIR_PATH / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.messages, f, indent=4, ensure_ascii=False)
        logger.info(f"Historia konwersacji zapisana do {filename}")

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
            # (jako dict — JSON + kolejne wywołania API)
            msg = response.choices[0].message
            self.messages.append(_assistant_message_to_dict(msg))

            if not msg.tool_calls:
                logger.info(f"Odpowiedź asystenta: {msg.content}")
                # Żeby uniknąć nieskończoną pętlę
                self.messages.append(
                    {
                        "role": "user",
                        "content": textwrap.dedent("""
                        Kontynuuj działanie używając dostępnych narzędzi,
                        aż zdobędziesz flagę {FLG:...}.""").strip(),
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
                tool_content = (
                    json.dumps(res, ensure_ascii=False)
                    if isinstance(res, (dict, list))
                    else str(res)
                )
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content,
                    }
                )

            # 4. Sprawdzenie flagi
            res_for_flag = (
                json.dumps(res, ensure_ascii=False)
                if isinstance(res, (dict, list))
                else str(res)
            )
            if "FLG:" in res_for_flag:
                logger.info(f">>> Zdobyto flagę <<< {res}")
                self.save_history("success_history.json")
                return

        # 5. Zabezpieczenie przed nieskończoną pętlą
        logger.error("Przekroczono limit iteracji")
        self.save_history("failed_history.json")
        return
