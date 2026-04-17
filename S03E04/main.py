import asyncio
import logging
from contextlib import asynccontextmanager

import httpx
from config import (
    API_KEY,
    LOGS_DIR_PATH,
    MAIN_MODEL,
    MAIN_SYSTEM_PROMPT,
    MY_TOOL_URL,
    OPENROUTER_API_KEY,
    OPENROUTER_URL,
    TASK,
    VERIFY_URL,
)
from fastapi import FastAPI, Request
from openai import AsyncOpenAI
from pydantic import BaseModel
from tools import load_database

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """Jedna konfiguracja root loggera: konsola + plik."""
    LOGS_DIR_PATH.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                LOGS_DIR_PATH / "logs.log",
                encoding="utf-8",
            ),
        ],
        force=True,
    )


configure_logging()

ACLIENT = AsyncOpenAI(
    base_url=OPENROUTER_URL,
    api_key=OPENROUTER_API_KEY,
)


async def verify_loop() -> None:
    """Rejestruje narzędzie i asynchronicznie odpytuje o flagę co 10 sekund."""
    async with httpx.AsyncClient() as client:
        logger.info("\n🚀 Rejestruję narzędzie w centrali...")
        payload = {
            "apikey": API_KEY,
            "task": TASK,
            "answer": {
                "tools": [
                    {
                        "URL": MY_TOOL_URL,
                        "description": "WINDFARM Szuka miast, w których dostępny jest sprzęt. W polu 'params' podaj, czego potrzebujesz (np. 'potrzebuję kabla długości 10 metrów'). Narzędzie zwróci listę miast (np. 'Warszawa, Krakow'). Użyj tego narzędzia dla każdego potrzebnego przedmiotu z osobna.",
                    },
                ]
            },
        }
        if not VERIFY_URL:
            raise ValueError("VERIFY_URL is not set")
        resp = await client.post(VERIFY_URL, json=payload)
        logger.info(
            "Rejestracja — status=%s body=%s",
            resp.status_code,
            resp.text,
        )

        await asyncio.sleep(5)
        logger.info("🕵️ Rozpoczynam nasłuchiwanie i sprawdzanie flagi (co 10s)...")

        while True:
            check_payload = {
                "apikey": API_KEY,
                "task": TASK,
                "answer": {"action": "check"},
                # "answer": {"action": "WINDFARM"},
            }
            try:
                check_resp = await client.post(VERIFY_URL, json=check_payload)
                data = check_resp.json()

                message = data.get("message", "")
                if isinstance(message, str) and "FLG:" in message:
                    logger.info("\n🎉 ZDOBYTO FLAGĘ:\n%s\n", message)
                    break

                logger.info("⏳ Sprawdzam... Centrala mówi: %s", message)
            except Exception:
                logger.exception("❌ Błąd podczas sprawdzania")

            await asyncio.sleep(10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db, all_items_str = load_database()
    app.state.db = db
    app.state.main_system_prompt = MAIN_SYSTEM_PROMPT.format(
        all_items_str=all_items_str,
    )
    logger.info("📦 Załadowano %s przedmiotów do pamięci.", len(db))

    task = asyncio.create_task(verify_loop())

    yield

    task.cancel()


app = FastAPI(lifespan=lifespan)


class ToolRequest(BaseModel):
    params: str


@app.post("/api/search")
async def search_cities(req: ToolRequest, request: Request):
    """Główny endpoint, do którego będzie uderzał Agent z Centrali."""
    db = request.app.state.db
    main_system_prompt = request.app.state.main_system_prompt

    logger.info("\n📥 Agent pyta o: %s", req.params)

    response = await ACLIENT.chat.completions.create(
        model=MAIN_MODEL,  # type: ignore
        messages=[
            {"role": "system", "content": main_system_prompt},
            {"role": "user", "content": req.params},
        ],
        temperature=0.0,
    )

    exact_item_name = response.choices[0].message.content.strip()  # type: ignore
    logger.info("🤖 LLM wywnioskował, że to: %s", exact_item_name)

    cities = db.get(exact_item_name, [])

    if not cities:
        logger.error("⚠️ Nie znaleziono miast dla tego przedmiotu!")
        return {"output": "Brak miast oferujących ten przedmiot."}

    cities_str = ", ".join(cities)
    if len(cities_str.encode("utf-8")) > 500:
        cities_str = cities_str[:490] + "..."

    logger.info("🏙️ Zwracam miasta: %s", cities_str)

    return {"output": cities_str}
