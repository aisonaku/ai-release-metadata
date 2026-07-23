from opentelemetry import trace
from ..core.context import get_current_context

def enrich_span(span: trace.Span = None) -> None:
    """
    Appends the active AI release context to the provided OpenTelemetry span.
    If no span is provided, it attempts to use the currently active span in the context.
    """
    if span is None:
        span = trace.get_current_span()
        
    if not span or not span.is_recording():
        return
        
    ctx = get_current_context()
    if not ctx:
        return
        
    # Serialize context and add attributes to the span
    data = ctx.as_dict()
    
    # Flatten the dict for OTEL attributes (OTEL doesn't support nested dictionaries)
    for key, value in data.items():
        if isinstance(value, (list, tuple)):
            # OTEL supports homogeneous arrays of primitives
            try:
                span.set_attribute(f"ai.{key}", list(value))
            except Exception:
                span.set_attribute(f"ai.{key}", [str(v) for v in value])
                
        elif isinstance(value, dict):
            # Flatten one level deep (e.g. tags, experiment_flags)
            for sub_k, sub_v in value.items():
                if isinstance(sub_v, (str, int, float, bool)):
                    span.set_attribute(f"ai.{key}.{sub_k}", sub_v)
                else:
                    span.set_attribute(f"ai.{key}.{sub_k}", str(sub_v))
                    
        elif isinstance(value, (str, int, float, bool)):
            span.set_attribute(f"ai.{key}", value)
        else:
            span.set_attribute(f"ai.{key}", str(value))


try:
    from opentelemetry.sdk.trace import SpanProcessor
    
    class ReleaseMetadataSpanProcessor(SpanProcessor):
        """
        An OpenTelemetry SpanProcessor that automatically injects the active
        ai_release_metadata context into every span created by auto-instrumentation 
        (e.g., FastAPI, Requests, OpenAI SDKs).
        """
        def on_start(self, span: trace.Span, parent_context=None):
            # enrich_span safely grabs the current context and flattens it 
            # into the provided span before the span is emitted.
            enrich_span(span)
            
        def on_end(self, span):
            # Guarantee that any metadata mutations (tags, experiment flags) added 
            # *after* the span started are flushed to the span before it exports.
            enrich_span(span)
            
except ImportError:
    # If opentelemetry-sdk is not installed, we ignore the processor definition.
    pass
