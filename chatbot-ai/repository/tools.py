
def get_values(values):
    if values is None:
        return None
    return [dict(value) for value in values] if isinstance(values, list) else dict(values)


def bordering_text(text: str, chunk_size: int = 512):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
    return chunks


