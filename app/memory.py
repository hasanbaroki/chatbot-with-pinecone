import uuid
from typing import List

from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec

from app.config import settings

EMBED_DIMENSION = 1024

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    dimensions=EMBED_DIMENSION,
    openai_api_key=settings.openai_api_key,
)

pc = Pinecone(api_key=settings.pinecone_api_key)
if settings.index_name not in pc.list_indexes().names():
    pc.create_index(
        name=settings.index_name,
        dimension=EMBED_DIMENSION,
        metric="euclidean",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
index = pc.Index(settings.index_name)


def store_memory(chat_id: str, user_msg: str, ai_msg: str, ts: str) -> None:
    vec = embeddings.embed_query(user_msg)
    meta = {
        "chat_room_id": chat_id,
        "message": user_msg,
        "response": ai_msg,
        "timestamp": ts,
    }
    index.upsert([(str(uuid.uuid4()), vec, meta)])


def fetch_memory(chat_id: str, query: str, top_k: int = 5) -> List[str]:
    vec = embeddings.embed_query(query)
    res = index.query(
        vector=vec,
        top_k=top_k,
        include_metadata=True,
        filter={"chat_room_id": chat_id},
    )
    hits = []
    for m in res["matches"]:
        md = m["metadata"]
        hits.append(f'User: {md["message"]}\nAI  : {md["response"]}')
    return hits
