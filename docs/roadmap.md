# Roadmap

This document outlines future development ideas and planned features for `ai-release-metadata`.

## Core SDK Features

1. **Auto-Discovery Enhancements:** 
   - Expand built-in plugins for more CI/CD environments (GitLab CI, CircleCI, Vercel).
   - Add built-in discovery for AWS EC2/ECS and GCP metadata services.

2. **Configuration from File:**
   - Allow initializing the `MetadataProvider` via a `pyproject.toml` or `ai-release.yaml` configuration file rather than purely programmatic injection.

## Exporters

1. **Datadog Native Exporter:**
   - While OpenTelemetry exports to Datadog perfectly, some users prefer pushing directly to the Datadog API via the native `ddtrace` Python SDK. A dedicated `DatadogExporter` would bypass the OTEL collector overhead.
   
2. **Langfuse / Braintrust Exporters:**
   - Dedicated exporters to push release context natively into popular LLM evaluation platforms.

3. **Standard Logging Filter:**
   - A `logging.Filter` to automatically append the `ai` context dictionary to Python's standard `logging` library output.

## Framework Auto-Instrumentation

1. **FastAPI Middleware:**
   - Provide a drop-in ASGI middleware for FastAPI that automatically wraps every incoming request in a `release_context` boundary, deriving the `feature` name from the FastAPI route automatically.

2. **Celery Integration:**
   - Ensure the `contextvars` propagate safely across Celery task boundaries using task signals.
