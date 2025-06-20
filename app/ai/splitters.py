from langchain.text_splitter import RecursiveCharacterTextSplitter


def get_splitter(chunk_size=200):
    chunk_overlap = int(0.15 * chunk_size)
    return RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)


def get_narrative_splitter(chunk_size: int = 150):
    chunk_overlap = int(0.2 * chunk_size)
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n", ". ", "! ", "? "]
    )
