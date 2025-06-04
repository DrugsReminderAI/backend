from fastapi import FastAPI
from pydantic import BaseModel
from backend.services.groq_client import ask_groq
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

class Message(BaseModel):
    user_id: int
    username: str | None = None
    text: str
    timestamp: str

@app.post("/api/chat")
async def receive(message: Message):
    logging.info(f"[{message.timestamp}] {message.username or message.user_id}: {message.text}")
    ai_reply = await ask_groq(message.text)
    logging.info(f"[AI Reply] → {ai_reply}")
    return {"reply": ai_reply}
