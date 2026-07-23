import os
import tempfile
import hashlib

from ai_release_metadata import release_context, get_current_context
from ai_release_metadata.prompts import LocalFilePromptProvider

def test_local_file_prompt_provider():
    with tempfile.TemporaryDirectory() as tmpdir:
        prompt_text = "You are a helpful assistant."
        expected_hash = "sha256-" + hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()[:8]
        
        # Create a dummy prompt file
        prompt_path = os.path.join(tmpdir, "support_bot.txt")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt_text)
            
        provider = LocalFilePromptProvider(base_dir=tmpdir)
        
        with release_context(model="gpt-4"):
            # Fetch the prompt
            text = provider.get_prompt("support_bot")
            
            # Verify text
            assert text == prompt_text
            
            # Verify the hash was injected into the context automatically
            ctx = get_current_context()
            assert ctx.prompt_version == expected_hash
            assert ctx.model == "gpt-4" # Pre-existing context is preserved
