import os, uuid, logging
from datetime import datetime
from typing import List, Dict

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec

###############################################################################
# ── 1. ENV  ──────────────────────────────────────────────────────────────────
###############################################################################
load_dotenv()                            # expects a .env with the keys below
OPENAI_API_KEY   = os.environ["OPENAI_API_KEY"]
PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]

INDEX_NAME       = "chatbot-longterm"
EMBED_DIMENSION  = 1024                 # text‑embedding‑3‑small

###############################################################################
# ── 2. CLIENTS  ──────────────────────────────────────────────────────────────
###############################################################################
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",   #   atau 'text-embedding-ada-002'
    dimensions=1024,                  # ⬅️  harus sama dgn index Pinecone
    openai_api_key=OPENAI_API_KEY
)
pc = Pinecone(api_key=PINECONE_API_KEY)
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBED_DIMENSION,
        metric="euclidean",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
index = pc.Index(INDEX_NAME)

###############################################################################
# ── 3. HELPERS  ──────────────────────────────────────────────────────────────
###############################################################################
def store_memory(chat_id: str, user_msg: str, ai_msg: str, ts: str) -> None:
    """
    Embed & upsert the user message plus bot reply.
    """
    vec = embeddings.embed_query(user_msg)
    meta = {
        "chat_room_id": chat_id,
        "message": user_msg,
        "response": ai_msg,
        "timestamp": ts,
    }
    # same upsert pattern as your original code :contentReference[oaicite:0]{index=0}
    index.upsert([(str(uuid.uuid4()), vec, meta)])

def fetch_memory(chat_id: str, query: str, top_k: int = 5) -> List[Dict]:
    """
    Retrieve past Q/A pairs for **this** chat_room_id that semantically
    match the current query.
    """
    vec = embeddings.embed_query(query)
    # filter guarantees we only see this room’s memories
    res = index.query(
        vector=vec,
        top_k=top_k,
        include_metadata=True,
        filter={"chat_room_id": chat_id},
    )
    print("🎯 Pinecone hits:", [m["metadata"]["message"] for m in res["matches"]])
    hits = []
    for m in res["matches"]:
        md = m["metadata"]
        hits.append(
            f'User: {md["message"]}\nAI  : {md["response"]}'
        )
    return hits
