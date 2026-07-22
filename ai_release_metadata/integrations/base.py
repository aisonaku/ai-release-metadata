from typing import Protocol
from ..core.models import ReleaseContext

class Exporter(Protocol):
    """Protocol for push-based AI release metadata exporters."""
    
    def export(self, context: ReleaseContext) -> None:
        """Export the unified release context to an external system."""
        ...
