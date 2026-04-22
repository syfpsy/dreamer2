"""Deterministic seeded randomness streams.

Named streams keep reproducibility. Given the same seed, memory tags,
and pack versions, the pipeline produces the same scene.
"""

from __future__ import annotations

import hashlib
import random
from typing import Union


def stream(seed: Union[str, int], name: str) -> random.Random:
    """Return a fresh random.Random seeded by the named stream."""
    blob = f"{seed}::{name}".encode("utf-8")
    digest = hashlib.sha256(blob).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def stable_hash(seed: Union[str, int], *parts: Union[str, int]) -> int:
    blob = "::".join([str(seed), *(str(p) for p in parts)]).encode("utf-8")
    return int.from_bytes(hashlib.sha256(blob).digest()[:8], "big")
