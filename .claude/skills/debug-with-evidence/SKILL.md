---
name: debug-with-evidence
description: Evidence-driven debugging process for any error, failing test, wrong answer, or unexpected behavior in this project. Use instead of jumping to a fix.
---

# Debug With Evidence

Teach the process, not just the answer. The user applies the fix.

1. **Collect evidence**: exact error, traceback, logs, inputs, what changed recently.
   Reproduce it.
2. **Possible causes**: list them by layer (config/env, Docker, Django, data, LangChain,
   external API).
3. **Hypotheses**: pick the 1–3 most likely, explicitly.
4. **Predictions**: "If H1 is true, then running X will show Y."
5. **Smallest safe experiment**: one read-only or reversible check at a time.
6. **Root cause**: state it plainly, with the evidence that proves it.
7. **Correction**: guide the user to write the fix.
8. **Verify**: rerun the original reproduction.
9. **Regression coverage**: the user adds a test that would have caught it.

Record anything non-obvious in `PROGRESS.md` under "Unresolved issues" or "Decisions".
