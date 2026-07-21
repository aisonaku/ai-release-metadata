import abc
from typing import Dict, Any

class Extractor(abc.ABC):
    """Base interface for all metadata extractors."""
    @abc.abstractmethod
    def extract(self) -> Dict[str, Any]:
        """Extract metadata and return as a dictionary."""
        pass
