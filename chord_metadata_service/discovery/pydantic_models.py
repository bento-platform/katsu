from bento_lib.discovery import FieldDefinition, OverviewSection, DiscoveryEntity, SearchSection
from pydantic import BaseModel, Field, RootModel

from .types import ModelCountOrBoolResponse

__all__ = [
    "BinWithValue",
    "BinList",
    "DiscoveryFieldAndOptions",
    "DiscoveryFieldResponse",
    "DiscoveryFieldResponses",
    "MatchExperimentResult",
    "MatchExperiment",
    "MatchBiosample",
    "MatchPhenopacket",
    "DiscoveryMatches",
    "DiscoveryPagination",
    "DiscoveryResponse",
    "DiscoveryMatchesPaginatedResponse",
    "DiscoverySearchSectionWithOptions",
    "DiscoverySearchFieldsResponse",
    "DiscoveryQuery",
]


class BinWithValue(BaseModel):
    label: str
    value: int


class BinList(RootModel):
    root: list[BinWithValue]

    def append(self, b: BinWithValue):
        self.root.append(b)


class BaseDiscoveryResolvedField(BaseModel):
    id: str
    definition: FieldDefinition


class DiscoveryFieldAndOptions(BaseDiscoveryResolvedField):
    # field ID + field definition + field filter options
    options: list[str]


class DiscoveryFieldResponse(BaseDiscoveryResolvedField):
    # field ID + field definition + field data
    data: BinList


class DiscoveryFieldResponses(RootModel):
    root: dict[str, DiscoveryFieldResponse]


class MatchExperimentResult(BaseModel):
    id: int = Field(..., title="Experiment result ID")
    f: str | None = Field(..., title="File name")
    url: str | None = Field(..., title="URL")
    # list of experiment_result_file_index objects (see experiments/schemas.py)
    idx: list[dict] = Field(..., title="Indices")
    ff: str | None = Field(..., title="File format")
    g: str | None = Field(..., title="Genome assembly ID")


class MatchExperiment(BaseModel):
    """
    Compact representation of an experiment for returning/rendering search responses.
    """
    id: str = Field(..., title="Experiment ID")
    r: list[MatchExperimentResult]


class MatchBiosample(BaseModel):
    """
    Compact representation of a biosample for returning/rendering search responses.
    """
    id: str = Field(..., title="Biosample ID")
    p: str | None = Field(..., title="Phenopacket ID")
    e: list[MatchExperiment] | None


class MatchPhenopacket(BaseModel):
    """
    Compact representation of a phenopacket for returning/rendering search responses.
    """
    id: str = Field(..., title="Phenopacket ID")
    s: str | None = Field(..., title="Subject ID")
    b: list[MatchBiosample]


class DiscoveryMatches(RootModel):
    root: list[MatchPhenopacket] | list[MatchBiosample] | list[MatchExperiment] | list[MatchExperimentResult]


class DiscoveryPagination(BaseModel):
    page: int
    page_size: int
    total: int  # total count of matches, whichever output format is chosen


class DiscoveryResponse(BaseModel):
    layout: list[OverviewSection]
    fields: DiscoveryFieldResponses
    # results section:
    #  - root_entity is the "entity name" of the queryset model used to generate this response.
    #  - "counts" can be either booleans or counts, depending on permissions level.
    #  - these counts can be aggregated at the level of dataset (nested in project), project, or just whatever scope was
    #    queried (flat).
    root_entity: DiscoveryEntity
    counts: (
        ModelCountOrBoolResponse | dict[str, ModelCountOrBoolResponse] | dict[str, dict[str, ModelCountOrBoolResponse]]
    )


class DiscoveryMatchesPaginatedResponse(BaseModel):
    results_entity: DiscoveryEntity
    results: DiscoveryMatches | dict[str, DiscoveryMatches] | dict[str, dict[str, DiscoveryMatches]]
    pagination: DiscoveryPagination


class DiscoverySearchSectionWithOptions(SearchSection):
    fields: list[DiscoveryFieldAndOptions]


class DiscoverySearchFieldsResponse(BaseModel):
    sections: list[DiscoverySearchSectionWithOptions]


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
