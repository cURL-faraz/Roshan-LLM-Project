"""Question → relevant chunks: dense and BM25 search fused with RRF. Pure Python: no Django imports."""

from langchain_core.documents import Document as LCDocument
from rag.fusion import reciprocal_rank_fusion
from rag.sparse import tokenize, bm25_search
from rag.vectorstore import get_vector_store



DEFAULT_K = 4
CANDIDATE_K = 20  # how many chunks each search contributes before fusion


def _load_all_chunks(store) -> list[LCDocument]:
    """Every indexed chunk, rebuilt as LCDocuments. Chroma stays the only copy, so BM25 can't go stale."""
    data = store.get(include=["documents", "metadatas"])
    chunks = []
    for i in range(len(data["documents"])):
        page_content = data["documents"][i]
        metadata = data["metadatas"][i]
        chunks.append(LCDocument(page_content=page_content, metadata=metadata, id=data["ids"][i]))
    return chunks


def _drop_duplicate_text(fused: list[tuple[LCDocument, float]]) -> list[tuple[LCDocument, float]]:
    """Keep the first chunk for each distinct text, so a document uploaded twice can't fill every slot."""
    seen = set()
    unique_fused = []
    for chunk, score in fused:
        normalized_page_content = " ".join(tokenize(chunk.page_content))
        if normalized_page_content not in seen:
            seen.add(normalized_page_content)
            unique_fused.append((chunk, score))
    return unique_fused


def retrieve(question: str, persist_directory: str, model_name: str, k: int = DEFAULT_K) -> list[tuple[LCDocument, float]]:
    """Return up to k (chunk, RRF score) pairs, best first."""
    store = get_vector_store(persist_directory, model_name)
    dense_list = [chunk for chunk, distance in store.similarity_search_with_score(query=question, k=CANDIDATE_K)]
    sparse_list = bm25_search(question, chunks=_load_all_chunks(store), k=CANDIDATE_K)
    fused = reciprocal_rank_fusion([dense_list, sparse_list])
    unique_fused = _drop_duplicate_text(fused)
    return unique_fused[:k]
