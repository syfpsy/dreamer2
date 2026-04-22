"""Deterministic seeded randomness streams.

Named streams keep reproducibility. Given the same seed, memory tags,
and pack versions, the pipeline produces the same scene.
"""

from __future__ import annotations

import hashlib
import random


def stream(seed: str | int, name: str) -> random.Random:
    """Return a fresh random.Random seeded by the named stream."""
    blob = f"{seed}::{name}".encode()
    digest = hashlib.sha256(blob).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def stable_hash(seed: str | int, *parts: str | int) -> int:
    blob = "::".join([str(seed), *(str(p) for p in parts)]).encode()
    return int.from_bytes(hashlib.sha256(blob).digest()[:8], "big")
