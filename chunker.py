def semantic_chunks(text: str, max_chars: int = 12000, overlap: int = 500) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    sentences = []
    current = []
    size = 0

    for sentence in text.replace("!", ".").replace("?", ".").split("."):
        sentence = sentence.strip()
        if not sentence:
            continue
        addition = len(sentence) + 1
        if current and size + addition > max_chars:
            sentences.append(" ".join(current))
            tail = current[-1][-overlap:]
            current = [tail]
            size = len(tail)
        current.append(sentence)
        size += addition

    if current:
        sentences.append(" ".join(current))
    return sentences
