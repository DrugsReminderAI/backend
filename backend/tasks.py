import logging
import asyncio
from backend.celery_app import celery_app
from telegram import Bot
from backend.config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)


async def send_async_message(user_id: int, text: str):
    await bot.send_message(chat_id=user_id, text=text)


@celery_app.task
def send_reminder_task(user_id: int, medicine: list[str]):
    if isinstance(medicine, list):
        medicine_str = ", ".join(medicine)
    else:
        medicine_str = str(medicine)

    message_text = f"💊 Напоминание: пора принять {medicine_str}"
    logging.info(f"[CELERY SEND] {user_id}: {message_text}")
    try:
        asyncio.run(send_async_message(user_id, message_text))
    except Exception as e:
        logging.error(f"[ERROR] Не удалось отправить сообщение {user_id}: {e}")
