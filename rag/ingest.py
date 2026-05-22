from pathlib import Path
from typing import List

from app.config import get_llm_client, get_settings
from rag.chunking import chunk_text
from rag.vector_store import init_schema, upsert_chunks


def read_markdown_files(docs_path: str):
    docs = []
    for path in sorted(Path(docs_path).glob("*.md")):
        docs.append({"source": path.name, "text": path.read_text(encoding="utf-8")})
    return docs


def embed(text: str) -> List[float]:
    settings = get_settings()
    client = get_llm_client()
    result = client.embeddings.create(model=settings.embedding_model, input=text)
    return result.data[0].embedding


def build_index() -> None:
    settings = get_settings()
    init_schema()

    docs = read_markdown_files(settings.docs_path)
    if not docs:
        print(f"[ingest] No markdown files found in {settings.docs_path}")
        return

    rows = []
    for doc in docs:
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            doc_id = f"{doc['source']}::{i}"
            embedding = embed(chunk)
            rows.append((doc_id, doc["source"], i, chunk, embedding, {"source": doc["source"], "chunk_index": i}))
            print(f"[ingest] embedded {doc_id} ({len(chunk)} chars)")

    written = upsert_chunks(rows)
    print(f"[ingest] upserted {written} chunks from {len(docs)} documents.")


if __name__ == "__main__":
    build_index()
