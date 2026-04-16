from agent import MainAgent


def main():
    agent = MainAgent()
    try:
        agent.run()
    except Exception as e:
        print(f"Wystąpił błąd krytyczny: {e}")


if __name__ == "__main__":
    main()
