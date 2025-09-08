import abc

from bento_lib.discovery import FieldDefinition, OverviewSection, DiscoveryEntity, SearchSection
from pydantic import BaseModel, Field, RootModel
from rest_framework.request import Request as DrfRequest
from typing import TypeAlias

from .types import ModelCountOrBoolResponse

__all__ = [
    "BinWithValue",
    "BinList",
    "DiscoveryFieldAndOptions",
    "DiscoveryFieldResponse",
    "DiscoveryFieldResponses",
    "BaseMatchModel",
    "MatchExperimentResult",
    "MatchExperiment",
    "MatchBiosample",
    "MatchPhenopacket",
    "MatchIndividual",
    "MatchObject",
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


class BaseMatchModel(BaseModel, abc.ABC):
    pr: str | None = Field(default=None, title="Project ID")
    ds: str | None = Field(default=None, title="Dataset ID")


class MatchExperimentResult(BaseMatchModel):
    id: int = Field(..., title="Experiment result ID")
    f: str | None = Field(..., title="File name")
    url: str | None = Field(..., title="URL")
    # list of experiment_result_file_index objects (see experiments/schemas.py)
    idx: list[dict] = Field(..., title="Indices")
    ff: str | None = Field(..., title="File format")
    g: str | None = Field(..., title="Genome assembly ID")


class MatchExperiment(BaseMatchModel):
    """
    Compact representation of an experiment for returning/rendering search responses.
    """
    id: str = Field(..., title="Experiment ID")
    r: list[MatchExperimentResult]


class MatchBiosample(BaseMatchModel):
    """
    Compact representation of a biosample for returning/rendering search responses.
    """
    id: str = Field(..., title="Biosample ID")
    p: str | None = Field(..., title="Phenopacket ID")
    e: list[MatchExperiment] | None


class MatchPhenopacket(BaseMatchModel):
    """
    Compact representation of a phenopacket for returning/rendering search responses.
    """
    id: str = Field(..., title="Phenopacket ID")
    s: str | None = Field(..., title="Subject ID")
    b: list[MatchBiosample]


class MatchIndividual(BaseMatchModel):
    """
    Compact representation of a subject for returning/rendering search responses.
    """
    id: str = Field(..., title="Subject ID")
    p: list[MatchPhenopacket]


MatchObject: TypeAlias = (
    list[MatchPhenopacket] |
    list[MatchIndividual] |
    list[MatchBiosample] |
    list[MatchExperiment] |
    list[MatchExperimentResult]
)


class DiscoveryMatches(RootModel):
    root: MatchObject


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
    queried_entities: frozenset[DiscoveryEntity]
    message: str = ""  # A message related to the response, e.g., insufficient data. If blank, it shouldn't be shown.
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


class DiscoveryQuery(BaseModel):
    """
    Model for discovery filtering queries. Right now, this is just a dictionary of {discovery field ID: value} extracted
    from query parameters minus project/dataset, but this could be extended in the future.
    """

    fts: str | None
    filters: dict[str, str]

    def queried_filter_fields(self) -> list[str]:
        return list(self.filters.keys())

    @classmethod
    def from_drf_request(cls, request: DrfRequest) -> "DiscoveryQuery":
        """
        Given a Django REST Framework request object from a discovery/discovery-matches request, return a validated
        DiscoveryQuery object.
        """

        params = request.query_params if request.method == "GET" else request.data

        # Process query parameters and check validity
        filters: dict[str, str] = {
            k: v[0] if isinstance(v, list) else v
            for k, v in params.items()
            if k and k not in ("project", "dataset") and k[0] != "_"
            # - remove project/dataset (i.e., scope) query parameters; otherwise, they get included in the fields and
            #   the response yields an error, as they are (presumably) not queryable fields in the discovery config.
            # - remove "special" query parameters, which start with "_" (for pagination or other non-filter uses)
        }

        return cls(fts=params.get("_fts") or None, filters=filters)
