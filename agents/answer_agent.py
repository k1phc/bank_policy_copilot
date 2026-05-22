from typing import List

from app.config import get_llm_client, get_settings
from app.schemas import SourceChunk


SYSTEM_PROMPT = """
You are Bank Policy RAG Copilot, an internal assistant for bank employees.

Rules:
1. Answer only using the provided context.
2. If the context is insufficient, say that you cannot confirm the answer from approved documents.
3. Always cite the source documents used.
4. Do not approve loans, bypass KYC, disclose personal data, or perform regulated actions.
5. For complaint responses, prepare a draft only and require human approval.
6. Keep the answer concise, factual and compliance-friendly.
""".strip()


def build_context(chunks: List[SourceChunk]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        parts.append(f"[Source {i}: {chunk.source}]\n{chunk.content}")
    return "\n\n---\n\n".join(parts)


def generate_answer(question: str, chunks: List[SourceChunk]) -> str:
    settings = get_settings()
    client = get_llm_client()

    context = build_context(chunks)
    user_prompt = f"""
Question:
{question}

Approved context:
{context}

Return:
- direct answer;
- source list;
- note if human review is required.
""".strip()

    response = client.chat.completions.create(
        model=settings.llm_model,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or ""
