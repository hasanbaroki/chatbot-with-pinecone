from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

from app.config import settings
from app.memory import store_memory, fetch_memory

app = FastAPI(title="LovesYou mini-bot")

openai_client = OpenAI()


class ChatRequest(BaseModel):
    chat_room_id: str
    user: str
    message: str
    timestamp: str


class ChatResponse(BaseModel):
    chat_room_id: str
    user: str
    message: str
    ai_response: str
    timestamp: str


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/chatbot", response_model=ChatResponse)
async def chatbot(req: ChatRequest):
    memories = fetch_memory(req.chat_room_id, req.message)

    system_prompt = (
        f"You are a friendly AI assistant talking to {req.user}. "
        "If past memories are relevant, weave them in naturally. "
        "Do not include any prefixes like 'AI:'—just output the answer text."
    )
    user_parts = []
    if memories:
        user_parts.append("Previous snippets:\n" + "\n\n".join(memories))
    user_parts.append(f"User: {req.message}")
    user_message = "\n".join(user_parts)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    try:
        resp = openai_client.chat.completions.create(
            model=settings.model,
            messages=messages,
            temperature=0.7,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    ai_reply = resp.choices[0].message.content.strip()

    store_memory(req.chat_room_id, req.message, ai_reply, req.timestamp)

    return ChatResponse(
        chat_room_id=req.chat_room_id,
        user=req.user,
        message=req.message,
        ai_response=ai_reply,
        timestamp=datetime.utcnow().isoformat(),
    )
