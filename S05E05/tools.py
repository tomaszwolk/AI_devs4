import json
import os
import logging
import requests
import time
import re
from config import settings

logger = logging.getLogger(__name__)


def download_data() -> str:
    url = settings.hub_url + "/dane/timetravel.md"
    response = requests.get(url)

    os.makedirs("data", exist_ok=True)
    with open("data/timetravel.md", "w", encoding="utf-8") as f:
        f.write(response.text)
    return "Data downloaded successfully"


def call_verify_api(**kwargs) -> str:
    answer_payload = (
        kwargs.get("answer_payload") or kwargs.get("answer") or kwargs
    )

    payload = {
        "apikey": settings.api_key,
        "task": settings.task,
        "answer": answer_payload,
    }

    try:
        response = requests.post(settings.verify_url, json=payload, timeout=30)
        data = response.json()
    except requests.exceptions.Timeout:
        return json.dumps(
            {"error": "Timeout. Spróbuj ponownie."},
            ensure_ascii=False
            )
    except Exception as e:
        return json.dumps(
            {"error": f"Błąd API lub parsowania: {e}"}, ensure_ascii=False
        )

    # Jeśli kod odpowiedzi jest ujemny, to znaczy, że należy zmienić zapytanie
    if data.get("code", 0) < 0:
        logger.warning(
            f"Otrzymano kod błędu {data.get('code')}: {data.get('message')}"
        )

    return json.dumps(data, ensure_ascii=False, indent=4)


def calculate_sync_ratio(day: int, month: int, year: int) -> float:
    """
    Oblicza wartość wskaźnika temporalnego na podstawie daty docelowej.
    Zwraca ułamek dziesiętny do 2 miejsc po przecinku (np. 0.81).
    """
    try:
        ratio = (day * 8 + month * 12 + year * 7) % 101
        # Zamiana na format oczekiwany przez API (np. wynik 37 to 0.37)
        return round(ratio / 100.0, 2)
    except Exception as e:
        logger.error(f"Błąd podczas wyliczania sync_ratio: {e}")
        return 0.0


def update_ui_state(**kwargs) -> str:
    """
    Wysyła polecenie zmiany ustawień do interfejsu WWW (Frontend).
    Może przyjmować `payload={...}` lub bezpośrednio spłaszczone parametry.
    """
    # Elastyczne wyciąganie danych niezależnie od tego, jak LLM sformatuje JSON
    if "payload" in kwargs:
        payload = kwargs["payload"]
    else:
        payload = kwargs

    full_payload = payload.copy()
    full_payload["apikey"] = settings.api_key

    # Endpoint interfejsu
    url = settings.hub_url + "/timetravel_backend"

    try:
        response = requests.post(url, json=full_payload, timeout=10)
        # Wypisujemy raw text w razie błędu 500, żeby wiedzieć co się stało
        if not response.ok:
            return f"Błąd HTTP {response.status_code}: {response.text}"

        data = response.json()
        return json.dumps(data, ensure_ascii=False, indent=4)

    except requests.exceptions.Timeout:
        return json.dumps(
            {"error": "Timeout UI. Spróbuj ponownie."}, ensure_ascii=False
        )
    except Exception as e:
        return json.dumps(
            {"error": f"Błąd komunikacji z UI: {e}"}, ensure_ascii=False
        )


def wait_and_click_sphere(expected_internal_mode: int) -> str:
    """Narzędzie, które nasłuchuje na UI aż stan będzie idealny do skoku."""
    url = settings.hub_url + "/timetravel_backend"

    # 1. Zapewniamy, że interfejs wchodzi w stan active
    requests.post(
        url,
        json={"apikey": settings.api_key, "mode": "active"},
        timeout=10
    ).json()

    logger.info(f"Oczekiwanie na perfect timing dla skoku...\
        (target mode: {expected_internal_mode})")
    # Waiting up to 45 seconds for the machine to be in the perfect timing
    for _ in range(45):
        try:
            response = requests.post(
                url,
                json={"apikey": settings.api_key},
                timeout=10
            ).json()
        except Exception as e:
            logger.warning(f"Błąd odczytu stanu maszyny: {e}")
            time.sleep(1)
            continue

        config = response.get("config", {})

        # Jeśli flaga wyleciała sama z siebie w payloadzie, przechwytujemy
        if "FLG:" in str(response):
            return json.dumps(response, ensure_ascii=False)

        current_mode = config.get("internalMode")
        flux = config.get("fluxDensity")

        if current_mode == expected_internal_mode and flux == 100:
            logger.info("Warunki idealne! KLIK!")

            jump_payload = {
                "apikey": settings.api_key,
                "task": settings.task,
                "answer": {"action": "timeTravel"}
            }
            try:
                jump_response = requests.post(
                    settings.verify_url,
                    json=jump_payload,
                    timeout=10
                ).json()
                if jump_response.get("code", 0) < 0:
                    error_msg = f"❌ SKOK ODRZUCONY PRZEZ MASZYNĘ! Centrala zwróciła błąd: {jump_response}. Powiedz Backendowi, by naprawił konfigurację!"
                    logger.error(error_msg)
                    return error_msg
                else:
                    success_msg = f"✅ SKOK UDANY! Aktualny stan z centrali: {json.dumps(jump_response, ensure_ascii=False)}"
                    logger.info(success_msg)
                    return success_msg
            except Exception as e:
                return json.dumps({"error": f"Błąd podczas aktywacji skoku: {e}"}, ensure_ascii=False)

        time.sleep(1)

    return f"""Timeout operacji.
        InternalMode: {current_mode} FluxDensity: {flux}
        Oczekiwany internalMode lub fluxDensity 100% nie wystąpiły na czas."""


def get_jump_requirements(year: int) -> str:
    """Narzędzie dla Agenta. Pobiera z dokumentacji prawidłowy poziom ochrony (PWR) oraz internalMode dla danego roku."""
    # 1. Oblicz internalMode
    if year < 2000:
        internal_mode = 1
    elif 2000 <= year <= 2150:
        internal_mode = 2
    elif 2151 <= year <= 2300:
        internal_mode = 3
    else:
        internal_mode = 4

    # 2. Pobierz bezbłędnie PWR z tabeli w Markdownie
    pwr = 0
    try:
        with open("data/timetravel.md", "r", encoding="utf-8") as f:
            content = f.read()
        # Wyrażenie regularne precyzyjnie łapiące rok z tabeli i jego wartość obok
        pattern = rf"\|\s*{year}\s*\|\s*(\d+)\s*\|"
        match = re.search(pattern, content)
        if match:
            pwr = int(match.group(1))
    except Exception as e:
        logger.error(f"Error parsing PWR: {e}")

    return json.dumps({
        "required_pwr": pwr,
        "required_internal_mode": internal_mode
    })


def pass_control(target_agent: str, message: str) -> dict:
    # To pseudo-narzędzie, przechwytywane przez kontroler agenta.
    return {"__handoff__": True, "target": target_agent, "message": message}


# Rozdzielone słowniki dla poszczególnych agentów
BACKEND_TOOLS_DICT = {
    "call_verify_api": call_verify_api,
    "calculate_sync_ratio": calculate_sync_ratio,
    "get_jump_requirements": get_jump_requirements,
    "pass_control": pass_control
}

FRONTEND_TOOLS_DICT = {
    "update_ui_state": update_ui_state,
    "wait_and_click_sphere": wait_and_click_sphere,
    "pass_control": pass_control
}

TOOLS_DICT = {
    **BACKEND_TOOLS_DICT,
    **FRONTEND_TOOLS_DICT,
}
