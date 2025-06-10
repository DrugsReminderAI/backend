import json
import logging
import yaml
from openai import AsyncOpenAI
from dotenv import load_dotenv
from services.memory import get_history, append_to_history
from config import GROQ_API_KEY, GROQ_MODEL, SYSTEM_PROMPT, TEMPERATURE, TOOLS
from services.functions import (
    search,
    save_med_schedule_to_yaml,
    load_med_schedule_from_yaml,
    send_reminder_timer,
    get_moscow_time,
)
from services.confirmation import confirm_medicine, is_confirmed

logging.basicConfig(level=logging.INFO)
load_dotenv()

client = AsyncOpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")


async def ask_groq(user_text: str, user_id: int) -> str:
    try:
        chat_history = get_history(user_id)

        if not chat_history:
            append_to_history(user_id, "system", SYSTEM_PROMPT)

        append_to_history(user_id, "user", user_text)

        confirm_medicine(user_id, "21:00", "аспирин")
        is_confirmed(user_id, "21:00", "аспирин")

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

                    logging.info(
                        f"[TOOL CALL] Вызов функции '{name}' с аргументами: {args}"
                    )

                    if name == "search":
                        result = search(args.get("query"))

                    elif name == "save_med_schedule_to_yaml":
                        result = save_med_schedule_to_yaml(
                            user_id, args.get("schedule_data", {})
                        )

                    elif name == "load_med_schedule_from_yaml":
                        result = load_med_schedule_from_yaml(user_id)

                    elif name == "send_reminder_timer":
                        # таймер асинхронный
                        from asyncio import create_task

                        create_task(
                            send_reminder_timer(
                                user_id,
                                args.get("time_str"),
                                args.get("medicine"),
                            )
                        )
                        result = "⏰ Напоминание будет отправлено"

                    elif name == "get_moscow_time":
                        result = get_moscow_time()

                    else:
                        result = f"⚠️ Неизвестная функция: {name}"

                    if not isinstance(result, str):
                        result = yaml.dump(result, allow_unicode=True)

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
        logging.exception(f"Ошибка во время запроса к Groq:")
        return f"⚠️ Ошибка запроса к Groq: {str(e)}"
