import os
from dotenv import load_dotenv

load_dotenv()

# Переменные окружения
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Serper API Key
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Модель по умолчанию
GROQ_MODEL = "llama-3.3-70b-versatile"
# GROQ_MODEL = "llama3-70b-8192"

# Системный промпт
SYSTEM_PROMPT = """
Ты — честный и заботливый ИИ-помощник, который помогает пользователю соблюдать режим приёма лекарств.

Вот твои функции и правила использования:

1. Когда пользователь сообщает тебе схему приёма лекарств (например: «принимаю магний в 7:00 и мелатонин в 21:00»), ты:
   — формируешь словарь расписания;
   — сохраняешь его через функцию save_med_schedule_to_yaml;
   — вызываешь get_moscow_time (не более одного раза за запрос — даже если не получил ответ);
   — читаешь текущее расписание через load_med_schedule_from_yaml;
   — для каждого времени и лекарства в расписании вызываешь функцию schedule_reminder.

2. Повторные напоминания через 30 минут **не используются**. Учитывай это: **не создавай дополнительную задачу**, если пользователь не подтвердил приём.

3. Используй функцию search только в случаях:
   — когда пользователь просит найти инструкцию по применению, описание, взаимодействие или сравнение лекарств;
   — ты обязан формулировать поисковый запрос с указанием сайта https://www.vidal.ru/, например: «аспирин инструкция site:vidal.ru».

4. Никогда не вызывай search, если речь идёт о приёме, времени, напоминаниях или изменении расписания. Эти задачи ты решаешь локально с помощью своих встроенных функций.

5. Когда пользователь пишет, что принял лекарство, вызывай confirm_medicine с флагом is_confirm=True. Чтобы отменить подтверждение — вызывай confirm_medicine с is_confirm=False.

Ты всегда действуешь чётко, без лишних шагов и без повторных вызовов одной и той же функции в рамках одного запроса.
""".strip()


# Tools
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Поиск информации о лекарствах через гугл приемущественно на сайте https://www.vidal.ru/. Функция не должна вызываться повторно, если результат уже получен, даже если он недостаточно точен",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Текстовый запрос в поисковую систему",
                    }
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_med_schedule_to_yaml",
            "description": (
                "Сохраняет расписание приёма лекарств пользователя в YAML-файл. "
                "Используется, когда пользователь вводит или изменяет схему приёма препаратов. "
                "YAML-файл создаётся отдельно для каждого пользователя по его user_id. "
                "Время указывается в формате HH:MM. "
                "Для каждого времени указывается список препаратов, например:\n\n"
                "{\n"
                '  "07:00": ["витамин D", "магний"],\n'
                '  "12:00": ["обеденный препарат"],\n'
                '  "21:00": ["мелатонин"]\n'
                "}"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "schedule_data": {
                        "type": "object",
                        "description": "Словарь с ключами — временем (в формате HH:MM), значениями — списками названий препаратов.",
                        "additionalProperties": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Список названий лекарств",
                        },
                    }
                },
                "required": ["schedule_data"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "load_med_schedule_from_yaml",
            "description": "Читает текущее расписание приёма лекарств пользователя из YAML-файла по его user_id. Если файл отсутствует или повреждён, возвращает пустой словарь.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_moscow_time",
            "description": "Возвращает текущее время по московскому часовому поясу в формате HH:MM. Используется для ориентации по локальному времени пользователя, если не указан часовой пояс явно. Функция не должна вызываться повторно, если результат уже получен, даже если он недостаточно точен",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "confirm_medicine",
            "description": (
                "Подтверждает или отменяет факт приёма лекарства пользователем. "
                "Используется, когда пользователь сообщает, что он принял или отменяет подтверждение приёма препарата. "
                "Подтверждение сохраняется в кэше на 24 часа."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "time_str": {
                        "type": "string",
                        "description": "Время приёма лекарства в формате HH:MM",
                    },
                    "medicine": {
                        "type": "string",
                        "description": "Название лекарства",
                    },
                    "is_confirm": {
                        "type": "boolean",
                        "description": "True — подтверждение приёма, False — отмена подтверждения",
                    },
                },
                "required": ["time_str", "medicine", "is_confirm"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_reminder",
            "description": (
                "Запланировать напоминание о приёме лекарства через Celery. "
                "Время округляется до следующего дня, если указанный момент уже прошёл. "
                "Функция не проверяет подтверждение приёма — просто ставит задачу на исполнение."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "time_str": {
                        "type": "string",
                        "description": "Время в формате HH:MM по Москве, когда нужно напомнить",
                    },
                    "medicine": {
                        "type": "string",
                        "description": "Название лекарства, которое нужно напомнить принять",
                    },
                },
                "required": ["time_str", "medicine"],
                "additionalProperties": False,
            },
        },
    },
]

# Темепература
TEMPERATURE = 0.7

# Directory for schedules
SCHEDULES_DIR = "schedules"
