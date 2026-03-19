from tools import call_zmail_api, get_help_data
from pprint import pprint
from agent import MainAgent


def main():
    # Get help data
    help_data = get_help_data()
    pprint(help_data)

    USER_PROMPT = f"""
    Wiemy, że donosiciel Wiktor (nie znamy jego nazwiska) wysłał maila z domeny 'proton.me'.
    Przeszukaj skrzynkę używając API by znaleźć wszytkie 3 informacje.
    Parametry są opisane w {help_data}.
    """

    agent = MainAgent()
    try:
        agent.run(USER_PROMPT)
    except Exception as e:
        print(f"Wystąpił błąd krytyczny: {e}")


if __name__ == "__main__":
    main()
    # reset = call_zmail_api(action="reset")
    # pprint(reset)
