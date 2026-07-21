import os
import sys
import logging
import structlog
from fastapi import FastAPI
from pydantic import BaseModel
import asyncio

from ai_release_metadata import (
    MetadataProvider, ai_trace, trace_generation
)
from ai_release_metadata.plugins.env import EnvPlugin
from ai_release_metadata.integrations.structlog import structlog_processor

# Initialize SDK configuration and extract environment variables
MetadataProvider(plugins=[EnvPlugin()])
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
log_format = os.environ.get("LOG_FORMAT", "json").lower()

processors = [
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog_processor, # Integrates ai_release_metadata metadata
]
if log_format == "console":
    processors.append(structlog.dev.ConsoleRenderer())
else:
    processors.append(structlog.processors.JSONRenderer())

structlog.configure(processors=processors, logger_factory=structlog.stdlib.LoggerFactory())
logging.basicConfig(format="%(message)s", stream=sys.stdout, level=getattr(logging, log_level))
logger = structlog.get_logger("demo")
app = FastAPI(title="AI Release Tracer Demo")

class GenerateRequest(BaseModel):
    model: str = "gpt-4o"
    prompt_version: str = "v1.0"
    user_query: str

# ---------------------------------------------------------
# Basic answer generation feature
# ---------------------------------------------------------
@trace_generation(feature="basic-answer", tags={"cost_center": "support"})
async def generate_basic_answer(query: str):
    logger.info("Generating basic answer...", provider="openai")
    await asyncio.sleep(0.3)
    logger.info("Basic answer complete", generated_tokens=20)
    return f"Basic answer to '{query}'"

# ---------------------------------------------------------
# Comprehensive answer generation feature
# ---------------------------------------------------------
@trace_generation(
    feature="comprehensive-answer", 
    experiment_flags={"use_deep_research": True}
)
async def generate_comprehensive_answer(query: str):
    logger.info("Starting comprehensive answer workflow")
    
    # Executes the basic answer logic within a nested trace context.
    # The child trace inherits the 'use_deep_research' experiment flag
    # and combines it with its own 'cost_center' tag.
    basic_part = await generate_basic_answer(query)
    
    logger.info("Performing deep research extension...", provider="openai")
    await asyncio.sleep(0.5)
    
    logger.info("Deep research complete", generated_tokens=150)
    return f"{basic_part} + [Deep Research: This topic is complex.]"


@app.post("/generate")
async def generate(req: GenerateRequest):
    logger.info("Received request")
    
    # Initializes top-level trace context with API request parameters
    with ai_trace(model=req.model, prompt_version=req.prompt_version):
        response = await generate_comprehensive_answer(req.user_query)
        
    return {"response": response}
