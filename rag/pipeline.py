"""Indexing use-cases. Pure Python: no Django imports; callers pass configuration in."""

from rag.chunking import chunk_text
from rag.vectorstore import get_vector_store


def delete_document(document_id: int, persist_directory: str, model_name: str) -> None:
    """Remove every chunk belonging to one document from Chroma."""
    store = get_vector_store(persist_directory, model_name)
    store.delete(where={"document_id": document_id})


def index_document(document_id: int, title: str, text: str, persist_directory: str, model_name: str) -> int:
    """Make Chroma match this document's current text. Returns the number of chunks stored.

    Delete first: an edit that produces FEWER chunks would otherwise leave stale chunks behind.
    """
    store = get_vector_store(persist_directory, model_name)
    delete_document(document_id, persist_directory, model_name)
    chunks = chunk_text(document_id, title, text)
    if chunks:
        store.add_documents(chunks, ids=[chunk.id for chunk in chunks])
    return len(chunks)
