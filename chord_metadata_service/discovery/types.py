from bento_lib.discovery import (
    DateFieldDefinition,
    DiscoveryEntity,
    FieldDefinition,
    NumberFieldDefinition,
    StringFieldDefinition,
)
from typing import Literal, NotRequired, TypeAlias, TypedDict

__all__ = [
    "ModelScopeFilters",
    "EntityCounts",
    "EntityCountOrBoolResponse",
    "DiscoveryResponseFormat",
    "AcceptedDiscoveryResponseFormats",
    "AnyFieldDefinition",
]


class ScopeLevelFilters(TypedDict):
    # If filter is a tuple, the field contains multiple filters that are ORed together. This is useful for, e.g., the
    # Resource model, where there are multiple possible paths one can take from the object to the parent dataset(s).
    filter: str | tuple[str, ...]
    prefetch_related: NotRequired[tuple[str, ...]]  # optional (currently unused): additional prefetches for this level


class ModelScopeFilters(TypedDict):
    base_prefetch_related: tuple[str, ...]  # scope-related prefetches to include on all querysets (scoped or instance)
    project: ScopeLevelFilters
    dataset: ScopeLevelFilters


EntityCounts: TypeAlias = dict[DiscoveryEntity, int]
EntityCountOrBoolResponse: TypeAlias = dict[DiscoveryEntity, int | bool]

DiscoveryResponseFormat = Literal["json", "csv"]
AcceptedDiscoveryResponseFormats: TypeAlias = frozenset[DiscoveryResponseFormat]

AnyFieldDefinition: TypeAlias = FieldDefinition | NumberFieldDefinition | StringFieldDefinition | DateFieldDefinition
