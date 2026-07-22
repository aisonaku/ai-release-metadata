import subprocess
from typing import Dict, Any
from .base import MetadataPlugin

class GitPlugin(MetadataPlugin):
    """Extracts metadata from the local Git repository using subprocess."""
    
    def extract(self) -> Dict[str, Any]:
        metadata = {}
        try:
            # Run git rev-parse HEAD to get the current commit SHA
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            sha = result.stdout.strip()
            if sha:
                metadata["git_sha"] = sha
                
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            branch = branch_result.stdout.strip()
            if branch and branch != "HEAD":
                metadata["git_branch"] = branch
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fails gracefully if git is not installed or not in a git repo
            pass
            
        return metadata
