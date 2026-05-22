from rag.chunking import chunk_text


def test_chunk_text_returns_one_chunk_for_short_text():
    text = "Short paragraph one.\n\nShort paragraph two."
    chunks = chunk_text(text, max_chars=1000)
    assert len(chunks) == 1
    assert "one" in chunks[0] and "two" in chunks[0]


def test_chunk_text_splits_when_over_limit():
    para_a = "A" * 600
    para_b = "B" * 600
    para_c = "C" * 600
    text = "\n\n".join([para_a, para_b, para_c])
    chunks = chunk_text(text, max_chars=1000)
    assert len(chunks) >= 2
    joined = "".join(chunks)
    assert "A" * 600 in joined
    assert "B" * 600 in joined
    assert "C" * 600 in joined


def test_chunk_text_ignores_empty_paragraphs():
    text = "First.\n\n\n\nSecond.\n\n   \n\nThird."
    chunks = chunk_text(text, max_chars=1000)
    assert len(chunks) == 1
    assert "First" in chunks[0]
    assert "Second" in chunks[0]
    assert "Third" in chunks[0]
