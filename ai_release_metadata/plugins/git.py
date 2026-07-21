import subprocess
from typing import Dict, Any
from .base import Plugin

class GitPlugin(Plugin):
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
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fails gracefully if git is not installed or not in a git repo
            pass
            
        return metadata
