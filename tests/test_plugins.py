import os
from ai_release_metadata.plugins.env import EnvPlugin

def test_env_plugin():
    os.environ["GIT_COMMIT"] = "abcdef"
    os.environ["ENVIRONMENT"] = "production"
    
    plugin = EnvPlugin()
    metadata = plugin.extract()
    
    assert metadata["git_sha"] == "abcdef"
    assert metadata["environment"] == "production"

def test_config_merging():
    os.environ["GIT_COMMIT"] = "123456"
    from ai_release_metadata.core.sdk import MetadataProvider
    MetadataProvider(plugins=[EnvPlugin()])
    
    # Re-evaluate logic to ensure context propagation still works under new config
    from ai_release_metadata.core.context import ai_trace, get_current_trace
    with ai_trace(feature="demo"):
        trace = get_current_trace()
        assert trace.ai.feature == "demo"
        assert trace.release.git_sha == "123456"
