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
    model: Optional[str] = None,
    experiment_flags: Optional[dict] = None,
    tags: Optional[dict] = None,
    auto_capture_args: bool = True
):
    """Decorator to wrap a function with an AI trace context."""
    import inspect
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        sig = inspect.signature(func)
        
        def _capture(trace, args, kwargs):
            if trace:
                if experiment_flags:
                    trace.experiment_flags.update(experiment_flags)
                if tags:
                    trace.tags.update(tags)
                    
                if auto_capture_args:
                    try:
                        bound = sig.bind(*args, **kwargs)
                        bound.apply_defaults()
                        for k, v in bound.arguments.items():
                            if isinstance(v, (str, int, float, bool)):
                                trace.tags[f"arg_{k}"] = v
                            else:
                                trace.tags[f"arg_{k}"] = str(v)
                    except Exception:
                        pass

        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                with ai_trace(feature=feature, prompt_version=prompt_version, model=model) as trace:
                    _capture(trace, args, kwargs)
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                with ai_trace(feature=feature, prompt_version=prompt_version, model=model) as trace:
                    _capture(trace, args, kwargs)
                    return func(*args, **kwargs)
            return sync_wrapper
    return decorator
