import dataclasses
from typing import Optional, Dict, Any, List

@dataclasses.dataclass
class ReleaseMetadata:
    """Immutable metadata about the deployment/release."""
    git_sha: Optional[str] = None
    deployment_version: Optional[str] = None
    environment: Optional[str] = None
    extra: Dict[str, Any] = dataclasses.field(default_factory=dict)

@dataclasses.dataclass
class RuntimeMetadata:
    """Volatile metadata tied to the specific execution context."""
    experiment_flags: Dict[str, Any] = dataclasses.field(default_factory=dict)
    retrieved_documents: List[str] = dataclasses.field(default_factory=list)
    tags: Dict[str, Any] = dataclasses.field(default_factory=dict)

@dataclasses.dataclass
class AIInteractionMetadata:
    """Metadata specifically identifying the AI feature and prompt."""
    feature: Optional[str] = None
    prompt_version: Optional[str] = None
    model: Optional[str] = None

@dataclasses.dataclass
class ReleaseContext:
    """Composite context representing the full execution trace."""
    release: ReleaseMetadata = dataclasses.field(default_factory=ReleaseMetadata)
    runtime: RuntimeMetadata = dataclasses.field(default_factory=RuntimeMetadata)
    ai: AIInteractionMetadata = dataclasses.field(default_factory=AIInteractionMetadata)
    
    def as_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None or empty values."""
        
        def _clean(data: dict) -> dict:
            return {
                k: v for k, v in data.items() 
                if v is not None and not (isinstance(v, (list, dict)) and not v)
            }
            
        release_dict = _clean(dataclasses.asdict(self.release))
        extra = release_dict.pop("extra", {})
        release_dict.update(_clean(extra))
            
        result = {}
        if release_dict:
            result["release"] = release_dict
            
        runtime_dict = _clean(dataclasses.asdict(self.runtime))
        if runtime_dict:
            result["runtime"] = runtime_dict
            
        ai_dict = _clean(dataclasses.asdict(self.ai))
        if ai_dict:
            result["ai"] = ai_dict
            
        return result
