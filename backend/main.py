from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Message(BaseModel):
    user_id: int
    username: str | None = None
    text: str
    timestamp: str

@app.post("/api/chat")
async def receive(message: Message):
    print(f"[{message.timestamp}] {message.username or message.user_id}: {message.text}")
    return {"reply": f"Вы написали: {message.text}"}