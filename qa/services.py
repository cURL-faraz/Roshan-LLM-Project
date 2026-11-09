"""Django-side orchestration: config from settings, call rag, persist the record."""

import time

from django.conf import settings

from rag.llm import build_chat_model
from rag.answering import answer_question

from .models import QARecord


def ask(question: str) -> QARecord:
    """Answer a question and save it. GenerationError propagates, so failures are not saved."""
    llm = build_chat_model(model=settings.OPENROUTER_MODEL, api_key=settings.OPENROUTER_API_KEY, timeout=settings.OPENROUTER_TIMEOUT)
    start = time.perf_counter()
    result = answer_question(question=question, persist_directory=str(settings.CHROMA_DIR), model_name=settings.EMBEDDING_MODEL, llm=llm)
    latency = round((time.perf_counter() - start) * 1000)
    record = QARecord.objects.create(question=question, answer=result.answer, sources=result.sources, model_name=settings.OPENROUTER_MODEL, latency_ms=latency)
    return record 
