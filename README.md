# AI Release Metadata (ai-release-metadata)

> **The SDK standardizes and propagates AI release metadata across engineering systems. It does not collect, store, analyze, or visualize that metadata.**

A lightweight, framework-agnostic Python SDK for standardizing AI release metadata across production applications.

## The Problem

When a production issue occurs in an AI-powered service (e.g., bad generation, regressions, prompt injection), it is often extremely difficult to quickly identify:
* Which prompt version generated the response?
* Which model was used?
* Which Git commit or deployment version is responsible?
* What experiments were active?

While existing observability platforms effectively capture execution metrics such as latency and token usage, manually correlating these spans back to the underlying release lifecycle often results in fragmented and inconsistent metadata.

## The Solution

This SDK provides a minimal set of context managers and decorators that automatically enrich existing logs, metrics, and traces with standardized release and environment metadata.

### Features
* **Zero Magic Wrapping:** Avoids wrapping underlying LLM clients, opting instead to wrap the application's business logic.
* **Auto-Extraction:** Automatically extracts CI/CD variables (`GIT_COMMIT`, `ENVIRONMENT`, `DD_VERSION`) at startup via a `Plugins` system.
* **Integrations:** Natively exports into `structlog` (JSON logs) and OpenTelemetry (planned).
* **Async First:** Safe to use in high-throughput `asyncio` applications such as FastAPI.

## Usage

Configure the SDK once at application startup using the `MetadataProvider`:

```python
from ai_release_metadata import MetadataProvider
from ai_release_metadata.plugins.env import EnvPlugin

MetadataProvider(plugins=[EnvPlugin()])
```

Use the context manager (`ai_trace`) or decorator (`@trace_generation`) within the business logic:

```python
from ai_release_metadata import ai_trace, get_current_trace

async def generate_response(user_id: str, query: str):
    # Start a trace block
    with ai_trace(feature="customer-support", model="gpt-4o", prompt_version="v2.1"):
        
        # ... LLM calling logic ...
        
        # Dynamically append runtime information to the trace
        trace = get_current_trace()
        if trace:
            trace.retrieved_documents = ["doc_1", "doc_2"]
```

All logs emitted within the `with ai_trace(...)` block will automatically have the metadata appended under the `ai` key.

## Running the Demo

This repository includes a FastAPI demo simulating a generation endpoint.

1. Activate a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install structlog fastapi uvicorn pydantic
```

2. Run the application:
```bash
export GIT_COMMIT=a1b2c3d 
export ENVIRONMENT=local 
export LOG_FORMAT=console
PYTHONPATH=. uvicorn demo.app:app
```

3. Send a request to observe the enriched telemetry in the terminal:
```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o", "prompt_version": "v2.0", "user_query": "I cannot login"}'
```
