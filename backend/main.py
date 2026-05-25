"""
FastAPI backend for the AI Research Agent.
Exposes a single POST /research endpoint that streams SSE events.
"""
from __future__ import annotations

import json

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


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "ai-research-agent"}


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
