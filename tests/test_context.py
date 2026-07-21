import asyncio
import pytest
from ai_release_metadata.core.context import ai_trace, trace_generation, get_current_trace

def test_ai_trace_context_manager():
    # Outside context, should be None
    assert get_current_trace() is None
    
    with ai_trace(feature="test-feature", prompt_version="v1"):
        trace = get_current_trace()
        assert trace is not None
        assert trace.ai.feature == "test-feature"
        assert trace.ai.prompt_version == "v1"
        assert trace.ai.model is None
        
        # Test updating runtime context
        trace.runtime.retrieved_documents.append("doc-1")
        assert get_current_trace().runtime.retrieved_documents == ["doc-1"]
        
    # After context, should reset to None
    assert get_current_trace() is None

def test_trace_generation_decorator_sync():
    @trace_generation(feature="decorated-feature")
    def sync_dummy():
        trace = get_current_trace()
        return trace.ai.feature if trace else None
        
    assert get_current_trace() is None
    assert sync_dummy() == "decorated-feature"
    assert get_current_trace() is None

@pytest.mark.asyncio
async def test_trace_generation_decorator_async():
    @trace_generation(model="gpt-4o")
    async def async_dummy():
        trace = get_current_trace()
        # Simulate some async work
        await asyncio.sleep(0.01)
        return trace.ai.model if trace else None
        
    assert get_current_trace() is None
    assert await async_dummy() == "gpt-4o"
    assert get_current_trace() is None

def test_nested_ai_trace():
    with ai_trace(feature="parent", model="gpt-4"):
        trace = get_current_trace()
        trace.runtime.tags["user_tier"] = "premium"
        trace.runtime.experiment_flags["new_rag"] = True
        
        with ai_trace(feature="child", prompt_version="v2"):
            child_trace = get_current_trace()
            # Inherited tags/experiments
            assert child_trace.runtime.tags["user_tier"] == "premium"
            assert child_trace.runtime.experiment_flags["new_rag"] is True
            # Overridden properties
            assert child_trace.ai.feature == "child"
            assert child_trace.ai.prompt_version == "v2"
            # Inherited model from parent because it wasn't specified in child
            assert child_trace.ai.model == "gpt-4"
            
            # Modifying child shouldn't modify parent due to copy()
            child_trace.runtime.tags["child_specific"] = "yes"
            
        # Back to parent
        parent_restored = get_current_trace()
        assert parent_restored.ai.feature == "parent"
        assert "child_specific" not in parent_restored.runtime.tags
