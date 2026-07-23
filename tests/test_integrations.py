import pytest
from opentelemetry import trace
from ai_release_metadata.core.context import release_context
from ai_release_metadata.integrations.opentelemetry import enrich_span

class MockSpan(trace.Span):
    def __init__(self):
        self.attributes = {}
        self._is_recording = True
        
    def set_attribute(self, key: str, value) -> None:
        self.attributes[key] = value
        
    def set_attributes(self, attributes) -> None:
        for k, v in attributes.items():
            self.attributes[k] = v
            
    def is_recording(self) -> bool:
        return self._is_recording
        
    def end(self, end_time=None) -> None:
        pass
        
    def get_span_context(self) -> trace.SpanContext:
        return trace.SpanContext(trace_id=1, span_id=1, is_remote=False)
        
    def set_status(self, status, description=None) -> None:
        pass
        
    def update_name(self, name) -> None:
        pass
        
    def record_exception(self, exception, attributes=None, timestamp=None, escaped=False) -> None:
        pass
        
    def add_event(self, name, attributes=None, timestamp=None) -> None:
        pass
        
    def add_link(self, context, attributes=None) -> None:
        pass

def test_otel_enrich_span():
    span = MockSpan()
    
    with release_context(feature="search", model="gpt-4o") as ctx:
        ctx.git_sha = "abc1234"
        ctx.tags["user_type"] = "admin"
        ctx.retrieved_documents = ["docA", "docB"]
        
        enrich_span(span)
        
    assert span.attributes["ai.feature"] == "search"
    assert span.attributes["ai.model"] == "gpt-4o"
    assert span.attributes["ai.git_sha"] == "abc1234"
    assert span.attributes["ai.tags.user_type"] == "admin"
    assert span.attributes["ai.retrieved_documents"] == ["docA", "docB"]

def test_otel_enrich_span_no_active_context():
    span = MockSpan()
    enrich_span(span)
    assert not span.attributes # Should do nothing without crashing

def test_otel_span_processor():
    try:
        from ai_release_metadata.integrations.opentelemetry import ReleaseMetadataSpanProcessor
    except ImportError:
        pytest.skip("opentelemetry-sdk not installed")
        
    processor = ReleaseMetadataSpanProcessor()
    span = MockSpan()
    
    with release_context(feature="auto-instrumented", model="gpt-3.5"):
        # Simulate an auto-instrumentation library starting a span
        processor.on_start(span)
        
    assert span.attributes["ai.feature"] == "auto-instrumented"
    assert span.attributes["ai.model"] == "gpt-3.5"
