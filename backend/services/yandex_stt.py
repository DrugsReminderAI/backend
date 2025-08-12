# backend/services/yandex_stt.py
import aiohttp
import logging
from typing import Optional
from backend.config import YANDEX_API_KEY, YANDEX_STT_LANG, YANDEX_FOLDER_ID

STT_URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"


async def transcribe_oggopus(audio_bytes: bytes) -> Optional[str]:
    """
    Распознаёт короткое голосовое (ogg/opus) через Yandex SpeechKit.
    Работает без folderId. Если YANDEX_FOLDER_ID задан — прокинем его опционально.
    """
    if not YANDEX_API_KEY:
        logging.error("YANDEX_API_KEY не задан")
        return None

    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
    }
    params = {
        "lang": YANDEX_STT_LANG,
        "format": "oggopus",
    }
    # НЕ обязательно. Если есть — добавим.
    if YANDEX_FOLDER_ID:
        params["folderId"] = YANDEX_FOLDER_ID

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                STT_URL, params=params, headers=headers, data=audio_bytes
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    logging.error(f"STT error {resp.status}: {text}")
                    return None

                ct = resp.headers.get("Content-Type", "")
                if "application/json" in ct:
                    data = await resp.json()
                    result = data.get("result")
                    if result:
                        return result.strip()
                    logging.error(f"STT JSON without result: {data}")
                    return None
                else:
                    text = (await resp.text()).strip()
                    return text or None
    except Exception as e:
        logging.exception(f"STT request failed: {e}")
        return None
