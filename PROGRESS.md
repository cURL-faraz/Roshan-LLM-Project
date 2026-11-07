# PROGRESS

## Current stage
**Stage 2: Task 1 (Django documents app).** Day 1 started 2026-11-06 18:12. Budget: about 7 focused hours.
Strategy: strict MVP first. Get the end-to-end path working before adding anything else.

## Milestones
- **M1: End-to-end MVP.** DOCX upload (Admin) → extraction → chunking → embeddings →
  Chroma → `POST /api/ask/` → dense retrieval → ChatOpenRouter → answer saved as `QARecord`.
- **M2: Assessment complete.** Document CRUD API, hybrid BM25 + RRF, Docker Compose demo,
  essential tests.
- **M3: Submission.** README, API docs, sample data, screenshots, ZIP, presentation.

## Task plan (time-boxed)
Legend: ⬜ not started · 🟨 in progress · ✅ accepted (verified) · ⏸ postponed

| # | Task | Milestone | Budget | Actual | Status |
|---|------|-----------|--------|--------|--------|
| 0 | Conda env, git, `.gitignore`, Django project boots (`.env.example` moved to Task 1) | M1 | 40m | ~2h | ✅ |
| 1 | `documents` app: env-based settings, `Document` model, Admin, DOCX extraction on save | M1 | 60m | | 🟨 |
| 2 | Minimal Dockerfile + compose; volume persistence test (SQLite + media) | M1 | 40m | | ⬜ |
| 3 | OpenRouter smoke test: ChatOpenRouter, model availability, timeout and error handling | M1 | 25m | | ⬜ |
| 4 | `rag/`: chunking, E5 embeddings (with prefixes), Chroma indexing; sync on save/delete | M1 | 75m | | ⬜ |
| 5 | `qa` app: `QARecord`, dense retrieve → prompt → generate, `POST /api/ask/` | M1 | 70m | | ⬜ |
| — | **M1 check: full flow inside Docker Compose** | M1 | 10m | | ⬜ |
| 6 | DRF documents CRUD API (upload, edit, delete) + history endpoint | M2 | 35m | | ⬜ |
| 7 | BM25 retriever + RRF fusion (user writes RRF) + duplicate handling | M2 | 50m | | ⬜ |
| 8 | Essential tests (extraction, RRF, sync, API with mocked LLM) | M2 | 40m | | ⬜ |
| 9 | README, drf-spectacular docs, sample DOCX (EN + FA), screenshots, ZIP | M3 | Day 2 | | ⬜ |
| — | Reranking, agents, metadata filters in API, eval set | — | — | | ⏸ (out of scope) |

Total for Day 1 (Tasks 0–8): about 7h 25m. That's slightly over budget, so Task 8 is the first to shrink.
**Rule:** if a task runs past its budget by more than 50%, stop, reassess scope, and record the decision here.

## Final architecture (confirmed for implementation)
- `config/`: Django project (settings read secrets from the environment).
- `documents/`: Django app. `Document` is the source of truth (file, title, `extracted_text`).
- `qa/`: Django app. `QARecord` (question, answer, sources, model, latency, timestamp).
- `rag/`: plain Python with no Django imports. It handles extraction, chunking, embeddings, vector store, retrieval, generation and pipeline.
- Django calls `rag.pipeline` (`index_document`, `delete_document`, `answer`). The Chroma
  index is a derived copy, keyed by `document_id` in the chunk metadata.
- Docker: one `web` service, with named volumes for `data/` (SQLite + Chroma), `media/` and the HF model cache.

## Key decisions
- Chat LLM: OpenRouter through `langchain-openrouter` (`ChatOpenRouter`), with the model name from an env var.
- Embeddings: `intfloat/multilingual-e5-small` with sentence-transformers and CPU-only torch;
  fastembed is the fallback. See `docs/adr/0001-embeddings.md` (proposed).
- The extraction and tokenization pipeline is language-independent: Unicode normalization and
  Unicode-aware tokens, with no language-specific stemming.
- Advanced retrieval: dense search first, then BM25 + dense fused with Reciprocal Rank Fusion. No reranker.
- Indexing runs synchronously on save (no Celery). Storage is SQLite + Chroma.
- Dependencies: install intentionally into the clean `roshan-rag` env, then
  `python -m pip freeze > requirements.txt` gives a full snapshot shared by local and Docker.
  Regenerate it after every intentional change and re-verify. pip-tools/uv are postponed.
  The env has `PYTHONNOUSERSITE=1` so `~/.local` packages can't leak in.
  Torch needs the CPU wheel index in Docker (Task 4).

## Unresolved issues / open questions
- Document language is unknown, so we design for English + Persian. The assessment brief
  (`docs/پروژه LLM.pdf`) is written in Persian, so Persian test documents are likely; sample data will include both.
- The brief says the API must "at minimum include the following:" but the list is empty. We'll cover
  document CRUD, ask, and history, and mention this in the README.
- Measure the real Docker image size and cold-start time with torch in Task 2/4. If it's above about 2.5 GB
  or the build is too slow, switch to fastembed.

## Next task
Task 1b: media storage settings, `file` max_length migration (0002), Admin registration.

## Task 1 sub-steps
- 1a ✅ env-based settings (`ImproperlyConfigured` on a missing key, `except KeyError ... from None`), `documents` app, `Document` model, migration 0001, MEDIA_ROOT (accepted 2026-11-07)
- 1b ⬜ MEDIA_URL (MEDIA_ROOT already set in 1a), `file` max_length=255 via migration 0002, ModelAdmin, superuser, upload tests
- 1c ⬜ DOCX extraction + where it hooks in (design decision)

## Schedule adjustments
- Task 0 overran (~2h vs 40m: foundations teaching + user-site leak). Default response: shrink Task 8 to the tests that matter most (RRF, index sync, ask API with a mocked LLM); docs/ZIP stay on Day 2.

## Incident log
- **2026-11-06, user site-packages leak.** `pip freeze` in `roshan-rag` listed langchain 0.2.11,
  langchain-ibm and watsonx packages that aren't in the env. Root cause: `~/.local/lib/python3.12/site-packages`
  (from older `pip install --user` runs) sits on `sys.path` *before* the env's site-packages,
  so it shadows newer versions (packaging 24.2 shadowed 26.3). It would have shadowed LangChain 1.x
  and polluted the Docker requirements. Fix: set `PYTHONNOUSERSITE=1` as an env var on the conda env.

## Interview question bank
_(filled per accepted component)_

## Knowledge gaps
- QuerySet evaluation: knows iteration triggers the query; still needs the full path (Query object → SQL compiler → cursor → model instances), the other triggers (`list`, `len`, `bool`, slicing, `repr`), and result caching.
