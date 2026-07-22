import os
from typing import Dict, Any
from .base import MetadataPlugin

class EnvPlugin(MetadataPlugin):
    """Extracts metadata from environment variables."""
    
    def extract(self) -> Dict[str, Any]:
        metadata = {}
        if git_sha := os.environ.get("GIT_COMMIT") or os.environ.get("GITHUB_SHA"):
            metadata["git_sha"] = git_sha
            
        if env := os.environ.get("ENVIRONMENT") or os.environ.get("APP_ENV"):
            metadata["environment"] = env
            
        if version := os.environ.get("DEPLOYMENT_VERSION") or os.environ.get("APP_VERSION"):
            metadata["deployment_version"] = version
            
        return metadata
