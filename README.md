# AI Release Metadata (ai-release-metadata)

> **A lightweight SDK for standardizing and propagating operational metadata for AI-powered services through existing observability systems.**

## The Problem

When a production issue occurs in an AI-powered service (e.g., regressions, prompt injection, or unexpected model behaviour), it is often extremely difficult to quickly identify:
* Which prompt version, model, deployment, or source revision was associated with this request?
* What experiments were active?

While existing observability platforms effectively capture execution metrics such as latency and token usage, manually correlating these spans back to the exact release configuration often results in fragmented and inconsistent metadata.

## The Solution

This SDK provides a minimal set of context managers and decorators that automatically enrich existing logs, metrics, and traces with standardized release and environment metadata.

### Architecture

```mermaid
flowchart TD
    App[Application] -->|with release_context()| Provider[MetadataProvider]
    Provider -->|extract| Plugins["Plugins (Git, Env)"]
    Plugins --> Context(("Release Context"))
    Context -->|get_current_context()| Exporters["Exporters"]
    Exporters --> OTEL["OpenTelemetry / Structlog"]
```

### Design Principles
- **Minimal developer overhead:** Drop-in context managers and decorators.
- **Existing Observability First:** Integrates directly into your current logging/tracing pipelines instead of requiring a new dashboard.
- **A reusable building block:** This explores one reusable approach for improving traceability between production behaviour and deployed AI releases.
- **Framework agnostic:** Works with FastAPI, Django, or raw scripts.
- **Vendor agnostic:** Does not wrap or depend on specific LLM provider SDKs.
- **Explicit over magic:** Developers explicitly define trace boundaries.
- **Existing observability first:** Propagates metadata to your existing tools (like OpenTelemetry) rather than acting as a standalone backend.
- **Async-safe by default:** Thread-safe and async-safe context propagation.

### Features
* **Automatic Infrastructure Metadata Discovery:** Detects deployment metadata such as Git revision, CI/CD information, and environment configuration through pluggable collectors.
* **Application Metadata Propagation:** Standardizes and propagates AI-specific metadata—such as model, prompt version, feature name, or experiment ID—provided by the application or optional framework integrations.
* **Application-level Instrumentation:** Instruments business operations instead of wrapping LLM SDKs, allowing the library to remain provider-agnostic.
* **Integrations:** Natively exports into `structlog` (JSON logs) and OpenTelemetry.
* **Async First:** Safe to use in high-throughput `asyncio` applications such as FastAPI.

## Use Cases

### 1. Diagnosing Latency Regressions by Git Commit
If latency spikes on a specific LLM feature, you can query Datadog/Grafana for all `generate` traces grouped by `ai.git_sha`. The SDK ensures this metadata is accurately attached to every span, instantly identifying the deployment that caused the regression.

### 2. A/B Testing Prompt Templates
When rolling out a new prompt (e.g. `prompt_version="v2.1"`), you can seamlessly track the token usage, error rates, and user feedback specifically for that variant.

## Documentation

- [Architecture](docs/architecture.md): How context propagation works under the hood.
- [Design Decisions](docs/design-decisions.md): The rationale behind the core architectural choices.
- [Metadata Schema](docs/metadata-schema.md): The full list of supported fields.
- [Plugin Development](docs/plugin-development.md): How to build custom discovery sources.
- [Exporters](docs/exporters.md): How to export data to OpenTelemetry, structlog, and more.
- [Roadmap](docs/roadmap.md): Future development ideas and planned integrations.

## Installation

```bash
pip install ai-release-metadata
```

To enable the OpenTelemetry integration automatically, install the `otel` extra:
```bash
pip install "ai-release-metadata[otel]"
```

## Usage

Configure the SDK once at application startup using the `MetadataProvider`. 

**Plugin Precedence Rules:** The SDK resolves metadata conflicts based on the order plugins are provided. The *last* plugin evaluated takes precedence over the preceding ones. We recommend putting local plugins first, and explicit environment plugins last.

```python
from ai_release_metadata import MetadataProvider
from ai_release_metadata.plugins import EnvPlugin, GitPlugin, GitHubActionsPlugin

# 1. GitPlugin tries to guess from local filesystem
# 2. GitHubActionsPlugin overwrites with CI variables
# 3. EnvPlugin overwrites with explicit user-defined env vars
MetadataProvider(plugins=[GitPlugin(), GitHubActionsPlugin(), EnvPlugin()])
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
            ctx.add_document("doc_1")
            ctx.add_tag("user_tier", "premium")
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
