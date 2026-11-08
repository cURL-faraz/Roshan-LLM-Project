"""Chat-model factory. Pure Python: no Django imports; callers pass configuration in."""

from langchain_core.language_models import BaseChatModel
from langchain_openrouter import ChatOpenRouter


def build_chat_model(
    model: str,
    api_key: str,
    timeout: float = 60,
    max_retries: int = 2,
    temperature: float = 0,
) -> BaseChatModel:
    """Return a configured ChatOpenRouter instance.

    The return type is the LangChain base class, so the rest of the pipeline never
    depends on OpenRouter specifically (swap providers by changing only this function).

    `timeout` is in seconds; ChatOpenRouter expects milliseconds, so it is converted here.
    """
    return ChatOpenRouter(model=model, api_key=api_key, timeout=int(timeout * 1000), max_retries=max_retries, temperature=temperature)
