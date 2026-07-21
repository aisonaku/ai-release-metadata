import asyncio
import contextvars
from contextlib import contextmanager
from functools import wraps
from typing import Optional, Generator, Callable, Any

from .models import AIReleaseMetadata
from .config import AIReleaseConfig

# The ContextVar that holds the current trace metadata
_current_trace: contextvars.ContextVar[Optional[AIReleaseMetadata]] = contextvars.ContextVar(
    "ai_release_trace", default=None
)

def get_current_trace() -> Optional[AIReleaseMetadata]:
    """Retrieve the active AI trace metadata from the current context."""
    return _current_trace.get()

@contextmanager
def ai_trace(
    feature: Optional[str] = None,
    prompt_version: Optional[str] = None,
    model: Optional[str] = None
) -> Generator[AIReleaseMetadata, None, None]:
    """Context manager to start a new AI trace and set it in the current context."""
    parent_trace = get_current_trace()
    kwargs = AIReleaseConfig.get_base_metadata()
    
    if parent_trace:
        kwargs.update({
            "feature": feature or parent_trace.feature,
            "prompt_version": prompt_version or parent_trace.prompt_version,
            "model": model or parent_trace.model,
            "git_sha": parent_trace.git_sha,
            "deployment_version": parent_trace.deployment_version,
            "environment": parent_trace.environment,
            "experiment_flags": parent_trace.experiment_flags.copy(),
            "retrieved_documents": parent_trace.retrieved_documents.copy(),
            "tags": parent_trace.tags.copy(),
        })
    else:
        kwargs.update({
            "feature": feature,
            "prompt_version": prompt_version,
            "model": model,
        })
        
    metadata = AIReleaseMetadata(**kwargs)
    
    token = _current_trace.set(metadata)
    try:
        yield metadata
    finally:
        _current_trace.reset(token)

def trace_generation(
    feature: Optional[str] = None,
    prompt_version: Optional[str] = None,
    model: Optional[str] = None
):
    """Decorator to wrap a function with an AI trace context."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                with ai_trace(feature=feature, prompt_version=prompt_version, model=model):
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                with ai_trace(feature=feature, prompt_version=prompt_version, model=model):
                    return func(*args, **kwargs)
            return sync_wrapper
    return decorator
