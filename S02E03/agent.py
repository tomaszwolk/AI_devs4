import json

from config import (
    MAIN_MODEL,
    MAIN_SYSTEM_PROMPT,
    OPENROUTER_API_KEY,
    OPENROUTER_URL,
    TOOLS_SCHEMA,
)
from dotenv import load_dotenv
from openai import OpenAI
from tools import TOOLS_DICT

load_dotenv()

CLIENT: OpenAI = OpenAI(
    base_url=OPENROUTER_URL,
    api_key=OPENROUTER_API_KEY,
)


class MainAgent:
    def __init__(self):
        self.messages = [{"role": "system", "content": MAIN_SYSTEM_PROMPT}]
        # Opcjonalnie: przechowuj aktualny stan skompresowanych logów
        # (żeby agent wiedział, co do tej pory uzbierał)
        self.current_logs_state = ""

    def run(self):
        """Uruchamia główną pętlę agenta."""
        print("Rozpoczynam pracę Agenta...")

        while True:
            # 1. Wywołaj model OpenAI (MAIN_MODEL)
            # z obecną listą self.messages i TOOLS_SCHEMA
            response = CLIENT.chat.completions.create(
                model=MAIN_MODEL,  # type: ignore
                messages=self.messages,  # type: ignore
                tools=TOOLS_SCHEMA,  # type: ignore
                tool_choice="auto",
            )

            # 2. Zapisz odpowiedź asystenta do historii
            msg = response.choices[0].message
            self.messages.append(msg)  # type: ignore

            # 3. Jeśli asystent chce wywołać narzędzie (Tool Call):
            #   - Zidentyfikuj, którą funkcję z pliku tools.py wywołać
            #   - Wykonaj ją w Pythonie, przekazując argumenty z LLM
            #   - Dodaj wynik działania funkcji jako nową wiadomość
            #   - Kontynuuj pętlę (continue)
            res = None
            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_name = tool_call.function.name  # type: ignore
                    args = json.loads(tool_call.function.arguments)  # type: ignore

                    print(f"Tool call: {tool_name} with args: {args}\n")
                    try:
                        res = TOOLS_DICT[tool_name](**args)
                        # if args else TOOLS_DICT[tool_name]()
                    except Exception as e:
                        print(f"Error calling tool {tool_name}: {e}")
                        res = f"Error calling tool {tool_name}: {e}"

                    print(f"Tool response: {res}\n")
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
                print(f">>> Zdobyto flagę <<< {res}")
                return

            # 5. (Opcjonalny krok bezpieczeństwa)
            #   Zabezpiecz się przed nieskończoną pętlą
            if len(self.messages) > 30:
                print("Przekroczono limit iteracji")
                break
