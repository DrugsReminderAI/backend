import requests
import logging
import os
import yaml
import pytz
from datetime import datetime, timedelta
from telegram import Bot
from backend.config import BOT_TOKEN
from pytz import timezone
from backend.tasks import send_reminder_task


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


# Добавление задачи в напоминания
def schedule_reminder(user_id: int, time_str: str, medicine: str):
    tz = timezone("Europe/Moscow")
    now = datetime.now(tz)

    naive_target = datetime.strptime(time_str, "%H:%M").replace(
        year=now.year, month=now.month, day=now.day
    )
    target_time = tz.localize(naive_target)

    if target_time < now:
        target_time += timedelta(days=1)

    logging.info(
        f"[SCHEDULE] user_id={user_id}, medicine='{medicine}', time={target_time}"
    )

    # Отложенный запуск задачи через Celery
    send_reminder_task.apply_async(args=[user_id, medicine], eta=target_time)


# Текущее время
def get_moscow_time() -> str:
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.now(tz)
    return now.strftime("%H:%M")
