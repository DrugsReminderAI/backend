from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.services.groq_client import ask_groq
from backend.services.yandex_stt import transcribe_oggopus
from telegram import Update
from telegram.error import BadRequest, TimedOut, RetryAfter
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import logging
import asyncio
import io
from backend.config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск Telegram-бота
    async def run_bot():
        app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
        app_bot.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_telegram_message)
        )
        app_bot.add_handler(
            MessageHandler(filters.VOICE & ~filters.COMMAND, handle_voice_message)
        )
        app_bot.add_handler(
            MessageHandler(~filters.TEXT & ~filters.VOICE, handle_unknown_message)
        )
        await app_bot.initialize()
        await app_bot.start()
        await app_bot.updater.start_polling()
        logging.info("Telegram бот запущен")

    asyncio.create_task(run_bot())
    yield


app = FastAPI(lifespan=lifespan)


async def handle_telegram_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message_text = update.message.text
    user_id = user.id
    timestamp = update.message.date.isoformat()

    placeholder = await update.message.reply_text("🤔 Думаем...")

    try:
        # 2) запрос к LLM
        ai_reply = await ask_groq(message_text, user_id)
        reply = ai_reply or "✅ Принято, без ответа."

        # 3) редактируем заглушку
        await placeholder.edit_text(reply)

    except (RetryAfter, TimedOut):
        # Telegram притормозил — отправим новое сообщение
        await update.message.reply_text("⏳ Сервер отвечает дольше обычного...")
        try:
            await update.message.reply_text(
                ai_reply if "ai_reply" in locals() and ai_reply else "✅ Принято."
            )
        except Exception:
            pass

    except BadRequest as e:
        # Например, сообщение уже удалено/устарело — шлём отдельным
        await update.message.reply_text(
            ai_reply if "ai_reply" in locals() and ai_reply else f"⚠️ {e}"
        )

    except Exception as e:
        # на всякий случай
        await update.message.reply_text(f"⚠️ Ошибка обработки запроса: {e}")


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    voice = update.message.voice

    # ограничим до ~60с
    if voice and voice.duration and voice.duration > 60:
        await update.message.reply_text(
            "⏱️ Голосовое длиннее 60 сек — укороти, пожалуйста."
        )
        return

    try:
        tg_file = await context.bot.get_file(voice.file_id)

        # Скачаем в память
        buf = io.BytesIO()
        await tg_file.download_to_memory(out=buf)
        audio_bytes = buf.getvalue()

        # Распознаём
        text = await transcribe_oggopus(audio_bytes)
        if not text:
            await update.message.reply_text(
                "😕 Не удалось распознать голос. Попробуй ещё раз."
            )
            return

        ai_reply = await ask_groq(text, user_id)
        reply = ai_reply or "✅ Принято, без ответа."
        await update.message.reply_text(f"🎤 Распознал: «{text}»\n\n{reply}")

    except Exception as e:
        logging.exception(f"Voice handling failed: {e}")
        await update.message.reply_text("⚠️ Ошибка обработки голосового сообщения.")


async def handle_unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤷 Я такое не понимаю. Пришли текст или голосовое."
    )
