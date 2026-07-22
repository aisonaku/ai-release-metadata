from typing import Dict, Any, Protocol

class MetadataPlugin(Protocol):
    """Protocol for all AI Release metadata discovery plugins."""
    
    def extract(self) -> Dict[str, Any]:
        """Extract metadata and return it as a dictionary.
        This dictionary will be merged into the ReleaseMetadata on startup.
        """
        ...
