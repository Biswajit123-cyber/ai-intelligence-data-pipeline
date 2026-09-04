from src.chunker import semantic_chunks

def test_chunk_limit():
    text = "sentence " * 5000
    chunks = semantic_chunks(text, max_chars=1000)
    assert chunks
    assert all(len(c) <= 1000 for c in chunks)
