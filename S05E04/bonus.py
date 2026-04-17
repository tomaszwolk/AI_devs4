import json
import sys
from pprint import pprint

from tools import call_verify_api, get_radio_hint, neutralize_trap, scan_frequency


def _print_response(response: str) -> None:
    try:
        data = json.loads(response)
        pprint(data)
    except json.JSONDecodeError:
        print(response)


def main():
    # Uruchom uv run bonus.py query
    # query - start, go, left, right, hint, scan, neutralize(frequency, detectionCode)
    query = sys.argv[1]
    frequency = sys.argv[2] if len(sys.argv) > 2 else None
    detectionCode = sys.argv[3] if len(sys.argv) > 3 else None

    if query in ["start", "go", "left", "right"]:
        cmd_answer = {"command": query}
        response = call_verify_api(answer_payload=cmd_answer)
        _print_response(response)
        sys.exit(0)

    if query == "hint":
        response = get_radio_hint()
        _print_response(response)
        sys.exit(0)

    if query == "scan":
        response = scan_frequency()
        _print_response(response)
        sys.exit(0)

    if query == "neutralize":
        response = neutralize_trap(int(frequency), detectionCode)  # type: ignore
        _print_response(response)
        sys.exit(0)


if __name__ == "__main__":
    main()
