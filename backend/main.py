"""
FastAPI backend for the AI Research Agent.
Exposes a single POST /research endpoint that streams SSE events.
"""
from __future__ import annotations

import json
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from agent import ResearchAgent

app = FastAPI(title="AI Research Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    question: str


@app.get("/")
async def root() -> dict:
    import groq_llm
    return {
        "name": "AI Research Agent API",
        "version": "1.0.0",
        "status": "running",
        "llm": "groq" if groq_llm.IS_ACTIVE else "rule-based",
        "docs": "/docs",
        "endpoints": ["/health", "/research"],
    }


@app.get("/health")
async def health() -> dict:
    import groq_llm
    return {"status": "ok", "service": "ai-research-agent", "llm": "groq" if groq_llm.IS_ACTIVE else "rule-based"}


@app.post("/research")
async def research(request: ResearchRequest):
    """Stream agent reasoning steps as Server-Sent Events."""

    async def event_generator():
        agent = ResearchAgent()
        for step in agent.run(request.question):
            step_type = step.get("type", "unknown")
            yield {
                "event": step_type,
                "data": json.dumps(step),
            }

    return EventSourceResponse(event_generator())
