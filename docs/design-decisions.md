# Design Decisions

This document outlines the core architectural and design choices made while building `ai-release-metadata`. 

### Why Plugins?
To support a wide variety of deployment environments without bloating the core SDK. Extracting the Git SHA on a local laptop requires running a `subprocess` command, while extracting it in GitHub Actions simply requires reading an environment variable. A plugin architecture allows the SDK to resolve these environment-specific quirks cleanly, and allows enterprises to easily write custom plugins for proprietary systems (like Kubernetes annotations or internal deployment APIs).

### Why ContextVars?
To solve the **Context Propagation** problem. In modern asynchronous Python applications (like FastAPI), an AI generation request might pass through a dozen nested functions before the actual LLM call occurs. If we didn't use `contextvars`, developers would be forced to pass `model` and `prompt_version` through every single function signature just to log it at the bottom of the stack. `contextvars` allows the context to flow invisibly alongside the async task, keeping function signatures clean.

### Why OpenTelemetry exporter instead of a tracing backend?
Because enterprise engineering teams do not want another dashboard. They already use Datadog, Grafana, Honeycomb, or New Relic. Building a standalone tracing backend forces teams to context-switch when debugging. By acting as an OpenTelemetry *enrichment layer* rather than a standalone backend, the SDK injects AI metadata directly into the tools engineers are already using to monitor system health.

### Why application-level instrumentation?
Many AI observability tools work by "monkey-patching" or wrapping the official OpenAI or Anthropic SDKs. This is fragile. When OpenAI releases a new SDK version, the instrumentation breaks. Furthermore, it locks you into specific LLM providers. By instrumenting at the application/business logic layer (e.g., `@capture_generation`), the SDK remains entirely provider-agnostic and completely immune to upstream API changes.

### Why mutable runtime metadata?
Because not all context is known at the start of a request. For example, if you are building a Retrieval-Augmented Generation (RAG) system, you do not know which documents the vector database will return until halfway through the request. By allowing the `ReleaseContext` to be mutated dynamically during execution (`ctx.add_document()`), the SDK ensures that the final exported span contains the complete, accurate picture of what actually happened, rather than just what was predicted to happen.
