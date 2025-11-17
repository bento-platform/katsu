import abc

from bento_lib.discovery import FieldDefinition, OverviewSection, DiscoveryEntity, SearchSection
from pydantic import BaseModel, Field, RootModel
from rest_framework.request import Request as DrfRequest
from typing import TypeAlias, Literal

from chord_metadata_service.experiments.types import ExperimentResultFileFormat
from .types import EntityCountOrBoolResponse

__all__ = [
    "BinWithValue",
    "BinList",
    "DiscoveryFieldAndOptions",
    "DiscoveryFieldResponse",
    "DiscoveryFieldResponses",
    "BaseMatchModel",
    "ExperimentResultIndex",
    "ExperimentResultIndices",
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
    "DiscoveryUIHintsResponse",
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
    project: str | None = Field(default=None, title="Project ID")
    dataset: str | None = Field(default=None, title="Dataset ID")


class ExperimentResultIndex(BaseModel):
    url: str
    format: Literal[
        "BAI",  # BAM index files ( http://samtools.github.io/hts-specs/SAMv1.pdf "BAI" )
        "BGZF",  # BGZip index files (often .gzi)
        "CRAI",  # CRAM index files ( https://samtools.github.io/hts-specs/CRAMv3.pdf "CRAM index" )
        "CSI",  # See http://samtools.github.io/hts-specs/CSIv1.pdf
        "TABIX",  # See https://samtools.github.io/hts-specs/tabix.pdf
        "TRIBBLE",
    ]


class ExperimentResultIndices(RootModel):
    root: list[ExperimentResultIndex]


# TODO: just merge this with the main serializer; there's no point in returning a subset -- possibly via drf-pydantic
class MatchExperimentResult(BaseMatchModel):
    id: int = Field(..., title="Experiment result ID")
    identifier: str = Field(..., title="Experiment result laboratory identifier")
    description: str = Field(..., title="Description")
    filename: str | None = Field(..., title="File name")
    url: str | None = Field(..., title="URL")
    indices: ExperimentResultIndices = Field(..., title="Indices")
    file_format: ExperimentResultFileFormat | None = Field(..., title="File format")
    data_output_type: Literal["Raw data", "Derived data"] | None = Field(..., title="Data output type")
    usage: str | None = Field(..., title="Usage")
    creation_date: str | None = Field(..., title="Creation date")
    created_by: str | None = Field(..., title="Created by")
    genome_assembly_id: str | None = Field(..., title="Genome assembly ID")
    extra_properties: dict = Field(..., title="Extra properties")
    # TODO: experiments backlink


class MatchExperiment(BaseMatchModel):
    """
    Compact representation of an experiment for returning/rendering search responses.
    """
    id: str = Field(..., title="Experiment ID")
    experiment_type: str = Field(..., title="Experiment Type")
    study_type: str = Field(..., title="Study Type")
    results: list[MatchExperimentResult]
    # backlink:
    phenopacket: str | None = Field(..., title="Phenopacket ID")


class MatchBiosample(BaseMatchModel):
    """
    Compact representation of a biosample for returning/rendering search responses.
    """
    id: str = Field(..., title="Biosample ID")
    # sampled_tissue: OntologyTerm | None
    # sample_type: OntologyTerm | None
    individual_id: str | None = Field(..., title="Individual ID")
    phenopacket: str | None = Field(..., title="Phenopacket ID")
    experiments: list[MatchExperiment] | None


class MatchPhenopacket(BaseMatchModel):
    """
    Compact representation of a phenopacket for returning/rendering search responses.
    """
    id: str = Field(..., title="Phenopacket ID")
    subject: str | None = Field(..., title="Subject ID")
    biosamples: list[MatchBiosample]


class MatchIndividual(BaseMatchModel):
    """
    Compact representation of a subject for returning/rendering search responses.
    """
    id: str = Field(..., title="Subject ID")
    phenopackets: list[MatchPhenopacket]


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
        EntityCountOrBoolResponse |
        dict[str, EntityCountOrBoolResponse] |
        dict[str, dict[str, EntityCountOrBoolResponse]]
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

        if request.method not in ("GET", "POST"):
            raise NotImplementedError("from_drf_request implemented for GET|POST only")

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


class DiscoveryUIHintsResponse(BaseModel):
    """
    Model representing the UI hints discovery response, which gives any API consumer some hints/suggestions on how to
    make the UI nicer by, e.g., selectively hiding parts.
    """

    entities_with_data: list[DiscoveryEntity]
    # biosample_location_present: bool  TODO
