import json
import logging
import yaml
from openai import AsyncOpenAI
from dotenv import load_dotenv
from backend.services.memory import get_history, append_to_history
from backend.config import (
    SYSTEM_PROMPT,
    TEMPERATURE,
    TOOLS,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)
from backend.services.functions import (
    search,
    save_med_schedule_to_yaml,
    load_med_schedule_from_yaml,
    get_moscow_time,
    refresh_reminders,
)
from backend.services.confirmation import confirm_medicine

logging.basicConfig(level=logging.INFO)
load_dotenv()

# client = AsyncOpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def ask_groq(user_text: str, user_id: int) -> str:
    try:
        chat_history = get_history(user_id)

        if not chat_history:
            append_to_history(user_id, "system", SYSTEM_PROMPT)

        append_to_history(user_id, "user", user_text)

        while True:
            response = await client.chat.completions.create(
                model=OPENAI_MODEL,
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
                        result = save_med_schedule_to_yaml(user_id, args)

                    elif name == "load_med_schedule_from_yaml":
                        result = load_med_schedule_from_yaml(user_id)

                    elif name == "get_moscow_time":
                        result = get_moscow_time()

                    elif name == "confirm_medicine":
                        confirm_medicine(
                            user_id=user_id,
                            time_str=args.get("time_str"),
                            medicine=args.get("medicine"),
                            is_confirm=args.get("is_confirm", True),
                        )
                        result = "✅ Подтверждение обработано"

                    elif name == "schedule_reminder":
                        refresh_reminders(user_id)
                        result = "📆 Все напоминания обновлены"

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
