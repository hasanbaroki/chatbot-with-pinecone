# api.py
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from openai import OpenAI
from memory import store_memory, fetch_memory

app = FastAPI(title="LovesYou mini‑bot")

openai_client = OpenAI()  # reads OPENAI_API_KEY from env automatically
MODEL = "gpt-4o-mini"


# ── request / response schema ────────────────────────────────────────────────
class ChatRequest(BaseModel):
    chat_room_id: str
    user: str
    message: str
    timestamp: str   # ISO 8601


class ChatResponse(BaseModel):
    chat_room_id: str
    user: str
    message: str
    ai_response: str
    timestamp: str


# ── endpoint ─────────────────────────────────────────────────────────────────
@app.post("/chatbot", response_model=ChatResponse)
async def chatbot(req: ChatRequest):
    # 1) recall relevant memories
    memories = fetch_memory(req.chat_room_id, req.message)

    # 2) build system + user messages to avoid speaker prefixes
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

    # 3) ask OpenAI
    try:
        resp = openai_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    ai_reply = resp.choices[0].message.content.strip()

    # 4) persist to Pinecone
    store_memory(req.chat_room_id, req.message, ai_reply, req.timestamp)

    # 5) send back
    return ChatResponse(
        chat_room_id=req.chat_room_id,
        user=req.user,
        message=req.message,
        ai_response=ai_reply,
        timestamp=datetime.utcnow().isoformat(),
    )
