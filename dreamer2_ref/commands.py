from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ParsedCommand:
    verb: str
    payload: str
    explicit: bool
    raw: str


def parse_shell_input(raw: str, known_verbs: set[str]) -> ParsedCommand:
    stripped = raw.strip()
    if not stripped:
        return ParsedCommand(verb="send", payload="", explicit=False, raw=raw)

    verb, _, remainder = stripped.partition(" ")
    lowered = verb.lower()
    if lowered in known_verbs or lowered in {"quit", "exit"}:
        return ParsedCommand(
            verb=lowered,
            payload=remainder.strip(),
            explicit=True,
            raw=raw,
        )

    return ParsedCommand(
        verb="send",
        payload=stripped,
        explicit=False,
        raw=raw,
    )
