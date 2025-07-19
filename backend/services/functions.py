import requests
import logging
import os
import yaml
import time
import pytz
from datetime import datetime, timedelta
from telegram import Bot
from backend.config import BOT_TOKEN
from pytz import timezone
from backend.tasks import send_reminder_task
from backend.celery_app import celery_app
from celery.result import AsyncResult


from backend.config import SERPER_API_KEY, SCHEDULES_DIR

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


# Удаление всех задач юзера
def clear_reminders_for_user(user_id: int):
    task_ids = [
        f"user-{user_id}-{hour:02}:{minute:02}"
        for hour in range(24)
        for minute in range(60)
    ]

    try:
        celery_app.control.revoke(task_ids, terminate=True)
        logging.info(f"[REVOKE] Отозваны задачи: {len(task_ids)} для user_id={user_id}")
        for task_id in task_ids:
            AsyncResult(task_id, app=celery_app).forget()
    except Exception as e:
        logging.warning(f"[REVOKE] Ошибка отзыва задач: {e}")


# Добавление задачи в напоминания
def schedule_reminder(user_id: int, time_str: str, medicines: list[str]):
    tz = timezone("Europe/Moscow")
    now = datetime.now(tz)

    naive_target = datetime.strptime(time_str, "%H:%M").replace(
        year=now.year, month=now.month, day=now.day
    )
    target_time = tz.localize(naive_target)

    if target_time < now:
        target_time += timedelta(days=1)

    logging.info(
        f"[SCHEDULE] user_id={user_id}, medicine='{medicines}', time={target_time}"
    )

    # Отложенный запуск задачи через Celery
    send_reminder_task.apply_async(
        args=[user_id, medicines], eta=target_time, task_id=f"user-{user_id}-{time_str}"
    )


def refresh_reminders(user_id: int):
    clear_reminders_for_user(user_id)
    time.sleep(10)
    schedule = load_med_schedule_from_yaml(user_id)
    for time_str, meds in schedule.items():
        schedule_reminder(user_id, time_str, meds)


# Текущее время
def get_moscow_time() -> str:
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.now(tz)
    return now.strftime("%H:%M")
