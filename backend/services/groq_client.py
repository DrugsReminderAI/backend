import os
from openai import AsyncOpenAI

# Загрузим переменные из .env
from dotenv import load_dotenv
load_dotenv()

# Конфигурация клиента
client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

async def ask_groq(user_text: str) -> str:
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Ты честный ИИ-помощник, который помогает с приемом лекарств, по указанным пользователем выписанным лекарствам и режиму их приема ты составляешь расписание их приема и отправляешь напоминания в 7:00 по москве для утреннего приема, в 12:00 для обеденного, в 19:00 для вечернего и в 21:00 для ночного если пользователь не оговорит другое время, если пользователь не ответил, что принял таблетки напоминаешь повторно через полчаса и так пока он не примет"},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Ошибка запроса к Groq: {str(e)}"
