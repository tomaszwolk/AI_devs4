from dotenv import load_dotenv
import os
import pandas as pd
import json
from pathlib import Path
from helper import (
    get_save_data_from_hub,
    send_request_to_hub,
    create_payload,
    find_closest_location,
    create_report,
    send_report,
)


def main():
    load_dotenv()
    hub_api_key = os.getenv("HUB_API_KEY")
    # Pobieranie listy elektrowni i ich kody
    filename = "findhim_locations.json"
    locations_data = get_save_data_from_hub(hub_api_key, filename)

    # Pobieranie danych osób z pliku people_transport.csv
    people_transport_path = Path(__file__).parent / "people_transport.csv"
    df_people_transport = pd.read_csv(people_transport_path, sep=";")

    # Inicjalizacja danych raportu
    report_data = {
        "name": None,
        "surname": None,
        "access_level": None,
        "power_plant": None,
        "distance": float("inf"),
    }
    for _, row in df_people_transport.iterrows():
        # Pobieranie danych osoby
        name = row["name"]
        surname = row["surname"]
        birth_year = pd.to_datetime(row["birthDate"]).year
        payload = create_payload(hub_api_key, name, surname, birth_year)

        # Pobieranie lokalizacji osoby
        location_response = send_request_to_hub("location", payload)

        # Znajdowanie najbliższej elektrowni z listy elektrowni
        power_plants_locations_path = (
            Path(__file__).parent / "Miejscowo-Szer-Dlug.json"
        )
        with open(
            power_plants_locations_path, encoding="utf-8"
        ) as power_plants_locations_file:
            power_plants_locations = json.load(power_plants_locations_file)
        power_plants_locations_list = power_plants_locations["cities"]

        closest_location = find_closest_location(
            location_response, power_plants_locations_list
        )
        print(
            f"Najbliższa elektrownia: {name}, {surname}, \
                {closest_location[0]['name']}, \
                    odległość: {closest_location[1]} km"
        )

        # Pobieranie poziomu dostępu osoby
        access_level_response = send_request_to_hub("accesslevel", payload)

        # Aktualizacja danych raportu jeśli odległość jest mniejsza
        if closest_location[1] < report_data["distance"]:
            report_data["name"] = name
            report_data["surname"] = surname
            report_data["access_level"] = access_level_response["accessLevel"]
            report_data["power_plant"] = closest_location[0]["name"]
            report_data["distance"] = closest_location[1]

    power_plant_code = (
        locations_data["power_plants"][report_data["power_plant"]]
    )
    report = create_report(
        hub_api_key,
        "findhim",
        report_data["name"],
        report_data["surname"],
        report_data["access_level"],
        power_plant_code["code"],
    )

    print(f"Report: {report}")
    status_code, response = send_report(report)

    print(f"Status code: {status_code}")
    print(f"Response: {response}")


if __name__ == "__main__":
    main()
