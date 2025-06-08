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

        # если пришёл вызов инструмента
        if tool_calls:
            tool_call = tool_calls[0]
            if tool_call.function.name == "search":
                args = json.loads(tool_call.function.arguments)
                query = args.get("query")
                result = search(query)

                append_to_history(
                    user_id, "assistant", None
                )  # чтобы сохранить tool_call
                append_to_history(
                    user_id, "tool", result, tool_call_id=tool_calls[0].id
                )
            else:
                unknown_response = f"⚠️ Неизвестная функция: {tool_call.function.name}"
                append_to_history(user_id, "tool", unknown_response)
                return unknown_response

            # повторный запрос без tools
            updated_history = get_history(user_id)
            response = await client.chat.completions.create(
                model=GROQ_MODEL, messages=updated_history, temperature=TEMPERATURE
            )

            final_msg = response.choices[0].message
            append_to_history(user_id, final_msg.role, final_msg.content)
            return final_msg.content

        # обычный ответ
        append_to_history(user_id, msg.role, msg.content)
        return msg.content

    except Exception as e:
        return f"⚠️ Ошибка запроса к Groq: {str(e)}"
