import contextvars
import asyncio
from contextlib import contextmanager
from functools import wraps
from typing import Optional, Generator, Callable, Any
import copy

from .sdk import MetadataProvider
from .models import ReleaseContext, RuntimeMetadata, AIInteractionMetadata

# A thread-safe, async-safe context variable to hold the current trace
_current_trace: contextvars.ContextVar[Optional[ReleaseContext]] = contextvars.ContextVar(
    "ai_release_metadata", default=None
)

def get_current_trace() -> Optional[ReleaseContext]:
    """Retrieve the active AI trace metadata from the current context."""
    return _current_trace.get()

@contextmanager
def ai_trace(
    feature: Optional[str] = None,
    prompt_version: Optional[str] = None,
    model: Optional[str] = None
) -> Generator[ReleaseContext, None, None]:
    """Context manager to start a new AI trace and set it in the current context."""
    parent_trace = get_current_trace()
    
    # 1. Base release metadata comes from the global MetadataProvider
    release = MetadataProvider.get_global().get_base_metadata()
    
    # 2. Inherit runtime and ai from parent, or start fresh
    if parent_trace:
        runtime = copy.deepcopy(parent_trace.runtime)
        ai = copy.deepcopy(parent_trace.ai)
        
        # Override AI fields if explicitly provided in this block
        if feature:
            ai.feature = feature
        if prompt_version:
            ai.prompt_version = prompt_version
        if model:
            ai.model = model
            
    else:
        runtime = RuntimeMetadata()
        ai = AIInteractionMetadata(
            feature=feature,
            prompt_version=prompt_version,
            model=model
        )
        
    metadata = ReleaseContext(
        release=release,
        runtime=runtime,
        ai=ai
    )
    
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
                    trace.runtime.experiment_flags.update(experiment_flags)
                if tags:
                    trace.runtime.tags.update(tags)
                    
                if auto_capture_args:
                    try:
                        bound = sig.bind(*args, **kwargs)
                        bound.apply_defaults()
                        for k, v in bound.arguments.items():
                            if isinstance(v, (str, int, float, bool)):
                                trace.runtime.tags[f"arg_{k}"] = v
                            else:
                                trace.runtime.tags[f"arg_{k}"] = str(v)
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
