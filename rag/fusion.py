"""Reciprocal Rank Fusion: merge ranked lists using rank positions only. Pure Python."""

from langchain_core.documents import Document as LCDocument

RRF_K = 60


def reciprocal_rank_fusion(ranked_lists: list[list[LCDocument]], rrf_k: int = RRF_K) -> list[tuple[LCDocument, float]]:
    """Return (chunk, score) pairs, highest score first, with one entry per chunk id.

    score(chunk) = sum over the lists containing it of 1 / (rrf_k + rank), with rank starting at 1.
    """
    chunks = {}
    scores = {}
    for ranked_list in ranked_lists:
        for rank, chunk in enumerate(ranked_list, start=1):
            chunks[chunk.id] = chunk
            scores[chunk.id] = scores.get(chunk.id, 0) + 1 / (rrf_k + rank)
    sorted_keys = sorted(chunks.keys(), key=lambda id: scores[id], reverse=True)
    sorted_pairs = []
    for key in sorted_keys:
        sorted_pairs.append((chunks[key], scores[key]))
    return sorted_pairs
