import os
from dotenv import load_dotenv

load_dotenv()

# Переменные окружения
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Модель по умолчанию
GROQ_MODEL = "llama-3.3-70b-versatile"

# Системный промпт
SYSTEM_PROMPT = (
    "Ты честный ИИ-помощник, который помогает с приемом лекарств. "
    "По указанным пользователем выписанным лекарствам и режиму их приема ты составляешь расписание, "
    "и отправляешь напоминания в 7:00 по Москве для утреннего приема, в 12:00 — обеденного, "
    "в 19:00 — вечернего, и в 21:00 — ночного, если пользователь не оговорит другое время. "
    "Если пользователь не ответил, что принял таблетки — напоминаешь повторно через полчаса и так далее."
)

# Темепература
TEMPERATURE = 0.7

# Serper API Key
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Directory for schedules
SCHEDULES_DIR = "schedules"

# Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
