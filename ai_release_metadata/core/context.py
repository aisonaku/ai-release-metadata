import contextvars
import asyncio
from contextlib import contextmanager
from functools import wraps
from typing import Optional, Generator, Callable, Any
import copy

from .sdk import MetadataProvider
from .models import ReleaseContext

# A thread-safe, async-safe context variable to hold the current release context
_current_context: contextvars.ContextVar[Optional[ReleaseContext]] = contextvars.ContextVar(
    "ai_release_metadata", default=None
)

def get_current_context() -> Optional[ReleaseContext]:
    """Retrieve the active AI release context metadata from the current execution."""
    return _current_context.get()

@contextmanager
def release_context(
    feature: Optional[str] = None,
    prompt_version: Optional[str] = None,
    model: Optional[str] = None
) -> Generator[ReleaseContext, None, None]:
    """Context manager to start a new AI release context block."""
    parent_context = get_current_context()
    
    if parent_context:
        # Deep copy to prevent modifying parent state
        metadata = copy.deepcopy(parent_context)
        
        # Override fields if explicitly provided in this block
        if feature:
            metadata.feature = feature
        if prompt_version:
            metadata.prompt_version = prompt_version
        if model:
            metadata.model = model
    else:
        # 1. Base release metadata comes from the global MetadataProvider
        metadata = MetadataProvider.get_global().get_base_metadata()
        metadata.feature = feature
        metadata.prompt_version = prompt_version
        metadata.model = model
    
    token = _current_context.set(metadata)
    try:
        yield metadata
    finally:
        _current_context.reset(token)

def capture_generation(
    feature: Optional[str] = None,
    prompt_version: Optional[str] = None,
    model: Optional[str] = None,
    experiment_flags: Optional[dict] = None,
    tags: Optional[dict] = None,
    auto_capture_args: bool = True
):
    """Decorator to wrap a function with an AI release context."""
    import inspect
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        sig = inspect.signature(func)
        
        def _capture(ctx, args, kwargs):
            if ctx:
                if experiment_flags:
                    ctx.experiment_flags.update(experiment_flags)
                if tags:
                    ctx.tags.update(tags)
                    
                if auto_capture_args:
                    try:
                        bound = sig.bind(*args, **kwargs)
                        bound.apply_defaults()
                        for k, v in bound.arguments.items():
                            if isinstance(v, (str, int, float, bool)):
                                ctx.tags[f"arg_{k}"] = v
                            else:
                                ctx.tags[f"arg_{k}"] = str(v)
                    except Exception:
                        pass

        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                with release_context(feature=feature, prompt_version=prompt_version, model=model) as ctx:
                    _capture(ctx, args, kwargs)
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                with release_context(feature=feature, prompt_version=prompt_version, model=model) as ctx:
                    _capture(ctx, args, kwargs)
                    return func(*args, **kwargs)
            return sync_wrapper
    return decorator
