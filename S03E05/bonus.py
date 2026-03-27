from tools import tool_call, verify_answer
import sys
from pprint import pprint
import json


def main():
    # Uruchom uv run bonus.py
    # Wyśle narzędzia do centrali. Potem zobacz na /debug
    query = sys.argv[2]
    tool = sys.argv[1]

    if tool == "verify":
        query_list = query.split(",")
        print(query_list)
        response = verify_answer(query_list)
        pprint(json.loads(response))
        sys.exit(0)
    response = tool_call(query, tool)
    pprint(json.loads(response))

    sys.exit(0)


if __name__ == "__main__":
    main()
