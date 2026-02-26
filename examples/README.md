# Examples

This directory contains examples of running RLM with different environments and providers.

## Usage Overview

Most examples use a mock or non-OpenAI backend by default (like `PortkeyClient` or `MockLM`). These examples will not attempt to read from `OPENAI_BASE_URL` or `OPENAI_API_KEY`, because they deliberately demonstrate alternative integrations and their scopes remain unchanged.

### Non-OpenAI / Mock Scope
The following examples are intentionally scoped to **non-OpenAI backends** or use mock configurations to demonstrate specific abstractions:

- `quickstart.py` (Portkey)
- `compaction_example.py` (Portkey)
- `compaction_history_retrieval_example.py` (Portkey)
- `custom_tools_example.py` (Portkey)
- `depth_metadata_example.py` (Portkey)
- `rlm_query_batched_example.py` (Portkey)
- `lm_in_repl.py` (Portkey)
- `lm_in_prime_repl.py` (Portkey)
- `logger_example.py` (Portkey)
- `daytona_repl_example.py` (MockLM)
- `docker_repl_example.py` (MockLM)
- `modal_repl_example.py` (MockLM)

### OpenAI-Compatible Scope
The following examples are configured to use the **OpenAI Client**, which natively supports standard OpenAI models as well as local endpoints running OpenAI-compatible providers:

- `e2b_repl_example.py`
- `prime_repl_example.py`

---

## Local Development with LM Studio

The OpenAI-Client natively supports overriding the base URL and API key via `.env` files. This means you can run the OpenAI-compatible examples listed above completely locally using a local endpoint like [LM Studio](https://lmstudio.ai/) without changing code headers.

### 1. LM Studio Setup
1. Download, install, and open LM Studio.
2. Search and download a model, for example `qwen/qwen-8b` or `meta-llama-3-8b`.
3. Open the **Local Server** tab.
4. Ensure the server is started and running on `http://localhost:1234/v1`.
5. Ensure the CORS and pass-through settings are enabled to accept incoming requests.

### 2. Configure Environment (`.env`)
Create a `.env` file in the root directory (or where you launch your script) with your LM Studio configuration:

```env
OPENAI_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=lm-studio
OPENAI_MODEL=qwen/qwen-8b
```
*(LM Studio accepts any string for the API key).*

### 3. Run an Example
Once your `.env` is configured and LM Studio is running, you can run any of the OpenAI-compatible examples. The client will automatically discover your `.env` variables and route requests locally.

```bash
uv run python examples/e2b_repl_example.py
```

### Troubleshooting
- **Missing API Key Error**: Ensure `OPENAI_API_KEY` is set in your `.env`. Even if your local endpoint does not enforce authentication, the underlying Python OpenAI Client explicitly requires the key formatting to be present.
- **Connection Refused**: Confirm LM Studio Local Server is running and listening on port `1234`. The endpoint should explicitly end in `/v1`.
- **Unexpected Output**: Local models might hallucinate or struggle with complex JSON. A stronger model like `qwen/qwen-8b` or greater is recommended for consistent execution.
