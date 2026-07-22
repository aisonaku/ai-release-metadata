# Architecture

`ai-release-metadata` is designed around a clean, unidirectional data flow: **Sources -> Context Propagation -> Exporters**.

## High-Level Flow

```mermaid
sequenceDiagram
    participant App as Application
    participant SDK as MetadataProvider
    participant Plugin as MetadataPlugins
    participant CTX as ContextVars
    participant Exp as "Exporters (e.g., OpenTelemetry)"

    App->>SDK: MetadataProvider(plugins=[...])
    SDK->>Plugin: extract()
    Plugin-->>SDK: {git_sha: "abc1234"}
    
    Note over SDK: Base Metadata stored in global singleton
    
    App->>CTX: with release_context(model="gpt-4"):
    Note over CTX: Base Metadata + model stored in Thread-safe Context
    
    App->>Exp: enrich_span()
    Exp->>CTX: get_current_context()
    CTX-->>Exp: Unified Release Context
    Note over Exp: Attributes appended to active span/log
```

## Context Propagation

The SDK uses Python's native `contextvars` to manage state. This is crucial for modern asynchronous frameworks like FastAPI or AsyncIO.

Instead of passing an `ai_context` object down through 10 layers of function arguments, `with release_context(...)` sets a context variable that is implicitly available to any deeply-nested function running on that same logical thread/task.

When an exporter (like `enrich_span()`) is called, it simply retrieves the active context from `contextvars` and serializes it.
