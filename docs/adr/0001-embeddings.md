# 0001. Embedding model and runtime
Status: accepted (measured 2026-11-09/10)

Context: We don't know the document language; it could be English, Persian or mixed. Embeddings must
be free, run inside Docker on CPU, and the Docker build must fit a one-day schedule.

Decision: `intfloat/multilingual-e5-small` (384 dimensions, about 118M parameters, about 100 languages
including Persian), run locally through `sentence-transformers` (via `langchain-huggingface`)
with the CPU-only PyTorch wheel. E5 needs the prefixes `"query: "` for questions and
`"passage: "` for chunks; we add them in one place, our embeddings wrapper.

Alternatives:
- fastembed (ONNX runtime, no torch): smaller image and faster install. It officially lists multilingual
  E5 models, but small-model support depends on the version, so we'd have to verify it with
  `TextEmbedding.list_supported_models()`. This is the fallback if torch is too heavy.
- English-only models (all-MiniLM, all-mpnet): poor on Persian.
- multilingual-e5-base/large: better quality but 2–5× the memory and slower on CPU.
- OpenRouter/OpenAI embeddings: costs money and adds a network dependency to indexing.

Consequences: a larger image (torch), about 0.5–1 GB RAM at runtime, and a model download on first
use (cached in a volume). The prefix handling is a known pitfall and must be tested.

Measured: Docker image 1.71 GB with `torch 2.15.0+cpu`; model cache 471 MB in the `hf_cache` volume
(downloaded once, reused after restart); the container uses about 1.2 GB RAM after answering questions.
The first upload took about 73 s (download), and the first question after a restart about 23 s (model load).
English and Persian questions retrieve the right chunk; fastembed was not needed.
