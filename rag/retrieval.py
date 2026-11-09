"""Question → relevant chunks. Pure Python: no Django imports. Dense only for now; BM25 + RRF arrive in Task 7."""

from langchain_core.documents import Document as LCDocument

from rag.vectorstore import get_vector_store

DEFAULT_K = 4


def retrieve(question: str, persist_directory: str, model_name: str, k: int = DEFAULT_K) -> list[tuple[LCDocument, float]]:
    """Return up to k (chunk, cosine distance) pairs, closest first."""
    store = get_vector_store(persist_directory, model_name)
    return store.similarity_search_with_score(query=question, k=k)
