import requests
import json
import io
import contextlib
import traceback

from config import API_KEY, TASK, VERIFY_URL, API_BASE_URL, HUB_ORIGIN


def tool_call(query: str, tool: str) -> str:
    """
    Call a tool.
    """
    payload = {
            "apikey": API_KEY,
            "query": query,
        }

    if tool.startswith("/api"):
        url = HUB_ORIGIN + tool
    else:
        url = API_BASE_URL + tool.lstrip("/")

    response = requests.post(url, json=payload)
    return json.dumps(response.json())


def verify_answer(answer: list[str]) -> str:
    """
    Verify the answer.
    """
    payload = {
            "apikey": API_KEY,
            "task": TASK,
            "answer": answer,
        }
    response = requests.post(VERIFY_URL, json=payload)
    return json.dumps(response.json())


def execute_python_code(code: str) -> str:
    """
    Executes Python code dynamically and captures stdout (print statements).
    """
    # Strumień wyjściowy, do którego "wpadną" wszystkie printy ze skryptu LLMa
    f = io.StringIO()

    with contextlib.redirect_stdout(f):
        try:
            # Uruchamiamy kod z pustym środowiskiem globalnym
            exec(code, {})
        except Exception:
            # Jeśli LLM popełni błąd w kodzie, zwracamy mu traceback, żeby sam go naprawił!
            error_msg = f"Execution Error:\n{traceback.format_exc()}"
            return error_msg

    output = f.getvalue()
    if not output.strip():
        return "Success, but no output. Make sure to use print() to output the final path array."
    return output


TOOLS_DICT = {
    "tool_call": tool_call,
    "verify_answer": verify_answer,
    "execute_python_code": execute_python_code,
}
