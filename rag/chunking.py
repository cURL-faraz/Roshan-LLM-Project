"""Text → chunks with metadata. Pure Python: no Django imports."""

from langchain_core.documents import Document as LCDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 800       # characters (see Task 4 notes: E5 truncates at 512 tokens)
CHUNK_OVERLAP = 120    # characters shared by neighbouring chunks

SEPARATORS = ["\n", ".", "؟", "!", " ", ""]
_splitter = RecursiveCharacterTextSplitter(separators=SEPARATORS, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, keep_separator="end")


def chunk_text(document_id: int, title: str, text: str) -> list[LCDocument]:
    """Split one document's text into LangChain Documents ready for indexing.

    Every chunk carries metadata {"document_id", "title", "chunk_index"} and a deterministic
    id "<document_id>:<chunk_index>" (set on LCDocument.id), so re-indexing the same document
    overwrites instead of duplicating, and deleting by document_id is possible.
    """
    chunks = _splitter.split_text(text)
    chunks = [LCDocument(page_content=chunk, metadata={"document_id": document_id, "title": title, "chunk_index": chunk_index}, id=f"{document_id}:{chunk_index}") for chunk_index, chunk in enumerate(chunks)]
    return chunks 
