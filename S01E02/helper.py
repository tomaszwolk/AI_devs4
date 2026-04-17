import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from haversine import haversine

load_dotenv()
API_KEY = os.getenv("HUB_API_KEY")
HUB_URL = os.getenv("HUB_URL")


def get_closest_power_plant(
    person_locations: list[dict], power_plants_list: list[dict]
) -> dict[str, dict | float | None]:
    """
    To narzędzie przyjmuje listę lokalizacji osoby i listę elektrowni,
    zwraca tę elektrownię, która jest najbliżej.
    """
    closest_power_plant = None
    closest_distance = float("inf")

    for location in power_plants_list:
        for person_location in person_locations:
            distance = haversine(
                (person_location["latitude"], person_location["longitude"]),
                (location["latitude"], location["longitude"]),
            )
            print(f"distance: {distance}, closest_distance: {closest_distance}")
            if distance < closest_distance:
                closest_distance = distance
                closest_power_plant = location
    print(f"closest_plant: {closest_power_plant}, distance: {closest_distance}")
    return {"closest_plant": closest_power_plant, "distance": closest_distance}


def get_person_locations(name: str, surname: str):
    if not HUB_URL:
        raise ValueError("HUB_URL is not set")
    url = HUB_URL + "/api/location"
    resp = requests.post(
        url,
        json={
            "apikey": API_KEY,
            "name": name,
            "surname": surname,
        },
    )
    return resp.json()


def get_access_level(name: str, surname: str, birthYear: int):
    if not HUB_URL:
        raise ValueError("HUB_URL is not set")
    url = HUB_URL + "/api/accesslevel"
    resp = requests.post(
        url,
        json={
            "apikey": API_KEY,
            "name": name,
            "surname": surname,
            "birthYear": birthYear,
        },
    )
    return resp.json()


def get_save_data_from_hub(hub_api_key: str, filename: str) -> dict:
    """
    Get data from hub and save it to a file.
    """
    out_path = Path(__file__).parent / filename

    if not out_path.exists():
        if not HUB_URL:
            raise ValueError("HUB_URL is not set")
        url = HUB_URL + f"/data/{hub_api_key}/{filename}"
        response = requests.get(url)
        data = response.json()
        with open(out_path, "w") as f:
            json.dump(data, f)
        print(f"Data saved to {out_path}")
    else:
        print(f"Data already exists in {out_path}")
        data = json.load(open(out_path))
    return data


def get_power_plants_data():
    """
    Zwraca modelowi listę elektrowni z koordynatami.
    """
    file_path = Path(__file__).parent / "data" / "findhim_locations.json"
    with open(file_path, "r") as f:
        return json.load(f)


def create_report(
    hub_api_key: str,
    task: str,
    name: str,
    surname: str,
    access_level: int,
    power_plant: str,
) -> dict:
    """
    Create a report.
    """
    report = {
        "apikey": hub_api_key,
        "task": task,
        "answer": {
            "name": name,
            "surname": surname,
            "accessLevel": access_level,
            "powerPlant": power_plant,
        },
    }
    return report


def send_report(report: dict) -> tuple[int | None, str | None]:
    """
    Send a report to the hub.
    """
    if not HUB_URL:
        raise ValueError("HUB_URL is not set")
    url = HUB_URL + "/verify"
    response = requests.post(url, json=report)
    return response.status_code, response.text
