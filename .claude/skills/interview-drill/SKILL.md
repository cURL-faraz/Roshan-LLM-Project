---
name: interview-drill
description: Interactive technical interview practice for a component the user has implemented, plus final 10-minute presentation preparation. Use after a component is accepted or when the user asks to practice.
---

# Interview Drill

1. Pick the component (default: the most recently accepted one in `PROGRESS.md`).
2. Prepare questions at three levels:
   - **Fundamentals** (what is BM25? what is an embedding?)
   - **Implementation / architecture** (why does the service layer own indexing? why
     Chroma?)
   - **Trade-offs / reliability / failure** (what if the LLM times out? how does deletion
     keep the index in sync? how would this scale to 1M documents?)
3. Ask **one question at a time**. Wait for the user's answer. Do not show model answers
   first.
4. Evaluate: correct / partially correct / incorrect, what was missing, and a sharper way
   to say it. Ground answers in the *actual* code, not generic theory.
5. Add weak topics to "Knowledge gaps" in `PROGRESS.md`; remove them once answered well.

## Final presentation mode
Build a 10-minute outline from the real implementation: problem → architecture diagram →
document lifecycle → retrieval strategy and why → grounding → Docker → demo script →
limitations and next steps. Then run a mock Q&A.
