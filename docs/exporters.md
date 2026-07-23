# Exporters

`ai-release-metadata` is designed to be an observability "glue" layer rather than a standalone backend. It seamlessly exports the unified `ReleaseContext` to your existing tools.

## Implemented Exporters

### OpenTelemetry
The OpenTelemetry integration uses the **Span Enrichment** pattern. Instead of generating a new span (which clutters trace views), it simply appends the release context to the currently active span.

**Usage:**
```python
from ai_release_metadata.integrations.opentelemetry import enrich_span

with tracer.start_as_current_span("generate_response"):
    with release_context(model="gpt-4o"):
        enrich_span()
```

#### The Span Processor Pattern (Auto-Instrumentation)
If you rely heavily on OpenTelemetry auto-instrumentation (e.g. FastAPI, HTTPX, OpenAI SDK integrations), you can avoid calling `enrich_span()` manually by registering the provided `ReleaseMetadataSpanProcessor`. This interceptor automatically injects the active release metadata into *every* auto-instrumented span that starts within a `release_context` block.

**Usage:**
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from ai_release_metadata.integrations.opentelemetry import ReleaseMetadataSpanProcessor

provider = TracerProvider()
provider.add_span_processor(ReleaseMetadataSpanProcessor())
trace.set_tracer_provider(provider)
```

### Structlog
The Structlog integration is implemented as a standard **Log Processor**. It intercepts log events and appends the serialized context under the `ai` key.

**Usage:**
```python
from ai_release_metadata.integrations.structlog import structlog_processor

processors = [
    structlog.processors.TimeStamper(fmt="iso"),
    structlog_processor, # Automatically injects release metadata
    structlog.processors.JSONRenderer(),
]
```

## Planned Exporters

The following exporters are planned for future releases. If you wish to implement one, refer to the `Exporter` protocol in `ai_release_metadata/integrations/base.py`.

- **Python Standard Logging:** A custom `logging.Filter` to inject the `ai` dictionary into standard `logging` library log records.
- **Direct Vendor Exporters:** Push-based exporters for platforms like Langfuse, Datadog, or Braintrust to bypass OpenTelemetry overhead if desired.
