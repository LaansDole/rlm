# Product Requirements Document
## Title
Local OpenAI-Compatible Support for `rlm` with LM Studio and `examples/`

## Background
`rlm` should run locally against OpenAI-compatible providers, with LM Studio as the first-class target. The immediate goal is to make OpenAI-based examples run end-to-end locally using a local model (`qwen/qwen-8b`), while leaving non-OpenAI backend examples unchanged and clearly out of scope.

## Problem Statement
Today, users who want to run `rlm` locally with LM Studio/OpenAI-compatible endpoints face friction in configuration and example execution. This limits local development, offline testing, and reproducibility for contributors.

## Goals
1. Enable local execution of `rlm` with LM Studio via `.env`-based configuration.
2. Ensure all OpenAI-based examples in `examples/` run locally end-to-end.
3. Preserve non-OpenAI examples as-is (Anthropic/Gemini/etc.) and document scope boundaries.
4. Keep model handling pass-through (no strict OpenAI model validation), validated with `qwen/qwen-8b`.
5. Maintain code quality gates:
   - `uv run ruff check --fix .`
   - `uv run ruff format .`
   - `uv run pytest`

## Non-Goals
1. Converting non-OpenAI backend examples to OpenAI-compatible in this effort.
2. Building provider auto-discovery or dynamic model catalog sync.
3. Introducing a new dedicated local CLI mode (unless needed later).

## Target Users
1. Contributors developing `rlm` locally.
2. Users running local inference stacks (LM Studio first, other OpenAI-compatible endpoints secondary).
3. Example-driven evaluators validating `rlm` behavior without cloud dependency.

## Scope
### In Scope
1. `.env` configuration path for local OpenAI-compatible endpoint usage.
2. OpenAI-compatible support aligned to whatever API surface the current OpenAI examples use (chat/responses as actually required by examples).
3. Example compatibility updates where small code/config changes are necessary.
4. Documentation updates for local setup and known boundaries.

### Out of Scope
1. Reworking non-OpenAI examples.
2. Broad refactor of client architecture not required for local compatibility.
3. Strict model-name validation against OpenAI cloud model lists.

## Functional Requirements
1. **Environment-based local configuration**
   - Support `.env`-driven setup (e.g., `OPENAI_BASE_URL`, `OPENAI_API_KEY`, model setting used by project conventions).
   - Local usage should not require new CLI flags.

2. **LM Studio first-class compatibility**
   - LM Studio endpoint must work as the primary tested path.
   - Document a known-good LM Studio config using `qwen/qwen-8b`.

3. **Examples compatibility**
   - All OpenAI-based examples in `examples/` run locally end-to-end.
   - If an example currently targets a non-OpenAI backend, it remains unchanged and explicitly documented as out of scope.
   - Small code/config changes in OpenAI-based examples are acceptable where necessary.

4. **API surface alignment**
   - Support whichever OpenAI-compatible endpoint behavior is currently exercised by OpenAI examples.
   - If examples span multiple OpenAI API styles, support all required by those examples.

5. **Model handling**
   - Pass-through model name behavior; allow unknown model IDs.
   - No strict OpenAI cloud model validation.
   - Test baseline model: `qwen/qwen-8b`.

## Non-Functional Requirements
1. Fail-fast error behavior on missing required config (consistent with repo philosophy).
2. Minimal branching and surgical diff footprint.
3. No regression for existing cloud OpenAI path.
4. Deterministic tests where feasible.

## User Stories and Acceptance Criteria

### US1: Local `.env` setup for LM Studio
As a developer, I can configure `rlm` for LM Studio in `.env` and run OpenAI-based flows locally.

**Acceptance Criteria**
1. A documented `.env` setup exists for LM Studio.
2. Missing/invalid critical config fails loudly with actionable error.
3. Local run path works without requiring new CLI-only setup.

### US2: OpenAI-based examples run locally end-to-end
As a user, I can run all OpenAI-based examples locally against LM Studio.

**Acceptance Criteria**
1. Every OpenAI-based example in `examples/` completes end-to-end with local OpenAI-compatible endpoint.
2. Validation is performed using `qwen/qwen-8b`.
3. Any required example changes are minimal and documented.

### US3: Non-OpenAI examples remain unchanged
As a maintainer, I keep non-OpenAI backend examples stable and out of scope.

**Acceptance Criteria**
1. Anthropic/Gemini/other non-OpenAI examples are not converted in this PRD scope.
2. Docs clearly distinguish OpenAI-local-compatible vs non-OpenAI examples.

### US4: Quality gates pass for all changes
As a maintainer, I ensure code quality and test stability.

**Acceptance Criteria**
1. `uv run ruff check --fix .` passes.
2. `uv run ruff format .` passes.
3. `uv run pytest` passes.

## Implementation Plan (Multi-PR Breakdown)

### PR1: Config + Client Compatibility Baseline
- Confirm/implement `.env` loading path for OpenAI-compatible base URL/key/model in existing conventions.
- Ensure OpenAI client passes base URL and model through without strict cloud-model validation.
- Add/adjust fail-fast config validation and error messages.
- Add/update unit tests around local config and pass-through model behavior.

### PR2: Examples Enablement
- Audit `examples/` and identify OpenAI-based subset.
- Apply minimal code/config updates to ensure local endpoint compatibility.
- Validate each OpenAI-based example end-to-end with LM Studio + `qwen/qwen-8b`.
- Keep non-OpenAI examples untouched; annotate scope in docs/readme.

### PR3: Documentation + Final Verification
- Add a concise “Run locally with LM Studio” section.
- Include `.env` template, launch steps, and troubleshooting.
- Document support boundary for non-OpenAI examples.
- Run full quality gates and finalize compatibility matrix.

## Dependencies
1. Running LM Studio instance exposing OpenAI-compatible endpoint.
2. Local model availability: `qwen/qwen-8b`.
3. Existing OpenAI client path in `rlm` and current example wiring.

## Risks and Mitigations
1. **Risk:** API mismatch between LM Studio and current OpenAI usage.
   - **Mitigation:** Align support to actual API calls used by examples; add targeted tests.
2. **Risk:** Examples use mixed backend assumptions.
   - **Mitigation:** Explicitly classify examples by backend and scope only OpenAI-based ones.
3. **Risk:** Hidden regressions in cloud OpenAI path.
   - **Mitigation:** Keep changes minimal; include regression checks/tests.

## Success Metrics
1. 100% of OpenAI-based examples in `examples/` pass locally end-to-end with LM Studio.
2. Zero required changes to non-OpenAI examples.
3. All quality gates pass (`ruff check`, `ruff format`, `pytest`).
4. New contributor can set up and run local OpenAI-compatible flow using docs only.

## Verification Checklist
1. Start LM Studio and load `qwen/qwen-8b`.
2. Configure `.env` for local endpoint and key.
3. Run OpenAI-based examples end-to-end.
4. Run:
   - `uv run ruff check --fix .`
   - `uv run ruff format .`
   - `uv run pytest`
5. Confirm non-OpenAI examples are unchanged and documented as out of scope.

## Open Decisions (to resolve during implementation)
1. Exact env var names for model selection if multiple conventions currently exist.
2. Whether any OpenAI-based example implicitly depends on cloud-only behavior and needs a minimal local guard/documentation note.