import dataclasses
from typing import Optional, Dict, Any, List

@dataclasses.dataclass
class ReleaseContext:
    """Standardized metadata model for an AI generation trace."""
    # Explicitly provided by developer
    feature: Optional[str] = None
    prompt_version: Optional[str] = None
    model: Optional[str] = None
    
    # Automatically extracted
    git_sha: Optional[str] = None
    deployment_version: Optional[str] = None
    environment: Optional[str] = None
    
    # Runtime context
    experiment_flags: Dict[str, Any] = dataclasses.field(default_factory=dict)
    retrieved_documents: List[str] = dataclasses.field(default_factory=list)
    tags: Dict[str, Any] = dataclasses.field(default_factory=dict)
    extra: Dict[str, Any] = dataclasses.field(default_factory=dict)
    
    def add_document(self, document: str) -> None:
        """Helper to append a retrieved document."""
        self.retrieved_documents.append(document)
        
    def add_tag(self, key: str, value: Any) -> None:
        """Helper to attach a runtime tag."""
        self.tags[key] = value
    
    def as_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None or empty values."""
        result = {}
        for k, v in dataclasses.asdict(self).items():
            if v is not None:
                # exclude empty dicts/lists for cleaner logs
                if isinstance(v, (list, dict)) and not v:
                    continue
                result[k] = v
        return result
