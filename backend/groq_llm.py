"""
Groq LLM client for the Research Agent.
Falls back gracefully to None if GROQ_API_KEY is not set.
"""
import os

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

try:
    from groq import Groq
    _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    IS_ACTIVE = True
    print(f"✓ Groq active for agent reasoning (model: {GROQ_MODEL})")
except (ImportError, KeyError):
    _client = None
    IS_ACTIVE = False
    print("⚠  GROQ_API_KEY not set — agent uses rule-based reasoning")


def reason(system_prompt: str, user_message: str, temperature: float = 0.4) -> str:
    """Call Groq and return the assistant reply, or raise if not configured."""
    if not IS_ACTIVE or _client is None:
        raise RuntimeError("Groq not configured")
    response = _client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=temperature,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content.strip()
