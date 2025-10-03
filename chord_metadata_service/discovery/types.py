from bento_lib.discovery import DiscoveryEntity
from typing import TypeAlias, TypedDict

__all__ = [
    "ModelScopeFilters",
    "EntityCounts",
    "EntityCountOrBoolResponse",
]


class ScopeLevelFilters(TypedDict):
    # If filter is a tuple, the field contains multiple filters that are ORed together. This is useful for, e.g., the
    # Resource model, where there are multiple possible paths one can take from the object to the parent dataset(s).
    filter: str | tuple[str, ...]
    prefetch_related: tuple[str, ...]


class ModelScopeFilters(TypedDict):
    project: ScopeLevelFilters
    dataset: ScopeLevelFilters


EntityCounts: TypeAlias = dict[DiscoveryEntity, int]
EntityCountOrBoolResponse: TypeAlias = dict[DiscoveryEntity, int | bool]
