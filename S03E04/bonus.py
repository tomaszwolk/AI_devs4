from tools import verify_answer, send_tools
import sys
from pprint import pprint


def main():
    # Uruchom uv run bonus.py
    # Wyśle narzędzia do centrali. Potem zobacz na /debug
    response = send_tools()
    pprint(response)

    response = verify_answer()
    pprint(response)
    sys.exit(0)


if __name__ == "__main__":
    main()
