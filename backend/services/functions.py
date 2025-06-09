import requests
import logging
import os
import yaml
import asyncio
from datetime import datetime, timedelta
from telegram import Bot
from config import BOT_TOKEN
from datetime import datetime
import pytz

from config import SERPER_API_KEY, SCHEDULES_DIR

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)


# Поиск в гугле
def search(query: str) -> str:
    logging.info(f"Ищу в гугле {query}")

    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY, "Content-type": "application/json"},
            json={"q": query},
        )

        if response.status_code in [200, 201]:
            data_json = response.json()
            data = "\n".join(
                f"{item['title']}: {item['snippet']}"
                for item in data_json.get("organic", [])[:3]
            )
            return data

    except Exception as e:
        logging.error(f"Ошибка при поиске: {str(e)}")
        return f"Ошибка при поиске: {str(e)[:5000]}"


# Составление расписания для пользователя в yml в формате
# `schedule_data`: {
# "07:00": ["витамин D", "магний"],
# "12:00": ["обеденный препарат"],
# "21:00": ["мелатонин"]
# }
def save_med_schedule_to_yaml(user_id: int, schedule_data: dict):

    os.makedirs(SCHEDULES_DIR, exist_ok=True)
    filepath = os.path.join(SCHEDULES_DIR, f"{user_id}.yml")

    with open(filepath, "w", encoding="utf-8") as file:
        yaml.dump(schedule_data, file, allow_unicode=True)

    return filepath


# Чтение расписания из файла
def load_med_schedule_from_yaml(user_id: int) -> dict:
    filepath = os.path.join(SCHEDULES_DIR, f"{user_id}.yml")

    if not os.path.exists(filepath):
        logging.warning(f"Файл расписания не найден для user_id={user_id}")
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            schedule_data = yaml.safe_load(file) or {}
            return schedule_data
    except Exception as e:
        logging.error(f"Ошибка при чтении расписания: {str(e)}")
        return {}


# Таймер
async def send_reminder_timer(user_id: int, time_str: str, medicine: str):
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.now(tz)
    target_time = datetime.strptime(time_str, "%H:%M").replace(
        year=now.year, month=now.month, day=now.day, tzinfo=moscow
    )

    delay = (target_time - now).total_seconds()
    logging.info(
        f"[TIMER] user_id={user_id}, medicine='{medicine}', delay={delay:.2f} сек "
        f"(target={target_time.strftime('%Y-%m-%d %H:%M:%S %Z')}, now={now.strftime('%Y-%m-%d %H:%M:%S %Z')})"
    )

    await asyncio.sleep(delay)

    try:
        message_text = f"💊 Напоминание: пора принять {medicine}"

        logging.info(
            f"[SEND] Отправка напоминания пользователю {user_id}: {message_text}"
        )
        await bot.send_message(chat_id=user_id, text=message_text)

    except Exception as e:
        print(f"Ошибка при отправке напоминания: {e}")


# Текущее время
def get_moscow_time() -> str:
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.now(tz)
    return now.strftime("%H:%M")
