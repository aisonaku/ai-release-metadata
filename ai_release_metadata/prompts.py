import hashlib
import os
from abc import ABC, abstractmethod
from typing import Tuple

from .core.context import get_current_context

class BasePromptProvider(ABC):
    """
    Abstract base class for all prompt providers.
    
    A PromptProvider is responsible for retrieving prompt text and 
    automatically injecting the prompt's version/hash into the active ReleaseContext.
    
    Example of extending for a Cloud Registry:
        class CloudRegistryPromptProvider(BasePromptProvider):
            def _fetch(self, prompt_name: str) -> tuple[str, str]:
                # Fetch from remote API
                response = my_cloud_api.fetch(prompt_name)
                # Return the text and the official UUID from the database
                return response.text, response.uuid
    """
    
    def get_prompt(self, prompt_name: str) -> str:
        """
        Retrieves the prompt and automatically injects its version 
        into the active ReleaseContext.
        """
        text, version = self._fetch(prompt_name)
        
        ctx = get_current_context()
        ctx.prompt_version = version
        
        return text

    @abstractmethod
    def _fetch(self, prompt_name: str) -> Tuple[str, str]:
        """
        Must return a tuple of (prompt_text, prompt_version).
        """
        pass


class LocalFilePromptProvider(BasePromptProvider):
    """
    Loads prompts from local text files and automatically calculates a SHA-256 hash
    to use as the prompt_version.
    """
    def __init__(self, base_dir: str, extension: str = ".txt"):
        self.base_dir = base_dir
        self.extension = extension
        
    def _fetch(self, prompt_name: str) -> Tuple[str, str]:
        file_path = os.path.join(self.base_dir, f"{prompt_name}{self.extension}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Prompt file not found: {file_path}")
            
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            
        # Auto-calculate the hash (first 8 characters of SHA-256)
        version_hash = "sha256-" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]
        return text, version_hash
