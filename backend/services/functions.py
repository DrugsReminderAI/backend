import requests
import logging
import os
import yaml

from config import SERPER_API_KEY, SCHEDULES_DIR

logging.basicConfig(level=logging.INFO)


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


# Составление расписания для пользователя в ymlв формате
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
