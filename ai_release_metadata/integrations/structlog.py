from typing import Any, Dict
from ..core.context import get_current_trace

def structlog_processor(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Structlog processor that appends the active AI trace to the log event."""
    trace = get_current_trace()
    if trace:
        # Append trace context under the 'ai' key
        trace_data = trace.as_dict()
        if trace_data:
            event_dict["ai"] = trace_data
    return event_dict
