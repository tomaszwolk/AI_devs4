import requests
import logging
import json
import mimetypes
import base64
from datetime import datetime
import sys
from config import settings
from e2b_code_interpreter import Sandbox

logger = logging.getLogger(__name__)


def call_verify_api(**kwargs) -> str:
    """
    Wykonuje strzał do API centrali. Automatycznie przechwytuje i dekoduje pliki Base64,
    aby nie obciążać modelu językowego niepotrzebnymi tokenami.
    """
    # Szukamy właściwego payloadu niezależnie od tego, jak model go nazwał
    if "answer_payload" in kwargs:
        answer_payload = kwargs["answer_payload"]
    elif "answer" in kwargs:
        answer_payload = kwargs["answer"]
    else:
        # Jeśli model pominął nadrzędny klucz i przesłał od razu np. {"action": "reset"}
        answer_payload = kwargs

    payload = {
        "apikey": settings.api_key,
        "task": settings.task,
        "answer": answer_payload
    }
    try:
        response = requests.post(settings.verify_url, json=payload, timeout=30)
        response.raise_for_status()  # Wyrzuci błąd jeśli status nie jest 200
    except requests.exceptions.Timeout:
        logger.error("Timeout wysyłania do API")
        return json.dumps({"error": "Timeout wysyłania do API. Spróbuj ponownie akcję listen."}, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Error: {e}")
        return json.dumps({"error": f"Błąd komunikacji z API: {str(e)}"}, ensure_ascii=False, indent=4)

    try:
        data = response.json()
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"Błąd dekodowania JSON z API: {response.text}"

    if "attachment" in data:
        meta_type = data.get("meta", "application/octet-stream")
        filesize = data.get('filesize', None)
        data["attachment"] = decode_base64(
            data["attachment"],
            meta_type,
            filesize
        )

    return json.dumps(data, ensure_ascii=False, indent=4)


def decode_base64(base64_data: str, meta_type: str, filesize: int) -> str:
    clean_b64 = base64_data
    if clean_b64.startswith("BASE64:"):
        clean_b64 = clean_b64.split(":", 1)[-1] if ":" in clean_b64 else clean_b64.replace("BASE64:", "")

    # Próba dekodowania
    try:
        file_bytes = base64.b64decode(clean_b64)

        # ustalam rozszerzenie na podstawie "meta"
        ext = mimetypes.guess_extension(meta_type) or ".bin"
        # Unikalna nazwa pliku
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"intercepted_file_{timestamp}{ext}"
        filepath = settings.logs_dir_path / filename

        # Zapis pliku
        with open(filepath, "wb") as f:
            f.write(file_bytes)

        # Powiadomienie użytkownika i pauza
        print("\n" + "!" * 60)
        print("🚨🚨🚨 UWAGA! PRZECHWYCONO PLIK BINARNY 🚨🚨🚨")
        print(f"Typ: {meta_type}")
        print(f"Rozmiar: {filesize if filesize else len(file_bytes)} bajtów")
        print(f"Zapisano jako: {filename}")
        print("!" * 60)

        while True:
            print("\nCo chcesz zrobić z tym plikiem?")
            print("[1] Wstrzyknij zdekodowaną zawartość bezpośrednio Agentowi (Tylko dla JSON/XML/TXT)")
            print("[2] Zobaczę plik samemu i napiszę Agentowi ręcznie co tam jest (Audio/Obraz)")
            print("[3] Zignoruj (Podaj Agentowi jedynie ścieżkę do pliku, np. by sprawdził go Pythonem)")
            print("[4] Przerwij działanie całego programu")

            user_decision = input("Wybierz opcję (1/2/3/4): ").strip()

            if user_decision == '1':
                try:
                    with open(filepath, "r", encoding='utf-8') as f:
                        content = f.read()
                        return f"[DEKODOWANY PLIK {meta_type}]:\n{content}"
                except UnicodeDecodeError:
                    logger.error("Błąd odczytu pliku: Nieprawidłowy kodowanie UTF-8")

            elif user_decision == '2':
                user_desc = input("Wpisz podsumowanie/transkrypcję/opis dla Agenta: ")
                return f"[OPERATOR PRZEANALIZOWAŁ PLIK I RAPORTUJE]: {user_desc}"

            elif user_decision == '3':
                return f"[UKRYTO BASE64. Plik znajduje się pod ścieżką: 'logs/{filename}'. Możesz do niego uzyskać dostęp używając Pythona.]"

            elif user_decision == '4':
                logger.info("Przerywam działanie skryptu. Zaktualizuj kod/toole na podstawie tego, co zobaczyłeś w pliku.")
                sys.exit(0)
            else:
                logger.error("Nieprawidłowy wybór. Spróbuj ponownie.")

    except Exception as e:
        logger.error(f"Błąd dekodowania Base64: {e}")


def execute_python_code(code: str) -> str:
    """Zwraca: Stdout z konsoli Python w bezpiecznym sandboxie."""
    logger.debug("E2B: run_code (len=%d)", len(code))
    # Sandbox() bez .create() nie tworzy połączenia — wymagane jest Sandbox.create()
    with Sandbox.create() as sandbox:
        execution = sandbox.run_code(code)
        if execution.error:
            return f"Błąd: {execution.error.value}"
        return execution.logs.stdout


TOOLS_DICT = {
    "call_verify_api": call_verify_api,
    "execute_python_code": execute_python_code,
}
