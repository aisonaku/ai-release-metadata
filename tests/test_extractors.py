import os
from ai_release_tracer.core.config import AIReleaseConfig
from ai_release_tracer.extractors.env import EnvExtractor

def test_env_extractor():
    os.environ["GIT_COMMIT"] = "abcdef"
    os.environ["ENVIRONMENT"] = "staging"
    
    extractor = EnvExtractor()
    data = extractor.extract()
    assert data["git_sha"] == "abcdef"
    assert data["environment"] == "staging"

def test_config_merging():
    os.environ["GIT_COMMIT"] = "123456"
    AIReleaseConfig.configure(extractors=[EnvExtractor()])
    
    from ai_release_tracer.core.context import ai_trace, get_current_trace
    with ai_trace(feature="demo"):
        trace = get_current_trace()
        assert trace.feature == "demo"
        assert trace.git_sha == "123456"
