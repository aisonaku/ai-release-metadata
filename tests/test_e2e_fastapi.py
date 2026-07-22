import os
import json
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def e2e_env(monkeypatch):
    """Sets up the environment exactly as it would be in a CI/CD pipeline."""
    monkeypatch.setenv("GIT_COMMIT", "e2e-test-sha")
    monkeypatch.setenv("ENVIRONMENT", "e2e")
    monkeypatch.setenv("LOG_FORMAT", "json") # Ensure structlog outputs raw JSON for parsing
    
    # Reset the global metadata provider so the new environment variables take effect
    from ai_release_metadata.core.sdk import MetadataProvider
    MetadataProvider._global_instance = None

def test_fastapi_e2e_flow(e2e_env, caplog):
    import logging
    caplog.set_level(logging.INFO)
    """
    True E2E test:
    1. Loads the FastAPI app
    2. Sends a real HTTP request
    3. Intercepts the terminal output
    4. Asserts that the 'ai' metadata survived the async stack and printed correctly
    """
    # Import inside the test so environment variables are applied during module load
    import demo.app
    import importlib
    
    # Force reload in case other tests imported it first
    importlib.reload(demo.app)
    
    client = TestClient(demo.app.app)
    
    # Send a request to the server
    response = client.post(
        "/generate",
        json={
            "model": "gpt-4o",
            "prompt_version": "v1.0",
            "user_query": "hello"
        }
    )
    
    assert response.status_code == 200
    
    # Capture the structlog output pushed to standard logging
    # Structlog serializes the dictionary into a JSON string in record.message
    found_target_log = False
    
    for record in caplog.records:
        try:
            log_data = json.loads(record.message)
        except json.JSONDecodeError:
            continue
            
        if log_data.get("message") == "Deep research complete" or log_data.get("event") == "Deep research complete":
            found_target_log = True
            ai_meta = log_data.get("ai", {})
            
            # Assert Global Context propagated (from EnvPlugin)
            assert ai_meta.get("git_sha") == "e2e-test-sha"
            
            # Assert Top-Level Request Context propagated (from app.post)
            assert ai_meta.get("model") == "gpt-4o"
            assert ai_meta.get("prompt_version") == "v1.0"
            
            # Assert Decorator Context propagated (from @capture_generation)
            assert ai_meta.get("feature") == "comprehensive-answer"
            assert ai_meta.get("experiment_flags", {}).get("use_deep_research") is True
            
    assert found_target_log, f"Did not find the expected log event. Captured messages: {[r.message for r in caplog.records]}"
