"""
engine/llm_client.py
--------------------
Thin abstraction layer over the OpenAI API.

Responsibilities:
    1. Read the API key from the environment (loaded from .env by app.py at startup).
    2. Send a prompt string to the model and return a structured result dict.
    3. Capture token usage and wall-clock latency for the evaluation engine.

Why a wrapper instead of calling OpenAI directly?
    Centralising the API call means we can swap providers (Anthropic, Groq, etc.)
    by editing one file instead of every strategy. The rest of the codebase only
    sees the generic {"response", "input_tokens", "output_tokens", "latency_seconds"}
    dict, which is provider-agnostic.

Model choice — gpt-4o-mini:
    Cheap (~$0.00015 / 1K input tokens), fast (~1–2 s), capable enough to show
    clear differences between prompting strategies. For a lab demo this is ideal:
    each full 7-strategy run costs roughly $0.01 total.

Environment:
    OPENAI_API_KEY must be set in promptforge/.env before starting the app.
"""

import os
import time
from openai import OpenAI


def get_client() -> OpenAI:
    """
    Construct and return an authenticated OpenAI client.

    Reads OPENAI_API_KEY from the process environment. The key is injected at
    startup via python-dotenv's load_dotenv() call in app.py.

    Returns:
        OpenAI: Configured client instance ready to make API calls.

    Raises:
        ValueError: If OPENAI_API_KEY is not present in the environment.
                    This surfaces as a visible st.error() in the dashboard.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment")
    return OpenAI(api_key=api_key)


def call_llm(
    prompt: str,
    model: str = "gpt-4o-mini",
    max_tokens: int = 1024,
) -> dict:
    """
    Send a single prompt to the LLM and return the response with metadata.

    The prompt is sent as a single user message (no system message). All 7
    prompting strategies rely on this same function — the only variable is the
    content of `prompt`. This is what makes the evaluation controlled: same model,
    same temperature (OpenAI default = 1.0), same max_tokens, different prompt.

    Args:
        prompt     : The fully assembled prompt string produced by a strategy builder.
        model      : OpenAI model ID. Default is gpt-4o-mini (fast and cheap).
        max_tokens : Upper bound on response length in tokens (not words).

    Returns:
        dict with keys:
            "response"         (str)   — Raw text content of the model's reply.
            "input_tokens"     (int)   — Tokens consumed by the prompt.
            "output_tokens"    (int)   — Tokens in the model's response.
            "latency_seconds"  (float) — Wall-clock time for the API round-trip.
            "model"            (str)   — Model ID used (useful if overridden).

    Raises:
        openai.APIError or subclass: Propagated to the caller; caught by the
        try/except in app.py's run loop and displayed as st.error().
    """
    client = get_client()

    # Record start time before the blocking API call so latency includes
    # network overhead, which is meaningful for token-efficiency comparison.
    start = time.time()

    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        # Single user turn — no system message. The prompting strategy itself
        # is responsible for setting context, role, and format instructions.
        messages=[{"role": "user", "content": prompt}],
    )

    elapsed = time.time() - start

    # Extract the text from the first (and only) completion choice.
    content = response.choices[0].message.content

    return {
        "response": content,
        # prompt_tokens = input tokens billed; completion_tokens = output tokens billed
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "latency_seconds": round(elapsed, 2),
        "model": model,
    }
