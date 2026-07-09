"""
Level 3: Fast Tier Model (via Groq's free API)
Replaces the earlier Ollama-based design. Ollama requires a persistent
local process and real RAM (2GB+), which free hosting tiers (Render,
Railway, etc.) don't support -- so it would break immediately after
deployment. Groq's free tier hosts fast open models (Llama, etc.) via
a simple API call, works identically whether running on your laptop
or a deployed server, and needs zero local compute.

Get a free API key at https://console.groq.com
Set it as: export GROQ_API_KEY="your-key-here"
"""
import os
import re
import requests

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
FAST_MODEL_NAME = "llama-3.1-8b-instant"  # free-tier, fast; check console.groq.com for current model list


def query_fast_model(query: str, domain: str = "general"):
    """
    Calls Groq's hosted model. Returns (answer_text, confidence_score).
    Confidence is self-reported by the model (0-100), parsed from its own output.
    """
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY not set. Get a free key at https://console.groq.com "
            "and set it as an environment variable."
        )

    prompt = _build_prompt(query, domain)

    response = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": FAST_MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
        timeout=30,
    )
    response.raise_for_status()
    raw_output = response.json()["choices"][0]["message"]["content"]

    answer, confidence = _parse_answer_and_confidence(raw_output)
    return answer, confidence


def _build_prompt(query: str, domain: str) -> str:
    domain_hint = "" if domain == "general" else f" This is a {domain.replace('_', ' ')} question."
    return (
        f"Answer the following question clearly and concisely.{domain_hint}\n\n"
        f"Question: {query}\n\n"
        f"After your answer, on a new line write exactly:\n"
        f"CONFIDENCE: <a number from 0 to 100 representing how confident you are "
        f"in the correctness and completeness of your answer>\n"
    )


def _parse_answer_and_confidence(raw_output: str):
    match = re.search(r"CONFIDENCE:\s*(\d+)", raw_output, re.IGNORECASE)
    confidence = int(match.group(1)) if match else 50

    answer = re.sub(r"CONFIDENCE:\s*\d+", "", raw_output, flags=re.IGNORECASE).strip()
    return answer, confidence
