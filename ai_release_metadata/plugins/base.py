from abc import ABC, abstractmethod
from typing import Dict, Any

class Plugin(ABC):
    """Base class for all AI Release metadata plugins."""
    
    @abstractmethod
    def extract(self) -> Dict[str, Any]:
        """Extract metadata and return it as a dictionary.
        This dictionary will be merged into the ReleaseMetadata on startup.
        """
        pass
