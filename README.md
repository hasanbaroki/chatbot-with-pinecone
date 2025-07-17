# chatbot-with-pine-cone

## Overview

A lightweight memory‑augmented chatbot service that uses **FastAPI**, **OpenAI GPT‑4o‑mini**, and **Pinecone** for long‑term vector search.  Conversations are enriched with past context retrieved by semantic similarity.

## Architecture

```
 Client ─HTTP─► FastAPI /chatbot
   │                         │
   │                         ▼
   │                fetch_memory() ───► Pinecone ⬅─ embed_query (LangChain OpenAIEmbeddings)
   │                         │
   │                         ▼
   │                OpenAI Chat Completion
   │                         │
   │                         ▼
   └─── JSON response ◄──────┘ (store_memory → Pinecone)
```

| Layer        | File        | Responsibility                                |
| ------------ | ----------- | --------------------------------------------- |
| API          | `api.py`    | HTTP endpoint, prompt assembly, orchestration |
| Memory Store | `memory.py` | Embedding + Pinecone upsert/query             |
| Runtime      | `main.py`   | Starts Uvicorn server                         |

## Data Flow (Happy Path)

1. **POST /chatbot** with `chat_room_id`, `user`, `message`, `timestamp`.
2. `fetch_memory` retrieves the most relevant past messages for that room.
3. System + user prompt is sent to OpenAI.
4. Reply comes back; `store_memory` embeds & upserts this turn.
5. JSON payload is returned to the client.

## Tech Stack

* **Python 3.11**
* **FastAPI + Uvicorn** – REST layer
* **OpenAI GPT‑4o‑mini** – reasoning & generation
* **Pinecone** – serverless vector index (euclidean, 1 024 dims)
* **LangChain OpenAIEmbeddings** – text‑embedding‑3‑small

## Local Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Create .env with your keys
OPENAI_API_KEY=...
PINECONE_API_KEY=...
python main.py   # defaults to 0.0.0.0:8000
```

## Environment Variables

| Variable           | Description         |
| ------------------ | ------------------- |
| `OPENAI_API_KEY`   | OpenAI secret key   |
| `PINECONE_API_KEY` | Pinecone secret key |

## API Reference

```
POST /chatbot
{
  "chat_room_id": "string",
  "user": "string",
  "message": "string",
  "timestamp": "ISO‑8601"
}
→ 200 OK
{
  "chat_room_id": "string",
  "user": "string",
  "message": "string",
  "ai_response": "string",
  "timestamp": "ISO‑8601"
}
```

## Scaling Notes

* **Stateless containers** → perfect for Cloud Run or AWS Fargate.
* Pinecone scales storage & QPS automatically; shard by namespace if needed.
* Add Redis/LRU cache in front of Pinecone for ultra‑low‑latency recalls.

---

© 2025 chatbot‑with‑pine‑cone
