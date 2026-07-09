"""
Level 4: Cloud/Premium Escalation
Only called when the fast tier's confidence is too low.

Two modes, chosen automatically:
- If ANTHROPIC_API_KEY is set: uses Claude (real, small per-token cost --
  this is the "paid tier" your project's cost-savings story is about).
- If not set: falls back to Groq's larger free-tier model as a stand-in
  "premium" tier, so the WHOLE app still runs at zero cost with nothing
  to configure. Clearly labelled in the response either way.
"""
import os
import re
import requests

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_PREMIUM_MODEL = "llama-3.3-70b-versatile"  # bigger free-tier Groq model, used as fallback

# Rough public per-token pricing for cost estimation (update if pricing changes)
INPUT_COST_PER_TOKEN = 3.0 / 1_000_000    # example: $3 per million input tokens
OUTPUT_COST_PER_TOKEN = 15.0 / 1_000_000  # example: $15 per million output tokens


def query_cloud_model(query: str):
    """
    Returns (answer_text, estimated_cost_usd, provider_used).
    """
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    groq_api_key = os.environ.get("GROQ_API_KEY")

    if anthropic_api_key:
        return _query_claude(query, anthropic_api_key)
    if groq_api_key:
        return _query_groq_premium(query, groq_api_key)
    raise RuntimeError(
        "No API key set for Level 4. Set either ANTHROPIC_API_KEY (paid, "
        "real cost-savings demo) or GROQ_API_KEY (free fallback) as an "
        "environment variable."
    )


def _query_claude(query: str, anthropic_api_key: str):
    from anthropic import Anthropic  # imported lazily so this file loads fine without the package configured

    client = Anthropic(api_key=anthropic_api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": query}],
    )
    answer = "".join(block.text for block in response.content if block.type == "text")

    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    cost = (input_tokens * INPUT_COST_PER_TOKEN) + (output_tokens * OUTPUT_COST_PER_TOKEN)

    return answer, round(cost, 6), "claude"


def _query_groq_premium(query: str, groq_api_key: str):
    response = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_PREMIUM_MODEL,
            "messages": [{"role": "user", "content": query}],
            "temperature": 0.3,
        },
        timeout=30,
    )
    response.raise_for_status()
    answer = response.json()["choices"][0]["message"]["content"]
    return answer, 0.0, "groq_premium_fallback"
