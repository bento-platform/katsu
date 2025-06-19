from typing import TypedDict

__all__ = [
    "BinWithValue",
    "ModelScopeFilters",
]


class BinWithValue(TypedDict):
    label: str
    value: int


class ScopeLevelFilters(TypedDict):
    # If filter is a tuple, the field contains multiple filters that are ORed together. This is useful for, e.g., the
    # Resource model, where there are multiple possible paths one can take from the object to the parent dataset(s).
    filter: str | tuple[str, ...]
    prefetch_related: tuple[str, ...]


class ModelScopeFilters(TypedDict):
    project: ScopeLevelFilters
    dataset: ScopeLevelFilters
