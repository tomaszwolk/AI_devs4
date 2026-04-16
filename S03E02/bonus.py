from tools import run_shell_command, send_verify_answer
import sys
import json
from pprint import pprint

# /bin/flaggengenerator schmetterling


def main():
    # Jeśli podany jest argument "verify",
    # wysyłamy kod potwierdzający do centrali.
    if sys.argv[1] == "verify":
        confirmation_code = sys.argv[2]
        response = send_verify_answer(confirmation_code)
        pprint(response)
        sys.exit(0)
    # Jedna komenda powłoki: scal argumenty
    # (np. ścieżka + argument binarki bez cudzysłowów).
    command = " ".join(sys.argv[1:]).strip()
    if not command:
        print("Użycie: uv run bonus.py <komenda powłoki>", file=sys.stderr)
        sys.exit(2)
    raw = run_shell_command(command)
    try:
        response = json.loads(raw)
    except json.JSONDecodeError:
        # Np. komunikat BAN-u (plaintext) z tools — wypisz jak jest.
        print(raw)
        sys.exit(1)
    pprint(response)


if __name__ == "__main__":
    main()
