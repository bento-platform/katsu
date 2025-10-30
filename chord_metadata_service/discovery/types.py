from bento_lib.discovery import DiscoveryEntity
from typing import NotRequired, TypeAlias, TypedDict

__all__ = [
    "ModelScopeFilters",
    "EntityCounts",
    "EntityCountOrBoolResponse",
]


class ScopeLevelFilters(TypedDict):
    # If filter is a tuple, the field contains multiple filters that are ORed together. This is useful for, e.g., the
    # Resource model, where there are multiple possible paths one can take from the object to the parent dataset(s).
    filter: str | tuple[str, ...]
    prefetch_related: NotRequired[tuple[str, ...]]


class ModelScopeFilters(TypedDict):
    base_prefetch_related: tuple[str, ...]  # scope-related prefetches to includ on all querysets (scoped or instance)
    project: ScopeLevelFilters
    dataset: ScopeLevelFilters


EntityCounts: TypeAlias = dict[DiscoveryEntity, int]
EntityCountOrBoolResponse: TypeAlias = dict[DiscoveryEntity, int | bool]
