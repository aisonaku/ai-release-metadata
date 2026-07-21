from typing import Any, Dict
from ..core.context import get_current_context

def structlog_processor(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Structlog processor that appends the active AI release metadata to the log event."""
    context = get_current_context()
    if context:
        # Append release context under the 'ai' key
        context_data = context.as_dict()
        if context_data:
            event_dict["ai"] = context_data
    return event_dict
