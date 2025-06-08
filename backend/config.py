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
SYSTEM_PROMPT = (
    "Ты честный ИИ-помощник, который помогает с приемом лекарств. "
    "По указанным пользователем выписанным лекарствам и режиму их приема ты составляешь расписание, "
    "и отправляешь напоминания в 7:00 по Москве для утреннего приема, в 12:00 — обеденного, "
    "в 19:00 — вечернего, и в 21:00 — ночного, если пользователь не оговорит другое время. "
    "Если пользователь не ответил, что принял таблетки — напоминаешь повторно через полчаса и так далее."
    "По запросу пользователя ты можешь найти описание, инструкцию по применению и определить совместимость выписанных лекарств"
)

# Tools
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Поиск информации о лекарствах через гугл приемущественно на сайте https://www.vidal.ru/",
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
    }
]

# Темепература
TEMPERATURE = 0.7

# Directory for schedules
SCHEDULES_DIR = "schedules"
