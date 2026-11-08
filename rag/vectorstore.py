"""Embeddings + Chroma vector store. Pure Python: no Django imports; callers pass configuration in."""

from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings

COLLECTION_NAME = "document_chunks"


@lru_cache(maxsize=1)
def get_embeddings(model_name: str) -> Embeddings:
    """Load the sentence-transformers model once per process (loading takes seconds and ~0.5 GB RAM).

    E5 models require "passage: " on stored text and "query: " on questions, and we want
    unit-length vectors so cosine similarity == dot product.
    """
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"prompt": "passage: " , "normalize_embeddings": True}
    query_encode_kwargs = {"prompt": "query: ", "normalize_embeddings": True}
    return HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs, query_encode_kwargs=query_encode_kwargs)


@lru_cache(maxsize=1)
def get_vector_store(persist_directory: str, model_name: str) -> Chroma:
    """Open (or create) the persistent Chroma collection, using cosine distance."""
    embedding_function = get_embeddings(model_name)
    return Chroma(collection_name=COLLECTION_NAME, embedding_function=embedding_function, persist_directory=persist_directory, collection_metadata={"hnsw:space": "cosine"})
