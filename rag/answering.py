"""Question-answering use-case. Pure Python: no Django imports; callers pass configuration in."""

from dataclasses import dataclass

from langchain_core.language_models import BaseChatModel

from rag.generation import generate_answer
from rag.retrieval import DEFAULT_K, retrieve

NO_CONTEXT_ANSWER = "No indexed document contains relevant content for this question."


@dataclass(frozen=True)
class AnswerResult:
    answer: str
    sources: list[dict]


def answer_question(question: str, persist_directory: str, model_name: str, llm: BaseChatModel, k: int = DEFAULT_K) -> AnswerResult:
    """Retrieve, then generate. Skips the LLM entirely when nothing was retrieved.

    Each source is {"document_id", "title", "chunk_index", "distance", "excerpt"}, in the same
    order as the [n] citations in the answer.
    """
    results = retrieve(question, persist_directory, model_name, k)
    if results:
        sources = []
        chunks = []
        for chunk, distance in results:
            chunks.append(chunk)
            source = {"document_id": chunk.metadata.get("document_id"),
                      "title": chunk.metadata.get("title"),
                      "chunk_index": chunk.metadata.get("chunk_index"),
                      "distance": distance,
                      "excerpt": chunk.page_content}
            sources.append(source)
        response = generate_answer(question, chunks, llm)
        return AnswerResult(response, sources)

    return AnswerResult(NO_CONTEXT_ANSWER, [])

