import os
from typing import Dict, Any
from .base import Extractor

class EnvExtractor(Extractor):
    """Extracts standard CI/CD and deployment environment variables."""
    def extract(self) -> Dict[str, Any]:
        metadata = {}
        
        # Git SHA
        git_sha = os.environ.get("GIT_COMMIT") or os.environ.get("GITHUB_SHA")
        if git_sha:
            metadata["git_sha"] = git_sha
            
        # Environment
        env = os.environ.get("ENVIRONMENT") or os.environ.get("ENV")
        if env:
            metadata["environment"] = env
            
        # Deployment Version
        version = os.environ.get("DEPLOY_VERSION") or os.environ.get("DD_VERSION")
        if version:
            metadata["deployment_version"] = version
            
        return metadata
