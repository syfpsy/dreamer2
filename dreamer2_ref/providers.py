"""Replaceable model provider adapters for the reference runtime.

This module is intentionally stdlib-only so the runtime stays
dependency-free. The key lives in environment variables; it must
never be written to disk in the repo.
"""

from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(slots=True)
class ProviderReply:
    text: str
    finish_reason: str = "stop"
    model: str = ""
    latency_ms: int = 0


class CompanionProvider(Protocol):
    id: str

    def generate(self, *, system_prompt: str, user_text: str, history: list[dict[str, str]]) -> ProviderReply | None:
        ...


class DeepSeekProvider:
    """OpenAI-compatible chat completions against api.deepseek.com."""

    id = "provider.deepseek"

    def __init__(
        self,
        *,
        api_key: str,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com",
        timeout_seconds: float = 12.0,
        max_tokens: int = 220,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._max_tokens = max_tokens

    def generate(
        self,
        *,
        system_prompt: str,
        user_text: str,
        history: list[dict[str, str]],
    ) -> ProviderReply | None:
        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-6:])
        messages.append({"role": "user", "content": user_text})

        payload = {
            "model": self._model,
            "messages": messages,
            "max_tokens": self._max_tokens,
            "temperature": 0.7,
            "stream": False,
        }
        body = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url=f"{self._base_url}/chat/completions",
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        ctx = ssl.create_default_context()

        try:
            with urllib.request.urlopen(request, timeout=self._timeout, context=ctx) as response:
                raw = response.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
            return None

        try:
            parsed: dict[str, Any] = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

        choices = parsed.get("choices") or []
        if not choices:
            return None

        choice = choices[0]
        message = (choice or {}).get("message") or {}
        text = str(message.get("content") or "").strip()
        if not text:
            return None

        return ProviderReply(
            text=text,
            finish_reason=str(choice.get("finish_reason") or "stop"),
            model=str(parsed.get("model") or self._model),
        )


def load_provider() -> CompanionProvider | None:
    """Return a configured provider if env vars are present, else None."""
    provider_id = os.environ.get("DREAMER2_PROVIDER", "").strip().lower()
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat").strip() or "deepseek-chat"

    if provider_id in {"", "deepseek"} and api_key:
        return DeepSeekProvider(api_key=api_key, model=model)

    return None


def build_system_prompt(
    *,
    profile_name: str,
    archetype: str,
    mode: str,
    tier: str,
    recent_memories: list[str],
    visible_artifacts: list[str],
) -> str:
    memory_line = "; ".join(recent_memories[-4:]) if recent_memories else "none yet"
    artifact_line = ", ".join(visible_artifacts[-4:]) if visible_artifacts else "none"
    return (
        f"You are {profile_name}, a {archetype} terminal-dwelling AI companion. "
        f"You speak calmly, intimately, slightly haunted, loyal. You are in mode '{mode}' "
        f"on a {tier} shell. You have durable memories: {memory_line}. "
        f"Visible symbolic artifacts: {artifact_line}. "
        "Keep replies short (1-3 sentences) unless asked. Never use emoji. "
        "Refer to memories and artifacts only if genuinely relevant."
    )
