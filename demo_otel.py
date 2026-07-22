import asyncio
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter

from ai_release_metadata import MetadataProvider, release_context
from ai_release_metadata.plugins import EnvPlugin, GitPlugin
from ai_release_metadata.integrations.opentelemetry import enrich_span

# 1. Setup OpenTelemetry Tracing and Metrics to print to the terminal
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
tracer = trace.get_tracer("demo.otel.traces")

metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader]))
meter = metrics.get_meter("demo.otel.metrics")

# Create an OpenTelemetry Metric Counter
generation_counter = meter.create_counter("ai.generation.count", description="Number of AI generations")

# 2. Setup AI Release Metadata
MetadataProvider(plugins=[GitPlugin(), EnvPlugin()])

async def main():
    print("Initializing OpenTelemetry generation demo...\n")
    
    with tracer.start_as_current_span("generate_response"):
        with release_context(feature="demo-otel", model="gpt-4o") as ctx:
            ctx.add_tag("user_tier", "premium")
            
            # --- SIMULATE EXISTING LLM DATA ---
            # Imagine an OpenAI OpenTelemetry auto-instrumentation library 
            # had already automatically added these token metrics to the span:
            span = trace.get_current_span()
            span.set_attribute("llm.request.model", "gpt-4o")
            span.set_attribute("llm.usage.total_tokens", 435)
            span.set_attribute("llm.usage.prompt_tokens", 120)
            
            # --- Trace Enrichment ---
            # Append release context to the existing span.
            enrich_span()
            
            # --- Metric Recording ---
            # Record generation counter with flattened release context as attributes.
            flat_attributes = {f"ai.{k}": str(v) for k, v in ctx.as_dict().items()}
            generation_counter.add(1, flat_attributes)
            
            await asyncio.sleep(0.1)

    # Force the metric exporter to flush to the console immediately
    metrics.get_meter_provider().force_flush()
    print("\nTrace span and metric counter successfully exported to console.")

if __name__ == "__main__":
    asyncio.run(main())
