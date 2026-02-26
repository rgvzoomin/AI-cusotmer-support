from __future__ import annotations

import logging
from typing import Any

from openai import OpenAI

from app.rag.prompts import SYSTEM_PROMPT, build_user_prompt
from app.utils.config import get_settings

logger = logging.getLogger(__name__)


def _stub_answer(question: str, contexts: list[dict[str, Any]]) -> str:
    if not contexts:
        return (
            "I don't have enough verified documentation context to answer confidently. "
            "Please hand this ticket to a human support specialist."
        )
    bullets = '\n'.join([f"- {c['text'][:220]}" for c in contexts[:3]])
    return (
        "Based on available documentation, here are the most relevant steps:\n"
        f"{bullets}\n\n"
        "If this does not resolve the issue, escalate to human support with the ticket history."
    )


def generate_answer(question: str, contexts: list[dict[str, Any]]) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        return _stub_answer(question, contexts)

    try:
        client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
        completion = client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.2,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': build_user_prompt(question, contexts)},
            ],
        )
        return completion.choices[0].message.content or _stub_answer(question, contexts)
    except Exception as exc:  # pragma: no cover
        logger.exception('LLM generation failed, using stub fallback: %s', exc)
        return _stub_answer(question, contexts)
