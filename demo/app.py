import os
import sys
import logging
import structlog
from fastapi import FastAPI
from pydantic import BaseModel
import asyncio

from ai_release_tracer import configure, get_current_trace, ai_trace
from ai_release_tracer.extractors.env import EnvExtractor
from ai_release_tracer.integrations.structlog import structlog_processor

# 1. Configure the SDK (Extracts GIT_COMMIT, ENVIRONMENT, etc. on startup)
configure(extractors=[EnvExtractor()])

# 2. Configure Structlog
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
log_format = os.environ.get("LOG_FORMAT", "json").lower()

processors = [
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog_processor, # Inject AI Release metadata into logs!
]

if log_format == "console":
    processors.append(structlog.dev.ConsoleRenderer())
else:
    processors.append(structlog.processors.JSONRenderer())

structlog.configure(
    processors=processors,
    logger_factory=structlog.stdlib.LoggerFactory(),
)
logging.basicConfig(format="%(message)s", stream=sys.stdout, level=getattr(logging, log_level))

logger = structlog.get_logger("demo")
app = FastAPI(title="AI Release Tracer Demo")

class GenerateRequest(BaseModel):
    model: str = "gpt-4o"
    prompt_version: str = "v1.0"
    user_query: str

@app.post("/generate")
async def generate(req: GenerateRequest):
    logger.info("Received request")
    
    # 3. Open an AI trace context. All logs emitted inside this block will have metadata.
    with ai_trace(feature="customer-support", model=req.model, prompt_version=req.prompt_version):
        response = await run_llm_chain(req.user_query)
        
    return {"response": response}

async def run_llm_chain(query: str):
    trace = get_current_trace()
    if trace:
        # Dynamically append context during runtime
        trace.tags["query_length"] = len(query)
        trace.retrieved_documents = ["doc_123", "doc_456"]
        
    logger.info("Starting LLM generation...", provider="openai")
    await asyncio.sleep(0.5)
    logger.info("LLM generation complete.", generated_tokens=42)
    return f"Simulated answer to '{query}'"
