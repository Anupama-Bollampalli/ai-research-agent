# AI Research Agent

A multi-step agentic AI system implementing the ReAct (Reason-Act-Observe) pattern. The agent breaks down research questions, uses tools to gather and verify information, then synthesises a final answer — streaming every reasoning step to the UI in real time.

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────┐
│              Agent Loop                 │
│  1. Thought  →  reason about question   │
│  2. Act      →  call a tool             │
│  3. Observe  →  inspect tool result     │
│  4. Repeat until answer is ready        │
└───────────────────┬─────────────────────┘
                    │
          ┌─────────▼─────────┐
          │      Tools        │
          │  🔍 web_search    │
          │  📝 summarizer    │
          │  ✅ fact_checker  │
          │  🧮 calculator    │
          └─────────┬─────────┘
                    │  SSE stream
                    ▼
          ┌─────────────────┐
          │   React UI      │
          │  ThoughtStream  │
          │  ToolCallCard   │
          │  FinalAnswer    │
          └─────────────────┘
```

## Tech Stack

Python · FastAPI · SSE (Server-Sent Events) · ReAct Pattern · React 18 · TypeScript · Tailwind CSS · Vite

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173/ai-research-agent/

## Extending

- **Real web search**: Replace mock `web_search` with SerpAPI — `pip install google-search-results` and swap the implementation in `tools.py`.
- **More tools**: Add a function to `tools.py` (following the same signature conventions) and register it in the `agent.py` dispatch logic.
- **Real LLM reasoning**: Replace the rule-based `ResearchAgent` in `agent.py` with calls to the Anthropic or OpenAI API for fully dynamic reasoning chains.
- **Persistent memory**: Add a vector store (e.g. Chroma) to cache past research results and surface them in future queries.
