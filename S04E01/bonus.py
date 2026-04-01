from tools import call_oko_editor_api, call_verify_api
import sys
from pprint import pprint
import json


def main():
    # Uruchom uv run bonus.py api "string"
    action = sys.argv[2]
    tool = sys.argv[1]
    page = sys.argv[3]
    record_id = sys.argv[4]
    title = sys.argv[5]
    if tool == "verify":
        response = call_verify_api(action)
        pprint(json.loads(response))
        sys.exit(0)
    response = call_oko_editor_api(action, page=page, record_id=record_id, title=title)
    pprint(json.loads(response))

    sys.exit(0)


if __name__ == "__main__":
    main()
