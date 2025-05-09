from bento_lib.discovery import FieldDefinition, OverviewSection
from pydantic import BaseModel, RootModel
from .model_lookups import PublicModelName

__all__ = [
    "BinWithValue",
    "DiscoveryFieldResponse",
    "DiscoveryFieldResponses",
    "DiscoveryOverviewResponse",
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


class DiscoveryOverviewResponse(BaseModel):
    layout: list[OverviewSection]
    fields: DiscoveryFieldResponses
    counts: dict[PublicModelName, int | bool]


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
