import base64
import json
import logging
import os
from datetime import datetime

import requests
from config import settings
from elevenlabs.client import ElevenLabs
from openai import OpenAI

logger = logging.getLogger(__name__)

# WAŻNE: Wymaga klucza OPENAI_API_KEY w .env
audio_client = OpenAI()

try:
    tts_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
except Exception as e:
    logger.error(f"[ELEVENLABS] Błąd: {e}")
    tts_client = None

# Głos „Adam”
ELEVENLABS_VOICE_ADAM = "pNInz6obpgDQGcFmaJgB"


def call_verify_api(**kwargs) -> str:
    if "answer_payload" in kwargs:
        answer_payload = kwargs["answer_payload"]
    elif "answer" in kwargs:
        answer_payload = kwargs["answer"]
    else:
        answer_payload = kwargs

    os.makedirs(settings.logs_dir_path, exist_ok=True)

    # === NOWA, TWARDA ZASADA DLA AKCJI "start" ===
    # Jeśli agent chce rozpocząć rozmowę, wysyłamy JSON bez względu na wszystko inne.
    if answer_payload.get("action") == "start":
        logger.info(
            "[AKCJA] Wykryto akcję 'start'. Wysyłam bezpośrednio bez przetwarzania audio."
        )
        # Czyścimy payload, zostawiając tylko to co potrzebne do startu
        # To nas chroni, gdyby LLM dodał też 'text_to_audio' przez pomyłkę
        answer_payload = {"action": "start"}

    # === KODOWANIE AUDIO DLA WSZYSTKICH POZOSTAŁYCH PRZYPADKÓW ===
    # Używamy elif, aby ten blok nie wykonał się, gdy akcją jest 'start'
    elif "text_to_audio" in answer_payload:
        text = answer_payload.pop("text_to_audio")
        logger.info(f"[TTS] Generuję wypowiedź: {text}")
        try:
            if not tts_client:
                raise RuntimeError(
                    "Klient ElevenLabs nie został zainicjalizowany (brak ELEVENLABS_API_KEY?)."
                )
            audio_bytes = b"".join(
                tts_client.text_to_speech.convert(
                    voice_id=ELEVENLABS_VOICE_ADAM,
                    text=text,
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128",
                )
            )

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            agent_audio_path = settings.logs_dir_path / f"{timestamp}_agent.mp3"

            with open(agent_audio_path, "wb") as f:
                f.write(audio_bytes)
            logger.info(
                f"[ZAPIS AUDIO] Zapisano wypowiedź Agenta do pliku: {agent_audio_path.name}"
            )

            answer_payload["audio"] = base64.b64encode(audio_bytes).decode("utf-8")
        except Exception as e:
            logger.error(f"[TTS] Błąd: {e}")
            return json.dumps({"error": f"Błąd generowania audio: {e}"})

    payload = {
        "apikey": settings.api_key,
        "task": settings.task,
        "answer": answer_payload,
    }
    if not settings.verify_url:
        raise ValueError("VERIFY_URL is not set")
    try:
        response = requests.post(settings.verify_url, json=payload, timeout=30)
        data = response.json()
    except requests.exceptions.Timeout:
        return json.dumps({"error": "Timeout. Spróbuj ponownie."}, ensure_ascii=False)
    except Exception as e:
        return json.dumps(
            {"error": f"Błąd API lub parsowania: {e}"}, ensure_ascii=False
        )

    # Jeśli kod odpowiedzi jest ujemny, to znaczy, że rozmowa się nie powiodła.
    if data.get("code", 0) < 0:
        error_code = data.get("code")
        error_msg = data.get("message", "Nieznany błąd")
        logger.warning(
            f"Rozmowa spalona! Otrzymano kod błędu {error_code}: {error_msg}"
        )
        return json.dumps(
            {
                "SYSTEM_ALERT": f"ROZMOWA SPALONA! Otrzymano kod błędu {error_code}. Operator uznał Cię za osobę podejrzaną. MUSISZ NATYCHMIAST przerwać i w kolejnym kroku wywołać API z akcją 'start', aby zacząć od nowa."
            },
            ensure_ascii=False,
            indent=4,
        )

    for key in ["message", "reply", "audio"]:
        if key in data and isinstance(data[key], str) and len(data[key]) > 200:
            logger.info("[Whisper] Odebrano długi ciąg znaków, sprawdzam czy to audio.")
            try:
                audio_bytes = base64.b64decode(data[key] + "===")

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                operator_audio_path = (
                    settings.logs_dir_path / f"{timestamp}_operator.mp3"
                )

                with open(operator_audio_path, "wb") as f:
                    f.write(audio_bytes)
                logger.info(
                    f"[ZAPIS AUDIO] Zapisano odpowiedź Operatora do pliku: \
                        {operator_audio_path.name}"
                )

                with open(operator_audio_path, "rb") as f:
                    transcript = audio_client.audio.transcriptions.create(
                        model="whisper-1", file=f, language="pl"
                    )

                logger.info(f"Operator powiedział: {transcript.text}")
                data[key] = f"(Transkrypcja nagrania od operatora): \
                    {transcript.text}"
            except Exception as e:
                logger.debug(f"Nie udało się odkodować Base64: {e}")

    return json.dumps(data, ensure_ascii=False, indent=4)


TOOLS_DICT = {
    "call_verify_api": call_verify_api,
}
