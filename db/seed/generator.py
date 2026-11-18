"""Schema-free deterministic row generation primitives for fabricated data."""

from __future__ import annotations

import random
from collections.abc import Callable, Mapping
from typing import TypeVar


Row = TypeVar("Row", bound=Mapping[str, object])


def generate_rows(
    count: int,
    row_factory: Callable[[random.Random], Row],
    *,
    seed: int,
) -> list[dict[str, object]]:
    """Generate deterministic fabricated rows without defining a data shape."""
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("count must be a non-negative integer")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    if not callable(row_factory):
        raise TypeError("row_factory must be callable")

    random_source = random.Random(seed)
    rows: list[dict[str, object]] = []
    for _ in range(count):
        row = row_factory(random_source)
        if not isinstance(row, Mapping):
            raise TypeError("row_factory must return a mapping")
        rows.append(dict(row))
    return rows
