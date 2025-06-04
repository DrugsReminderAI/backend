import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from services.memory import get_history, append_to_history

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = (
    "Ты честный ИИ-помощник, который помогает с приемом лекарств. "
    "По указанным пользователем выписанным лекарствам и режиму их приема ты составляешь расписание и отправляешь напоминания: "
    "в 7:00 (утро), в 12:00 (обед), в 19:00 (вечер) и в 21:00 (ночь), если не сказано иное. "
    "Если пользователь не подтвердил приём, повторяешь напоминание каждые 30 минут."
)

async def ask_groq(user_text: str, user_id: int) -> str:
    try:
        chat_history = get_history(user_id)

        if not chat_history:
            append_to_history(user_id, "system", SYSTEM_PROMPT)

        append_to_history(user_id, "user", user_text)

        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=chat_history,
            temperature=0.7
        )

        ai_message = response.choices[0].message
        append_to_history(user_id, ai_message.role, ai_message.content)

        return ai_message.content

    except Exception as e:
        return f"⚠️ Ошибка запроса к Groq: {str(e)}"
