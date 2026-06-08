"""Shared LLM client utility.

Provides a common OpenAI client and chat helper used by both the LLM
reasoner and problem parser modules.
"""

from __future__ import annotations

import os
import structlog
from typing import Any

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None  # type: ignore[assignment,misc]


logger = structlog.get_logger()

_client: Any = None


def get_openai_client() -> Any:
    """Get or create a cached OpenAI client.

    Returns:
        AsyncOpenAI client instance (cached after first call).

    Raises:
        ImportError: If openai package is not installed.
        ValueError: If OPENAI_API_KEY is not set.
    """
    global _client
    if _client is not None:
        return _client
    if AsyncOpenAI is None:
        raise ImportError("openai package is required. Install with: pip install openai")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required.")
    _client = AsyncOpenAI(api_key=api_key)
    return _client


async def chat_completion(
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
) -> str:
    """Make an OpenAI chat completion call.

    Args:
        model: Model name (e.g., "gpt-4").
        system_prompt: System message content.
        user_prompt: User message content.
        temperature: Sampling temperature.

    Returns:
        The assistant's response text.
    """
    client = get_openai_client()
    response = await client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content or ""


def strip_json_fences(raw: str) -> str:
    """Strip markdown code fences from JSON output.

    Args:
        raw: Raw string that may contain ```json ... ``` fences.

    Returns:
        Cleaned string with fences removed.
    """
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        if "\n" in cleaned:
            cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
    return cleaned
