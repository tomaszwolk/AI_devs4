import requests
import os
from dotenv import load_dotenv

load_dotenv()
hub_api_key = os.getenv("HUB_API_KEY")
package_url = "https:///api/packages"


def check_package(packageid: str) -> dict:
    body = {
        "apikey": hub_api_key,
        "action": "check",
        "packageid": packageid,
    }
    response = requests.post(package_url, json=body)
    return response.json()


def redirect_package(packageid: str, destination: str, code: str) -> dict:
    body = {
        "apikey": hub_api_key,
        "action": "redirect",
        "packageid": packageid,
        "destination": destination,
        "code": code,
    }
    response = requests.post(package_url, json=body)
    return response.json()
