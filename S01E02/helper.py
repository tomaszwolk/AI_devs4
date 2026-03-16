import requests
import json
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2


def get_save_data_from_hub(hub_api_key: str, filename: str) -> dict:
    """
    Get data from hub and save it to a file.
    """
    out_path = Path(__file__).parent / filename

    if not out_path.exists():
        url = f"https:///data/{hub_api_key}/{filename}"
        response = requests.get(url)
        data = response.json()
        save_to_file(data, out_path)
        print(f"Data saved to {out_path}")
    else:
        print(f"Data already exists in {out_path}")
        data = json.load(open(out_path))
    return data


def save_to_file(data: dict, out_path: Path) -> None:
    """
    Save data to a file.
    """
    with open(out_path, "w") as f:
        json.dump(data, f)


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two points on the Earth's surface
    using the Haversine formula.

    Args:
        lat1: float - latitude of the first point (in degrees)
        lon1: float - longitude of the first point (in degrees)
        lat2: float - latitude of the second point (in degrees)
        lon2: float - longitude of the second point (in degrees)

    Returns:
        float - distance between the two points in kilometers
    """
    R = 6371.0  # promień Ziemi [km]

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def send_request_to_hub(api_type: str, payload: dict) -> dict:
    """
    Send a request to the hub.
    """
    url = f"https:///api/{api_type}"
    response = requests.post(url, json=payload)
    return response.json()


def create_payload(
    hub_api_key: str,
    name: str,
    surname: str,
    birth_year: int | None = None
) -> dict:
    """
    Create a payload for a request to the hub.
    """
    payload = {
        "apikey": hub_api_key,
        "name": name,
        "surname": surname
    }
    if birth_year is not None:
        payload["birthYear"] = birth_year
    return payload


def find_closest_location(
    person_locations: list[dict],
    locations: list[dict]
) -> tuple[dict, float]:
    """
    Find the closest location from a list of locations.
    """
    closest_location = None
    closest_distance = float('inf')
    for location in locations:
        for person_location in person_locations:
            distance = haversine(
                person_location['latitude'],
                person_location['longitude'],
                location['latitude'],
                location['longitude']
            )
            if distance < closest_distance:
                closest_distance = distance
                closest_location = location
    return closest_location, closest_distance


def create_report(
    hub_api_key: str,
    task: str,
    name: str,
    surname: str,
    access_level: int,
    power_plant: str
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
            "powerPlant": power_plant
        }
    }
    return report


def send_report(report: dict) -> None:
    """
    Send a report to the hub.
    """
    url = "https:///verify"
    response = requests.post(url, json=report)
    return response.status_code, response.text
