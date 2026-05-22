from typing import List


def chunk_text(text: str, max_chars: int = 1200) -> List[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current = ""

    for paragraph in paragraphs:
        if not current:
            current = paragraph
            continue

        if len(current) + 2 + len(paragraph) > max_chars:
            chunks.append(current)
            current = paragraph
        else:
            current += "\n\n" + paragraph

    if current:
        chunks.append(current)

    return chunks
