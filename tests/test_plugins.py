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

def test_github_actions_plugin(monkeypatch):
    monkeypatch.setenv("GITHUB_SHA", "gha123")
    monkeypatch.setenv("GITHUB_RUN_ID", "9876")
    monkeypatch.setenv("GITHUB_REF_NAME", "main")
    
    from ai_release_metadata.plugins.github import GitHubActionsPlugin
    plugin = GitHubActionsPlugin()
    data = plugin.extract()
    
    assert data["git_sha"] == "gha123"
    assert data["deployment_version"] == "gha-9876"
    assert data["environment"] == "main"

def test_git_plugin_mocked(monkeypatch):
    import subprocess
    
    # Mock subprocess.run to simulate a valid git repo
    def mock_run(*args, **kwargs):
        class MockResult:
            stdout = "mock-sha-890\n"
        return MockResult()
        
    monkeypatch.setattr(subprocess, "run", mock_run)
    
    from ai_release_metadata.plugins.git import GitPlugin
    plugin = GitPlugin()
    data = plugin.extract()
    
    assert data["git_sha"] == "mock-sha-890"
