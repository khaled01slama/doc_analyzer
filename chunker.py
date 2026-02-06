"""Document chunking utilities."""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_document(text: str, chunk_size: int = 2000, overlap: int = 200) -> list[str]:
    """Split document into chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n\n", "\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)
