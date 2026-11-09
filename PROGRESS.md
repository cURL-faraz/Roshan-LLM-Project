# PROGRESS

## Current stage
**Stage 2: Task 7 (BM25 + RRF hybrid retrieval, duplicate handling).** Day 1 started 2026-11-06 18:12. Budget: about 7 focused hours.
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
| 1 | `documents` app: env-based settings, `Document` model, Admin, DOCX extraction on save | M1 | 60m | ~3h | ✅ |
| 2 | Minimal Dockerfile + compose; volume persistence test (SQLite + media) | M1 | 40m | ~45m | ✅ |
| 3 | OpenRouter smoke test: ChatOpenRouter, model availability, timeout and error handling | M1 | 25m | ~70m | ✅ |
| 4 | `rag/`: chunking, E5 embeddings (with prefixes), Chroma indexing; sync on save/delete | M1 | 75m | ~2h | ✅ |
| 5 | `qa` app: `QARecord`, dense retrieve → prompt → generate, `POST /api/ask/` | M1 | 70m | not timed | ✅ |
| — | **M1 check: full flow inside Docker Compose** | M1 | 10m | | ⬜ |
| 6 | DRF documents CRUD API (upload, edit, delete) + history endpoint | M2 | 35m | not timed | ✅ |
| 7 | BM25 retriever + RRF fusion (user writes RRF) + duplicate handling | M2 | 50m | | 🟨 |
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
- Chat LLM: OpenRouter through `langchain-openrouter` (`ChatOpenRouter`); model id, key, timeout from env (`OPENROUTER_MODEL`, default `nvidia/nemotron-3.5-lightning:free` (gemma-4 free returned 429 upstream on 2026-11-08; nemotron answered Persian in ~2–3s); free-model list changes, so it's configurable). Factory `rag/llm.build_chat_model` returns `BaseChatModel` so the pipeline is provider-agnostic. Errors: `langchain-openrouter` 0.2.9 does NOT translate to `langchain_core.exceptions`; it raises `openrouter.errors.*` (base `OpenRouterError`): 401 `UnauthorizedResponseError`, 400 `BadRequestResponseError` (unknown model), 429 `TooManyRequestsResponseError`.
- Embeddings: `intfloat/multilingual-e5-small` with sentence-transformers and CPU-only torch;
  fastembed is the fallback. See `docs/adr/0001-embeddings.md` (proposed).
- The extraction and tokenization pipeline is language-independent: Unicode normalization and
  Unicode-aware tokens, with no language-specific stemming.
- Advanced retrieval: dense search first, then BM25 + dense fused with Reciprocal Rank Fusion. No reranker.
- BM25 (2026-11-09): `rank_bm25.BM25Okapi`, rebuilt per query from `store.get()`, so Chroma stays the single copy and no invalidation is needed (fine at this corpus size). Okapi over BM25Plus because scores > 0 mean a real term match; Plus gave all 23 chunks a positive score. Consequence: in a tiny corpus a term in half or more of the chunks scores <= 0, and dense search covers it. Persian character and digit folding is applied, but no stemming or stopwords.
- Extraction happens at form/serializer validation time through a pure function in `rag/extraction.py`, so an invalid DOCX is rejected with a validation error before any file is written. Admin and the API share the function.
- Indexing runs synchronously on save (no Celery). Storage is SQLite + Chroma.
- Dependencies: install intentionally into the clean `roshan-rag` env, then
  `python -m pip freeze > requirements.txt` gives a full snapshot shared by local and Docker.
  Regenerate it after every intentional change and re-verify. pip-tools/uv are postponed.
  The env has `PYTHONNOUSERSITE=1` so `~/.local` packages can't leak in.
  Torch needs the CPU wheel index in Docker (Task 4).

## Unresolved issues / open questions
- **Task 5 conceptual checkpoint still open.** Behavior accepted 2026-11-09, but the user hasn't yet explained the `/api/ask/` flow in their own words. Do this before the Task 5 interview drill.
- **Citation digits (known limitation).** The model still writes `[۱]` in Persian answers despite the Western-digits rule. Harmless unless citations get linked to `sources`.
- **Regression test for Task 8:** a blank LLM reply raises `GenerationError`. Also keep the off-topic hijack question as a test case.
- **Task 6 prediction question still open:** which step rejects a `.zip`, which rejects a fake `.docx`, and why.
- **API root (accepted limitation):** `GET /api/` lists only `history`, because two `DefaultRouter`s share the `api/` prefix. User chose to leave it.
- **M1 check in Docker still not done.** It was planned before Task 6 and has been pushed back, so run it no later than after Task 7.
- Document language is unknown, so we design for English + Persian. The assessment brief
  (`docs/پروژه LLM.pdf`) is written in Persian, so Persian test documents are likely; sample data will include both.
- The brief says the API must "at minimum include the following:" but the list is empty. We'll cover
  document CRUD, ask, and history, and mention this in the README.
- Measure the real Docker image size and cold-start time with torch in Task 2/4. If it's above about 2.5 GB
  or the build is too slow, switch to fastembed.

## Next task
Task 7: `rag/sparse.py` (tokenize, BM25), `rag/fusion.py` (RRF), hybrid `retrieve`. Then the M1 check in Docker.

## Task 1 sub-steps
- 1a ✅ env-based settings (`ImproperlyConfigured` on a missing key, `except KeyError ... from None`), `documents` app, `Document` model, migration 0001, MEDIA_ROOT (accepted 2026-11-07)
- 1b ✅ migration 0002 (AlterField + rollback experiment), DocumentAdmin, superuser, upload/validation verified (accepted 2026-11-07; MEDIA_URL fix confirmed in 1c)
- 1c ✅ `rag/extraction.py` (pure, Django-free; catches BadZipFile/PackageNotFoundError/KeyError; filters empty blocks at source) + `DocumentAdminForm.clean_file` (extracts only for a new `UploadedFile`). Verified: Persian/table/English order, fake/zip/empty rejected with form errors, rejected upload leaves nothing in media/, title-only edit keeps text (accepted 2026-11-07). Follow-ups: add `from exc` in clean_file; merged cells duplicate text (known limitation).

- 2 ✅ `python:3.12-slim`, requirements layer before source, `.dockerignore` (secrets/state/caches), compose with `env_file`, named volumes `data`/`media`, `migrate && runserver 0.0.0.0:8000`, host port bound to `127.0.0.1`. Verified: Admin works in container, data (1 doc, 1 user) survives `down`/`up`, no `.env` in `/app`. Image 198 MB before torch (accepted 2026-11-08).

- 3 ✅ `rag/llm.build_chat_model` (seconds→ms at the boundary), `scripts/smoke_llm.py`: Persian answer, 9.6 s for 1209 output tokens (latency scales with output length → cap `max_tokens`/ask for concise answers in Task 5), invalid key → `UnauthorizedResponseError` (accepted 2026-11-08).

- 4a ✅ `rag/chunking.py` (800/120 chars, sentence separators kept at chunk end, deterministic ids), `rag/vectorstore.py` (E5 prefixes, normalized, cosine). Verified: 384 dims, norm 1.0, no duplicates on re-index, Persian and English queries at dist 0.165/0.178 (accepted 2026-11-08). Multi-chunk ranking still to be checked on a longer document in 4b.

- 4b ✅ `rag/pipeline.py` + `post_save`/`post_delete` signals with `transaction.on_commit(robust=True)`. Verified in Admin: long file 22 chunks, title edit stays 22, file swap drops to 1, bulk delete removes all (accepted 2026-11-08).

## Schedule adjustments
- Task 1 overran (~3h vs 60m: Django/forms/DOCX teaching + exception debugging). Task 8 shrinks further; keep Task 2 strictly minimal.
- Task 0 overran (~2h vs 40m: foundations teaching + user-site leak). Default response: shrink Task 8 to the tests that matter most (RRF, index sync, ask API with a mocked LLM); docs/ZIP stay on Day 2.

## Incident log
- **2026-11-09, off-topic question hijacked by document text.** "Capital of France?" sometimes returned a Persian or Chinese answer about Langfuse, because chunk 16 of `systemPrompt` holds a `User:` example and the prompt had no boundary around the context. Evidence, 3 runs per variant on the free model: current prompt 1/3 correct, newline fix only 1/3, newline + `<context>` delimiters 3/3. Small sample; delimiters reduce this risk, they don't remove it. Earlier passes were partly luck, so run prompt tests more than once.

- **2026-11-09, empty and truncated answers from `/api/ask/`.** Root cause: nemotron is a reasoning model, and reasoning tokens count against `max_tokens`. With the mentor-suggested 800, a Persian question used all 800 on reasoning (`finish_reason=length`, 0 content chars); with 3000 the same call used 893 on reasoning and returned a full answer. Reasoning cost varies per call (685-893 observed). Lesson: `max_tokens` is the total output budget, and an empty string is a failure the code must detect, since `StrOutputParser` hides `finish_reason`.

- **2026-11-08, 500 on Admin save during indexing (two causes).** (1) Document 1 predates extraction, so its `extracted_text` is empty; a title edit doesn't re-extract, so `chunk_text` returned `[]` and Chroma rejects an empty upsert (`ValueError`). Fix: return early when there are no chunks. (2) `robust=True` should have logged that error, but Django's logger reads `func.__qualname__`, which `functools.partial` lacks (`AttributeError`). Mentor's template suggested `partial`. Fix: copy values into locals, pass a `lambda` (it has `__qualname__`).

- **2026-11-08, HF model load PermissionError.** `~/.cache` is owned by root with mode 700 (from an earlier sudo run; dated Jul 30), so the Hugging Face library can't read its token file or write its cache. Code was fine: the check passes with a writable `HF_HOME`. Fix: chown `~/.cache` back to the user.

- **2026-11-08, pydantic conflict after Task 4 install.** Installing chroma/HF stack upgraded pydantic to 2.14.3, violating `openrouter`'s `pydantic<2.13`. Cause: pip resolves only the packages being installed, not the whole env. Fix: `pip install "pydantic>=2.11.2,<2.13"` (→ 2.12.5), then `pip check`, re-run smoke test, then freeze. The real source was `kubernetes` 37 (pulled by chromadb, needs `pydantic>=2.14.2`); fixed by pinning `kubernetes==35.0.0` (chromadb accepts `>=28.1.0`, no pydantic requirement). `pip check` clean, smoke test re-passed, requirements refrozen. Rule: always `pip check` before `pip freeze`.
- **2026-11-08, smoke test hangs ~5 min with no output.** Root cause: `ChatOpenRouter(timeout=...)` is in **milliseconds** (maps to SDK `timeout_ms`); `60` meant 60 ms, so every attempt timed out and the SDK kept retrying with backoff (stack dump showed `openrouter/utils/retries.py: retry_with_backoff`, even with `max_retries=0`). Evidence: same call with `60_000` returned in ~1s. Lesson: check units in the installed source (`model_fields`/docstring), not by assumption.

- **2026-11-06, user site-packages leak.** `pip freeze` in `roshan-rag` listed langchain 0.2.11,
  langchain-ibm and watsonx packages that aren't in the env. Root cause: `~/.local/lib/python3.12/site-packages`
  (from older `pip install --user` runs) sits on `sys.path` *before* the env's site-packages,
  so it shadows newer versions (packaging 24.2 shadowed 26.3). It would have shadowed LangChain 1.x
  and polluted the Docker requirements. Fix: set `PYTHONNOUSERSITE=1` as an env var on the conda env.

- **2026-11-07, wrong exception caught in extraction.** The user's experiment passed a *path*, which gave `PackageNotFoundError`; production passes a *stream*, which gives `zipfile.BadZipFile`. A zip that isn't a DOCX gives `KeyError`. Lesson: run an experiment under the same conditions as production.

## Interview question bank
_(filled per accepted component)_

## Knowledge gaps
- OpenRouter SDK retry budget: time-based, not count-based. Timeouts and 5xx are retried until `max_retries × 150 s` elapses; 429 and 400 fail immediately. Worst-case wait with `max_retries=2` is about 5 minutes, so the API uses `max_retries=1`.
- Container data loss is about *lifecycle*, not isolation: the writable layer dies with the container on `down` (not on `stop`). Any file not in a volume/image is gone; `migrate` then creates a fresh empty DB.
- Form validation order: model-field validators (e.g. `FileExtensionValidator` on the model) run in `_post_clean` → `instance.full_clean()`, i.e. *after* `clean_<field>`; and `FileField` writes bytes to storage during `save()` (`pre_save`), which is the real reason extraction can't wait for `Model.save()`.
- QuerySet evaluation: knows iteration triggers the query; still needs the full path (Query object → SQL compiler → cursor → model instances), the other triggers (`list`, `len`, `bool`, slicing, `repr`), and result caching.
