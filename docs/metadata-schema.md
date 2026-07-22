# Metadata Schema

The SDK uses a flattened `ReleaseContext` dataclass to ensure maximum compatibility with external systems like OpenTelemetry, which do not natively support deeply nested JSON objects as span attributes.

## Core Fields

| Field | Type | Description | Discovered By |
|-------|------|-------------|---------------|
| `git_sha` | string | The commit hash of the deployed code. | Plugins (Env, Git, GitHub) |
| `environment` | string | The deployment environment (e.g., `production`, `staging`). | Plugins (Env, GitHub) |
| `deployment_version` | string | An arbitrary release tag or CI run ID. | Plugins (Env, GitHub) |
| `feature` | string | The business feature triggering the AI call. | `@capture_generation` / `release_context` |
| `model` | string | The AI model used (e.g., `gpt-4o`). | `@capture_generation` / `release_context` |
| `prompt_version` | string | The version tag of the prompt template. | `@capture_generation` / `release_context` |

## Dynamic Collections

| Field | Type | Description |
|-------|------|-------------|
| `experiment_flags` | dict | Key-value pairs of active A/B tests or flags. |
| `retrieved_documents` | list[str] | List of document IDs injected via RAG. |
| `tags` | dict | Arbitrary key-value pairs for runtime data (e.g., `user_tier: premium`). |
| `extra` | dict | Escape hatch for unstandardized data. |

> [!NOTE]
> **OpenTelemetry Flattening**
> When exporting to OpenTelemetry, nested dictionaries like `tags` are flattened one level deep. For example, `tags={"user_tier": "premium"}` becomes the span attribute `ai.tags.user_tier = "premium"`.
