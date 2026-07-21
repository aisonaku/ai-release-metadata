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
* **Application-level Instrumentation:** Instruments business operations instead of wrapping LLM SDKs, allowing the library to remain provider-agnostic.
* **Automatic Metadata Discovery:** Detects release and runtime information from the execution environment through a pluggable metadata system.
* **Integrations:** Natively exports into `structlog` (JSON logs) and OpenTelemetry.
* **Async First:** Safe to use in high-throughput `asyncio` applications such as FastAPI.

## Usage

Configure the SDK once at application startup using the `MetadataProvider`:

```python
from ai_release_metadata import MetadataProvider
from ai_release_metadata.plugins.env import EnvPlugin

MetadataProvider(plugins=[EnvPlugin()])
```

Use the context manager (`release_context`) or decorator (`@capture_generation`) within the business logic:

```python
from ai_release_metadata import release_context, get_current_context

async def generate_response(user_id: str, query: str):
    # Start a release context block
    with release_context(feature="customer-support", model="gpt-4o", prompt_version="v2.1"):
        
        # ... LLM calling logic ...
        
        # Dynamically append runtime information to the context
        ctx = get_current_context()
        if ctx:
            ctx.retrieved_documents = ["doc_1", "doc_2"]
```

All logs emitted within the `with release_context(...)` block will automatically have the metadata appended under the `ai` key.

### OpenTelemetry Integration

If you use OpenTelemetry, you can automatically enrich the currently active span with the release context. It gracefully ignores spans if none are active.

```python
from ai_release_metadata.integrations.opentelemetry import enrich_span
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("generate_response") as span:
    with release_context(model="gpt-4o"):
        # Enrich the span with git_sha, environment, model, etc.
        enrich_span()
        
        # ... LLM calling logic ...
```

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
