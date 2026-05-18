---
name: VI. Test-Backed Confidence
---

New domain functionality MUST include corresponding test coverage under `src/tests/`. Tests MUST be runnable via `uv run pytest` and MUST use `pytest-asyncio` for async code. External HTTP interactions MUST be recorded using VCR cassettes (`pytest-recording`) to ensure deterministic CI. Test utilities MUST use `pytest-mock` rather than `unittest.mock`. Coverage reports MUST be generated on every test run. Rationale: Regression prevention, deterministic CI, and confidence in refactoring.
