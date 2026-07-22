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
    assert data["git_branch"] == "main"

def test_git_plugin_mocked(monkeypatch):
    import subprocess
    
    # Mock subprocess.run to simulate a valid git repo
    def mock_run(args, **kwargs):
        class MockResult:
            def __init__(self, stdout):
                self.stdout = stdout
        if "--abbrev-ref" in args:
            return MockResult("mock-branch\n")
        return MockResult("mock-sha-890\n")
        
    monkeypatch.setattr(subprocess, "run", mock_run)
    
    from ai_release_metadata.plugins.git import GitPlugin
    plugin = GitPlugin()
    data = plugin.extract()
    
    assert data["git_sha"] == "mock-sha-890"
    assert data["git_branch"] == "mock-branch"

def test_custom_plugin_extra_fields():
    from typing import Dict, Any
    
    class CustomCompanyPlugin:
        def extract(self) -> Dict[str, Any]:
            return {
                "git_sha": "custom123",
                "company_org": "finance",
                "cost_center": "4455"
            }
            
    from ai_release_metadata.core.sdk import MetadataProvider
    provider = MetadataProvider(plugins=[CustomCompanyPlugin()])
    
    base_meta = provider.get_base_metadata()
    
    # Core field should be mapped
    assert base_meta.git_sha == "custom123"
    
    # Unknown fields should be dumped into 'extra'
    assert base_meta.extra["company_org"] == "finance"
    assert base_meta.extra["cost_center"] == "4455"
