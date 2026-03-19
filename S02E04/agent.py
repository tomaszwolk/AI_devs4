from openai import OpenAI
from tools import TOOLS_DICT
from config import (
    MAIN_MODEL, MAIN_SYSTEM_PROMPT, TOOLS_SCHEMA,
    OPENROUTER_API_KEY, BASE_URL, BONUS_SYSTEM_PROMPT
)
import json
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

CLIENT: OpenAI = OpenAI(
    base_url=BASE_URL,
    api_key=OPENROUTER_API_KEY,
)


class MainAgent:
    def __init__(self):
        self.messages = [{"role": "system", "content": MAIN_SYSTEM_PROMPT}]
        # Opcjonalnie: przechowuj aktualny stan skompresowanych logów
        # (żeby agent wiedział, co do tej pory uzbierał)
        self.current_logs_state = ""

    def run(self, user_prompt: str):
        """Uruchamia główną pętlę agenta."""
        print("Rozpoczynam pracę Agenta...")
        self.messages.append({"role": "user", "content": user_prompt})

        iteration = 0
        while iteration < 30:
            iteration += 1
            logger.info(f"Iteration: {iteration}")
            # 1. Wywołaj model OpenAI (MAIN_MODEL)
            # z obecną listą self.messages i TOOLS_SCHEMA
            response = CLIENT.chat.completions.create(
                model=MAIN_MODEL,
                messages=self.messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto"
            )

            # 2. Zapisz odpowiedź asystenta do historii
            msg = response.choices[0].message
            self.messages.append(msg)

            if not msg.tool_calls:
                logger.info(f"Response: {msg.content}")
                # Żeby uniknąć nieskończoną pętlę
                self.messages.append({
                    "role": "user",
                    "content": "Kontynuuj wyszukiwanie używając dostępnych \
                    narzędzi, aż zdobędziesz flagę."
                })
                continue

            # 3. Jeśli asystent chce wywołać narzędzie (Tool Call):
            #   - Zidentyfikuj, którą funkcję z pliku tools.py wywołać
            #   - Wykonaj ją w Pythonie, przekazując argumenty z LLM
            #   - Dodaj wynik działania funkcji jako nową wiadomość
            #   - Kontynuuj pętlę (continue)
            for tool_call in msg.tool_calls:
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                logger.info(f"Tool call: {tool_name} with args: {args}\n")
                try:
                    res = TOOLS_DICT[tool_name](**args)
                    # if args else TOOLS_DICT[tool_name]()
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

            # 4. Jeśli w odpowiedzi narzędzia `submit_logs` pojawiła się flaga:
            #   - Wypisz flagę
            #   - break (wyjście z pętli)
            if "FLG:" in str(res):
                logger.info(f">>> Zdobyto flagę <<< {res}")
                logger.info(f"Messages: {self.messages}")
                return

        # 5. (Opcjonalny krok bezpieczeństwa)
        #   Zabezpiecz się przed nieskończoną pętlą
        logger.error("Przekroczono limit iteracji")
        logger.error(f"Messages: {self.messages}")
        return
