from __future__ import annotations

import json
import os
from pprint import pprint

from helper import create_payload, send_payload


def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def main() -> None:
    payload = create_payload("help")
    status_code, response = send_payload(payload)
    print(status_code)
    print(response)

    pprint(response)

    ensure_dir("data")
    with open(os.path.join("data", "help.json"), "w", encoding="utf-8") as f:
        json.dump(response, f, ensure_ascii=False)

    payload = create_payload("reconfigure", "X-01")
    status_code, response = send_payload(payload)
    print(status_code)
    pprint(response)

    payload = create_payload("setstatus", "X-01", "RTOPEN")
    status_code, response = send_payload(payload)
    print(status_code)
    pprint(response)

    payload = create_payload("getstatus", "X-01")
    status_code, response = send_payload(payload)
    print(status_code)
    pprint(response)

    payload = create_payload("save", "X-01")
    status_code, response = send_payload(payload)
    print(status_code)
    pprint(response)


if __name__ == "__main__":
    main()
