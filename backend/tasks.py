import logging
from backend.celery_app import celery_app
from telegram import Bot
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)


@celery_app.task
def send_reminder_task(user_id: int, medicine: str):
    """Фоновая Celery-задача — отправка напоминания пользователю"""
    message_text = f"💊 Напоминание: пора принять {medicine}"
    logging.info(f"[CELERY SEND] {user_id}: {message_text}")

    try:
        bot.send_message(chat_id=user_id, text=message_text)
    except Exception as e:
        logging.error(f"[ERROR] Не удалось отправить сообщение {user_id}: {e}")
