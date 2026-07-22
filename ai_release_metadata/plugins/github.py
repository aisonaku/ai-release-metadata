import os
from typing import Dict, Any
from .base import MetadataPlugin

class GitHubActionsPlugin(MetadataPlugin):
    """Extracts metadata specific to GitHub Actions environment variables."""
    
    def extract(self) -> Dict[str, Any]:
        metadata = {}
        
        # GITHUB_SHA is the commit that triggered the workflow
        if git_sha := os.environ.get("GITHUB_SHA"):
            metadata["git_sha"] = git_sha
            
        # GITHUB_RUN_ID is a unique number for each workflow run, great for deployment version
        if run_id := os.environ.get("GITHUB_RUN_ID"):
            metadata["deployment_version"] = f"gha-{run_id}"
            
        # GITHUB_REF_NAME is the branch or tag name
        if ref := os.environ.get("GITHUB_REF_NAME"):
            metadata["environment"] = ref
            
        return metadata
