from bento_lib.discovery import FieldDefinition, OverviewSection, DiscoveryEntity
from pydantic import BaseModel, RootModel

from .types import ModelCountOrBoolResponse

__all__ = [
    "BinWithValue",
    "DiscoveryFieldResponse",
    "DiscoveryFieldResponses",
    "DiscoveryResponse",
    "DiscoveryQuery",
]


class BinWithValue(BaseModel):
    label: str
    value: int


class DiscoveryFieldResponse(BaseModel):
    id: str
    definition: FieldDefinition
    data: list[BinWithValue]


class DiscoveryFieldResponses(RootModel):
    root: dict[str, DiscoveryFieldResponse]


class DiscoveryMatches(RootModel):
    root: dict[DiscoveryEntity, list[str]]  # dictionary of {model name: [list of IDs]}


class DiscoveryResponse(BaseModel):
    layout: list[OverviewSection]
    fields: DiscoveryFieldResponses
    # results section:
    #  - "counts" can be either booleans or counts, depending on permissions level.
    #  - these counts can be aggregated at the level of dataset (nested in project), project, or just whatever scope was
    #    queried (flat).
    counts: (
        ModelCountOrBoolResponse | dict[str, ModelCountOrBoolResponse] | dict[str, dict[str, ModelCountOrBoolResponse]]
    )
    matches: DiscoveryMatches | dict[str, DiscoveryMatches] | dict[str, dict[str, DiscoveryMatches]] | None = None


class DiscoveryQuery(RootModel):
    """
    Model for discovery filtering queries. Right now, this is just a dictionary of {discovery field ID: value} extracted
    from query parameters minus project/dataset, but this could be extended in the future.
    """

    root: dict[str, str]

    def __iter__(self):
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)

    def items(self):
        return self.root.items()

    def queried_fields(self) -> list[str]:
        return list(self.root.keys())
