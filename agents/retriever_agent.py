from typing import List

from app.config import get_llm_client, get_settings
from app.schemas import SourceChunk
from rag.vector_store import query_top_k


def embed_query(query: str) -> List[float]:
    settings = get_settings()
    client = get_llm_client()
    result = client.embeddings.create(model=settings.embedding_model, input=query)
    return result.data[0].embedding


def retrieve_context(question: str, top_k: int = 4) -> List[SourceChunk]:
    query_embedding = embed_query(question)
    rows = query_top_k(query_embedding, k=top_k)

    chunks: List[SourceChunk] = []
    for row in rows:
        doc_id, source, _chunk_index, content, _metadata, distance = row
        chunks.append(
            SourceChunk(
                document_id=doc_id,
                source=source,
                content=content,
                score=float(1.0 - distance) if distance is not None else None,
            )
        )
    return chunks
