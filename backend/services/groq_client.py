import json
from openai import AsyncOpenAI
from dotenv import load_dotenv
from services.memory import get_history, append_to_history
from config import GROQ_API_KEY, GROQ_MODEL, SYSTEM_PROMPT, TEMPERATURE, TOOLS
from services.functions import search

load_dotenv()

client = AsyncOpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")


async def ask_groq(user_text: str, user_id: int) -> str:
    try:
        chat_history = get_history(user_id)

        if not chat_history:
            append_to_history(user_id, "system", SYSTEM_PROMPT)

        append_to_history(user_id, "user", user_text)

        while True:
            response = await client.chat.completions.create(
                model=GROQ_MODEL,
                messages=chat_history,
                temperature=TEMPERATURE,
                tools=TOOLS,
                tool_choice="auto",
                parallel_tool_calls=True,
            )

            msg = response.choices[0].message
            tool_calls = msg.tool_calls

            if tool_calls:
                # Добавляем assistant-сообщение с tool_calls
                append_to_history(
                    user_id,
                    role="assistant",
                    content=None,
                    tool_calls=[
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in tool_calls
                    ],
                )

                for tc in tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments)

                    if name == "search":
                        query = args.get("query")
                        result = search(query)
                    else:
                        result = f"⚠️ Неизвестная функция: {name}"

                    append_to_history(
                        user_id,
                        role="tool",
                        content=result,
                        tool_call_id=tc.id,
                    )

                # Повторный запрос после выполнения инструментов
                chat_history = get_history(user_id)
                continue

            # Обычный текстовый ответ
            append_to_history(user_id, msg.role, msg.content)
            return msg.content

    except Exception as e:
        return f"⚠️ Ошибка запроса к Groq: {str(e)}"
