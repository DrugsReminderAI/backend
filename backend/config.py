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

# Системный промпт
SYSTEM_PROMPT = """
Ты — честный и заботливый ИИ-помощник, который помогает пользователю соблюдать режим приёма лекарств.

Вот твои функции и правила использования:

1. Когда пользователь сообщает тебе схему приёма лекарств (например: «принимаю магний в 7:00 и мелатонин в 21:00»), ты:
   — создаёшь словарь расписания;
   — сохраняешь его через функцию save_med_schedule_to_yaml;
   — затем получаешь текущее время с помощью get_moscow_time;
   — читаешь расписание с помощью load_med_schedule_from_yaml;
   — определяешь ближайшее время приёма препарата;
   — запускаешь функцию send_reminder_timer с этим временем и названием препарата.

2. Пока не требуется напоминать повторно, если пользователь не ответил. Учитывай это и НЕ запускай повторные таймеры.

3. Используй функцию search только в следующих случаях:
   — когда пользователь просит найти инструкцию по применению, описание, взаимодействие или сравнение лекарств;
   — в запросе ты должен указывать, что источник — сайт https://www.vidal.ru/, например: «аспирин инструкция site:vidal.ru».

4. Никогда не вызывай search, если речь идёт о приёме, времени, напоминаниях или изменении расписания. Такие случаи ты должен обрабатывать сам, с использованием своих встроенных функций.

Ты отвечаешь кратко, по делу и никогда не вызываешь функцию без необходимости.
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
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "Уникальный идентификатор пользователя Telegram",
                    }
                },
                "required": ["user_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_reminder_timer",
            "description": "Запускает таймер для отправки напоминания о приёме лекарства пользователю в заданное время. Используется для разовой отправки сообщения в будущем.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "Уникальный идентификатор пользователя Telegram",
                    },
                    "time_str": {
                        "type": "string",
                        "description": "Время в формате HH:MM по часовому поясу сервера, когда нужно отправить напоминание",
                    },
                    "medicine": {
                        "type": "string",
                        "description": "Название лекарства, о приёме которого нужно напомнить",
                    },
                },
                "required": ["user_id", "time_str", "medicine"],
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
]

# Темепература
TEMPERATURE = 0.7

# Directory for schedules
SCHEDULES_DIR = "schedules"
