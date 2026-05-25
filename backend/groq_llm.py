"""
Groq LLM client for the Research Agent.
Falls back gracefully to rule-based mode if GROQ_API_KEY is not set or client fails to init.
"""
import os

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
IS_ACTIVE = False
_client = None

try:
    from groq import Groq
    _api_key = os.environ.get("GROQ_API_KEY", "")
    if _api_key:
        _client = Groq(api_key=_api_key)
        IS_ACTIVE = True
        print(f"✓ Groq active for agent reasoning (model: {GROQ_MODEL})")
    else:
        print("⚠  GROQ_API_KEY not set — agent uses rule-based reasoning")
except Exception as e:
    print(f"⚠  Groq init failed ({e}) — agent uses rule-based reasoning")


def reason(system_prompt: str, user_message: str, temperature: float = 0.4) -> str:
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
