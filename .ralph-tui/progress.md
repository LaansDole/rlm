# Ralph Progress Log

This file tracks progress across iterations. Agents update this file
after each iteration and it's included in prompts for context.

## Codebase Patterns (Study These First)

*Add reusable patterns discovered during development here.*

- Normalize optional config dicts at module boundaries (for example, `backend_kwargs = backend_kwargs or {}` in client routing) so env-driven defaults can work without callers passing explicit kwargs.

---

## 2026-02-26 - US-001
- What was implemented
  - Added .env-driven OpenAI client defaults for `OPENAI_BASE_URL`, `OPENAI_API_KEY`, and model env conventions (`OPENAI_MODEL`, `OPENAI_MODEL_NAME`, `RLM_MODEL_NAME`, `MODEL_NAME`).
  - Added fail-fast validation for missing API key and invalid base URL with actionable error messages.
  - Updated OpenAI model-missing errors to point developers to `backend_kwargs['model_name']` and supported env vars.
  - Allowed `get_client("openai", None)` by normalizing missing backend kwargs to `{}`.
- Files changed
  - `rlm/clients/openai.py`
  - `rlm/clients/__init__.py`
  - `tests/clients/test_openai.py`
  - `.ralph-tui/progress.md`
- **Learnings:**
  - Patterns discovered
    - The OpenAI client is a shared compatibility layer for OpenAI-compatible providers; provider-specific key env selection should branch from resolved base URL.
    - Existing call paths can pass `backend_kwargs=None`, so client routing should normalize optional dicts early.
  - Gotchas encountered
    - `load_dotenv()` happens at import time, but reading env values at client init is more robust for tests that patch `os.environ`.
---
