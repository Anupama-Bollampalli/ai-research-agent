"""
ReAct (Reason-Act-Observe) Research Agent.

The agent iterates through a fixed reasoning loop:
  1. Analyse the question (thought)
  2. Web search for relevant information (tool_call)
  3. Summarise the search results (tool_call)
  4. Optionally fact-check a key claim if the question is specific (tool_call)
  5. Synthesise and stream the final answer (final_answer)
  6. Signal completion (done)
"""
from __future__ import annotations

import json
import re
import time
from typing import Generator


from tools import web_search, text_summarizer, fact_checker, calculator
import groq_llm


class ResearchAgent:
    """Streaming ReAct agent that yields reasoning steps as dicts."""

    # ------------------------------------------------------------------ #
    # Public interface
    # ------------------------------------------------------------------ #

    def run(self, question: str) -> Generator[dict, None, None]:
        """
        Execute the research loop for *question*.

        Yields dicts of the form:
          {"type": "thought",       "content": str}
          {"type": "tool_call",     "tool": str, "input": any, "output": any}
          {"type": "final_answer",  "content": str}
          {"type": "done"}
        """
        question = question.strip()

        # --- Step 1: Analyse the question ---
        yield self._thought(
            "Breaking down the question into key research areas. "
            f"The query '{question[:80]}{'...' if len(question) > 80 else ''}' "
            "touches on several distinct topics. "
            "I'll plan a multi-step research loop: first a broad web search, "
            "then summarisation of findings, followed by targeted fact-checking "
            "if the question contains specific claims or numbers."
        )

        # --- Step 2: Web search ---
        search_query = self._build_search_query(question)
        yield self._thought(
            f"I'll search for recent, authoritative information using the query: "
            f'"{search_query}". This should surface relevant technical sources.'
        )

        search_results = web_search(search_query)
        yield {
            "type": "tool_call",
            "tool": "web_search",
            "input": {"query": search_query},
            "output": search_results,
        }

        # --- Step 3: Summarise the search results ---
        yield self._thought(
            "I've retrieved the top search results. Now I'll concatenate the snippets "
            "and run the text summariser to distil the key points before reasoning further."
        )

        combined_snippets = "\n".join(
            f"[{r['title']}] {r['snippet']}" for r in search_results
        )
        summary_result = text_summarizer(combined_snippets)
        yield {
            "type": "tool_call",
            "tool": "text_summarizer",
            "input": {"text": combined_snippets},
            "output": summary_result,
        }

        # --- Step 4 (conditional): Fact-check a key claim ---
        if self._should_fact_check(question):
            key_claim = self._extract_key_claim(question, search_results)
            yield self._thought(
                f"The question contains a specific claim or assertion that warrants "
                f"independent verification. I'll run the fact checker on: \"{key_claim[:120]}\""
            )
            fact_result = fact_checker(key_claim)
            yield {
                "type": "tool_call",
                "tool": "fact_checker",
                "input": {"claim": key_claim},
                "output": fact_result,
            }
        else:
            fact_result = None

        # --- Step 5 (conditional): Calculator for numeric questions ---
        if self._should_calculate(question):
            expression = self._extract_expression(question)
            if expression:
                yield self._thought(
                    f"The question involves a numerical computation. "
                    f"I'll evaluate the expression: {expression}"
                )
                calc_result = calculator(expression)
                yield {
                    "type": "tool_call",
                    "tool": "calculator",
                    "input": {"expression": expression},
                    "output": calc_result,
                }
            else:
                calc_result = None
        else:
            calc_result = None

        # --- Step 6: Synthesise final answer ---
        yield self._thought(
            "Synthesising findings from web search, summarisation"
            + (", and fact-checking" if fact_result else "")
            + ". I now have enough information to compose a thorough, grounded answer."
        )

        final = self._compose_answer(
            question=question,
            search_results=search_results,
            summary=summary_result["summary"],
            fact_result=fact_result,
            calc_result=calc_result,
        )
        yield {"type": "final_answer", "content": final}
        yield {"type": "done"}

    # ------------------------------------------------------------------ #
    # Private helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _thought(content: str) -> dict:
        return {"type": "thought", "content": content}

    # -- Query planning ------------------------------------------------- #

    @staticmethod
    def _build_search_query(question: str) -> str:
        """Convert the raw question into a concise search query."""
        # Strip question marks and common filler words
        q = re.sub(r"[?!]+$", "", question.strip())
        q = re.sub(r"^(what|how|why|when|who|where|can you|please|tell me about|explain)\s+", "", q, flags=re.IGNORECASE)
        # Truncate to ~80 chars
        if len(q) > 80:
            q = q[:77] + "..."
        return q.strip()

    @staticmethod
    def _should_fact_check(question: str) -> bool:
        """Return True if the question contains a specific claim worth verifying."""
        triggers = [
            r"\d+\s*%",          # percentage figures
            r"\d+x\s",           # multipliers like "10x faster"
            r"\$\d+",            # dollar amounts
            r"\b(claim|assert|state|argue|says?|proven?|fact|true|false|myth)\b",
            r"\b(always|never|best|worst|fastest|slowest|most|least)\b",
            r"\b(billion|million|trillion)\b",
        ]
        q_lower = question.lower()
        return any(re.search(p, q_lower, re.IGNORECASE) for p in triggers)

    @staticmethod
    def _should_calculate(question: str) -> bool:
        """Return True if the question looks like it has a math component."""
        triggers = [
            r"\d+\s*[\+\-\*/\^]\s*\d+",   # arithmetic operators between numbers
            r"calculate|compute|how much is|what is \d",
            r"\d+\s*(plus|minus|times|divided by|mod)\s*\d+",
        ]
        return any(re.search(p, question, re.IGNORECASE) for p in triggers)

    @staticmethod
    def _extract_expression(question: str) -> str | None:
        """Try to pull a numeric expression from the question."""
        # Match things like "15 * 4 + 2" or "sqrt(144)"
        match = re.search(r"[\d\.\(\)\s\+\-\*/\^]+", question)
        if match:
            expr = match.group().strip()
            if re.search(r"\d", expr) and re.search(r"[\+\-\*/]", expr):
                return expr
        return None

    @staticmethod
    def _extract_key_claim(question: str, results: list[dict]) -> str:
        """Build the most specific verifiable claim from the question + top result."""
        # Use the first snippet as context for the claim
        if results:
            snippet = results[0]["snippet"]
            # Extract first sentence of the snippet
            first_sentence = re.split(r"(?<=[.!?])\s+", snippet)[0]
            return first_sentence
        return question

    # -- Answer synthesis ----------------------------------------------- #

    def _compose_answer(
        self,
        question: str,
        search_results: list[dict],
        summary: str,
        fact_result: dict | None,
        calc_result: dict | None,
    ) -> str:
        """Synthesise a final answer — uses Groq when available, structured markdown otherwise."""
        if groq_llm.IS_ACTIVE:
            return self._compose_answer_groq(question, search_results, summary, fact_result, calc_result)
        return self._compose_answer_fallback(question, search_results, summary, fact_result, calc_result)

    @staticmethod
    def _compose_answer_groq(
        question: str,
        search_results: list[dict],
        summary: str,
        fact_result: dict | None,
        calc_result: dict | None,
    ) -> str:
        sources_text = "\n".join(
            f"- [{r['title']}]: {r['snippet']}" for r in search_results
        )
        extra = ""
        if fact_result:
            extra += f"\nFact-check: {fact_result['verdict']} (confidence {fact_result['confidence']}%) — {fact_result['explanation']}"
        if calc_result and "result" in calc_result:
            extra += f"\nCalculation: {calc_result['expression']} = {calc_result['result']}"

        system = (
            "You are a research analyst. Write a well-structured, markdown-formatted answer. "
            "Use headings (##), bullet points, and bold key terms. "
            "Be informative but concise. Base your answer on the provided sources."
        )
        user = (
            f"Question: {question}\n\n"
            f"Web search findings:\n{sources_text}\n\n"
            f"Summarised overview: {summary}"
            f"{extra}"
        )
        try:
            return groq_llm.reason(system, user, temperature=0.5)
        except Exception:
            return ResearchAgent._compose_answer_fallback(question, search_results, summary, fact_result, calc_result)

    @staticmethod
    def _compose_answer_fallback(
        question: str,
        search_results: list[dict],
        summary: str,
        fact_result: dict | None,
        calc_result: dict | None,
    ) -> str:
        lines: list[str] = [
            f"## Research Summary\n",
            f"Based on my multi-step research into **\"{question}\"**, here is what I found:\n",
            "### Key Findings from Web Search\n",
        ]
        for r in search_results:
            lines.append(f"- **[{r['title']}]({r['url']})**: {r['snippet']}\n")
        lines.append("\n### Synthesised Overview\n")
        lines.append(summary + "\n")
        if fact_result:
            verdict_emoji = {"Likely True": "✅", "Partially True": "⚠️", "Unverified": "❓"}.get(fact_result["verdict"], "🔍")
            lines.append(f"\n### Fact-Check\n{verdict_emoji} **{fact_result['verdict']}** (confidence: {fact_result['confidence']}%)\n> {fact_result['explanation']}\n")
        if calc_result and "result" in calc_result:
            lines.append(f"\n### Calculation\n`{calc_result['expression']}` = **{calc_result['result']}**\n")
        lines.append("\n### Conclusion\nThe sources retrieved represent current thinking. Cross-reference with primary documentation for high-stakes decisions.")
        return "".join(lines)
