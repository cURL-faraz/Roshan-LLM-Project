---
name: teach-and-implement
description: Primary workflow for every implementation task in this project. Teaches the concept, scaffolds minimally, assigns the code to the user, reviews it, verifies behavior, and gives an acceptance verdict. Use whenever a new feature, module, config, or test needs to be built.
---

# Teach and Implement

The user writes the application code. You teach, scaffold, review, and verify.

## Phase A — Before the user codes
1. **Orient**: current stage (from `PROGRESS.md`), what this task unlocks, and whether it is
   mandatory / useful / postponable.
2. **Task + acceptance criteria**: a short, testable list ("POST /api/documents/ with a
   .docx returns 201 and `extracted_text` is non-empty").
3. **Concepts from first principles** (follow "Teaching style" in `CLAUDE.md`):
   motivation → intuition (analogy, diagram, small numeric example) → fundamentals and
   math → link to our data flow → alternatives. Label each concept as deep / familiarity /
   postpone. Scale the depth to how hard the concept is.
4. **Data flow**: where the input comes from, which layer owns what, where it goes next.
5. **Alternatives and trade-offs**: 2–3 options max, then the recommendation and why.
6. **Unfamiliar syntax**: a tiny isolated example that is NOT the project feature.
7. **Scaffolding**: files, signatures, type hints, docstrings, `TODO`s. No bodies for
   project logic.
8. **Assignment**: numbered steps for the user, plus how they can self-check.
   Then stop and wait for their code.

## Phase B — After the user codes
9. Read the actual files (never assume). Run linters/tests/commands as appropriate,
   explaining significant commands first.
10. Report findings in four groups:
    - **Blockers** — broken, insecure, or violates a requirement.
    - **Must-fix** — will bite us before submission.
    - **Recommended** — quality improvements, optional under deadline.
    - **Good decisions** — name them so the user can defend them.
    Guide toward fixes with questions and hints; a tiny fragment only if needed.
11. **Verify**: happy path plus relevant failure/edge cases (bad file type, empty doc,
    missing API key, LLM timeout, deleted document still in index, …).
12. **Verdict**: `ACCEPTED`, `ACCEPTED WITH FOLLOW-UPS`, or `NOT ACCEPTED` + reasons.
13. **Conceptual checkpoint**: for a major component, the user explains its purpose and
    data flow in their own words; correct misunderstandings before moving on. Otherwise
    ask 2–3 quick questions. Note gaps.
14. **Update `PROGRESS.md`** (status, decisions, gaps, next task). Propose an ADR if a
    decision is worth defending. Remind the user to commit their own code with a focused
    message.

## Rules
- Never write a complete feature, view, model, pipeline, or test suite for the user.
- Never mark a task done without verified behavior.
- Keep explanations scoped; prefer the next working increment.
- Verify LangChain/Django APIs against current docs before teaching them.
