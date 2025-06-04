from fastapi import FastAPI
from pydantic import BaseModel
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
    return {"reply": ai_reply}
logging.info(f"[AI Reply] → {ai_reply}")