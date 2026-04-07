import requests
from config import settings


def solve_bonus():
    # Part 1: Send pocisk
    payload = {
        "apikey": settings.api_key,
        "task": settings.task,
        "answer": {"audio": "pocisk"}
    }

    print(f"Wysyłam pocisk pod adres: {settings.verify_url}")

    try:
        response = requests.post(settings.verify_url, json=payload)
        print("Status Code:", response.status_code)
        print("Odpowiedź serwera:")
        print(response.text)
        data = response.json()
    except Exception as e:
        print(f"Błąd: {e}")

    # Part 2: Get file
    url = settings.hub_url + data['secret']

    params = {"input[number]": 2333331}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        print(response.text)
    else:
        print(f"Błąd pobierania: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    solve_bonus()
