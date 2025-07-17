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

    # 2) build prompt (ultra‑simple, as requested)
    prompt_parts = [
        f"You are a friendly AI talking to {req.user}.",
        "If past memories are relevant, weave them in naturally."
    ]
    if memories:
        prompt_parts.append("\nPrevious snippets:\n" + "\n\n".join(memories))
    prompt_parts.append(f"\nUser: {req.message}")
    prompt = "\n".join(prompt_parts)

    # 3) ask OpenAI
    try:
        resp = openai_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
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
