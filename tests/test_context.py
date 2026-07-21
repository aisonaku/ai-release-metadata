import asyncio
import pytest
from ai_release_metadata.core.context import release_context, capture_generation, get_current_context

def test_release_context_manager():
    # Outside context, should be None
    assert get_current_context() is None
    
    with release_context(feature="test-feature", prompt_version="v1"):
        ctx = get_current_context()
        assert ctx is not None
        assert ctx.feature == "test-feature"
        assert ctx.prompt_version == "v1"
        assert ctx.model is None
        
        # Test updating runtime context
        ctx.retrieved_documents.append("doc-1")
        assert get_current_context().retrieved_documents == ["doc-1"]
        
    # After context, should reset to None
    assert get_current_context() is None

def test_capture_generation_decorator_sync():
    @capture_generation(feature="decorated-feature")
    def sync_dummy():
        ctx = get_current_context()
        return ctx.feature if ctx else None
        
    assert get_current_context() is None
    assert sync_dummy() == "decorated-feature"
    assert get_current_context() is None

@pytest.mark.asyncio
async def test_capture_generation_decorator_async():
    @capture_generation(model="gpt-4o")
    async def async_dummy():
        ctx = get_current_context()
        # Simulate some async work
        await asyncio.sleep(0.01)
        return ctx.model if ctx else None
        
    assert get_current_context() is None
    assert await async_dummy() == "gpt-4o"
    assert get_current_context() is None

def test_nested_release_context():
    with release_context(feature="parent", model="gpt-4"):
        ctx = get_current_context()
        ctx.tags["user_tier"] = "premium"
        ctx.experiment_flags["new_rag"] = True
        
        with release_context(feature="child", prompt_version="v2"):
            child_ctx = get_current_context()
            # Inherited tags/experiments
            assert child_ctx.tags["user_tier"] == "premium"
            assert child_ctx.experiment_flags["new_rag"] is True
            # Overridden properties
            assert child_ctx.feature == "child"
            assert child_ctx.prompt_version == "v2"
            # Inherited model from parent because it wasn't specified in child
            assert child_ctx.model == "gpt-4"
            
            # Modifying child shouldn't modify parent due to copy()
            child_ctx.tags["child_specific"] = "yes"
            
        # Back to parent
        parent_restored = get_current_context()
        assert parent_restored.feature == "parent"
        assert "child_specific" not in parent_restored.tags
