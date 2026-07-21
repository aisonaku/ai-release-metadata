from typing import List, Optional, Dict, Any
import copy

from ..plugins.base import Plugin
from .models import ReleaseContext

class MetadataProvider:
    """Instanced SDK Manager. Registers itself as the global provider upon instantiation."""
    
    _global_instance = None
    
    def __init__(self, plugins: Optional[List[Plugin]] = None):
        self.plugins = plugins or []
        self.base_metadata = ReleaseContext()
        self._evaluate_plugins()
        
        # OpenTelemetry pattern: registering as the global instance implicitly
        MetadataProvider._global_instance = self
        
    def _evaluate_plugins(self):
        """Run all registered plugins and populate base_metadata."""
        extra = {}
        for plugin in self.plugins:
            result = plugin.extract()
            # Map known fields, dump the rest into extra
            for k, v in result.items():
                if hasattr(self.base_metadata, k) and k != "extra":
                    setattr(self.base_metadata, k, v)
                else:
                    extra[k] = v
        self.base_metadata.extra = extra
        
    @classmethod
    def get_global(cls) -> "MetadataProvider":
        """Get the global SDK instance. If none exists, return a dummy one to avoid crashes."""
        if cls._global_instance is None:
            return cls()
        return cls._global_instance
        
    def get_base_metadata(self) -> ReleaseContext:
        """Return a deep copy of the base metadata for trace injection."""
        return copy.deepcopy(self.base_metadata)
