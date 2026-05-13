from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from itertools import islice
from typing import TypeVar

T = TypeVar("T")


def batched(items: Iterable[T], batch_size: int) -> Iterator[tuple[T, ...]]:
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0")

    iterator = iter(items)
    while batch := tuple(islice(iterator, batch_size)):
        yield batch


def materialize(items: Iterable[T] | Sequence[T]) -> tuple[T, ...]:
    if isinstance(items, tuple):
        return items
    return tuple(items)
