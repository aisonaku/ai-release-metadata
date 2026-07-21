import os
from ai_release_metadata.plugins.env import EnvPlugin

def test_env_plugin():
    os.environ["GIT_COMMIT"] = "abcdef"
    os.environ["ENVIRONMENT"] = "staging"
    
    extractor = EnvPlugin()
    data = extractor.extract()
    assert data["git_sha"] == "abcdef"
    assert data["environment"] == "staging"

def test_config_merging():
    os.environ["GIT_COMMIT"] = "123456"
    from ai_release_metadata.core.sdk import MetadataProvider
    MetadataProvider(plugins=[EnvPlugin()])
    
    # Re-evaluate logic to ensure context propagation still works under new config
    from ai_release_metadata.core.context import release_context, get_current_context
    with release_context(feature="demo"):
        ctx = get_current_context()
        assert ctx.feature == "demo"
        assert ctx.git_sha == "123456"
