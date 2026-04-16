from tools import send_command
import sys
from pprint import pprint

# UG8gZG90YXJjaXUgZG8gY2VsdSB3csOzYyBuYSBzdGFydA==


def main():
    # Jeśli podany jest argument "verify",
    # wysyłamy kod potwierdzający do centrali.
    if sys.argv[1] == "verify":
        command = sys.argv[2]
        response = send_command(command)
        pprint(response)
        sys.exit(0)


if __name__ == "__main__":
    main()
