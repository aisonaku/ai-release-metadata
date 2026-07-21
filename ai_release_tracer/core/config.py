from typing import List, Optional
from ..extractors.base import Extractor

class AIReleaseConfig:
    _extractors: List[Extractor] = []
    _base_metadata: dict = {}
    
    @classmethod
    def configure(cls, extractors: Optional[List[Extractor]] = None):
        cls._base_metadata.clear()
        if extractors:
            cls._extractors = extractors
            
        # Run extractors once on startup and cache the result
        for extractor in cls._extractors:
            cls._base_metadata.update(extractor.extract())
            
    @classmethod
    def get_base_metadata(cls) -> dict:
        return cls._base_metadata.copy()

def configure(extractors: Optional[List[Extractor]] = None):
    """Global configuration function for the SDK."""
    AIReleaseConfig.configure(extractors=extractors)
