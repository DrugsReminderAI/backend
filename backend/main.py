from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
from services.groq_client import ask_groq
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import logging
import asyncio
import os
from config import BOT_TOKEN

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

    ai_reply = await ask_groq(message_text, user_id)

    reply = ai_reply or "✅ Принято, без ответа."
    await update.message.reply_text(reply)
