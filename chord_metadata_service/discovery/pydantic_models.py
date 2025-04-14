from bento_lib.discovery import FieldDefinition, OverviewSection
from pydantic import BaseModel


__all__ = [
    "BinWithData",
    "DiscoveryFieldResponse",
    "OverviewResponseCounts",
    "OverviewResponse",
]


class BinWithData(BaseModel):
    label: str
    value: int


class DiscoveryFieldResponse(BaseModel):
    id: str
    definition: FieldDefinition
    data: list[BinWithData] | None


class OverviewResponseCounts(BaseModel):
    individuals: int | None = None
    biosamples: int | None = None
    experiments: int | None = None


class OverviewResponse(BaseModel):
    layout: list[OverviewSection]
    fields:  dict[str, DiscoveryFieldResponse]
    counts: OverviewResponseCounts
