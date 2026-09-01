import abc
import sys

from bento_lib.discovery import FieldDefinition, OverviewSection, DiscoveryEntity, SearchSection, DiscoveryConfig
from bento_lib.ontologies.models import OntologyClass
from django.core.exceptions import ValidationError
from django.http import QueryDict
from pydantic import AnyUrl, BaseModel, ConfigDict, Field, RootModel
from rest_framework.request import Request as DrfRequest
from typing import Literal, Self

from chord_metadata_service.authz.types import (
    DataPermissionsLevel,
    DataTypeDiscoveryPermissions,
    DataPermissions,
    FieldDiscoveryPermissions,
)
from chord_metadata_service.experiments.types import ExperimentResultFileFormat
from .censorship import get_max_query_parameters
from .scope import ValidatedDiscoveryScope
from .types import EntityCountOrBoolResponse, FTSType
from .utils import get_discovery_field_set_permissions

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
    "DiscoveryQueryFilterOneOf",
    "DiscoveryQuery",
    "DiscoveryUIHintsResponse",
]


class BinWithValue(BaseModel):
    model_config = ConfigDict(frozen=True)

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
    model_config = ConfigDict(frozen=True)

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
    storage_uri: AnyUrl | None = Field(..., title="Storage URI")
    storage_server: str | None = Field(..., title="Storage server")
    file_format: ExperimentResultFileFormat | None = Field(..., title="File format")
    data_output_type: Literal["Raw data", "Derived data"] | None = Field(..., title="Data output type")
    usage: str | None = Field(..., title="Usage")
    creation_date: str | None = Field(..., title="Creation date")
    created_by: str | None = Field(..., title="Created by")
    genome_assembly_id: str | None = Field(..., title="Genome assembly ID")
    extra_properties: dict = Field(..., title="Extra properties")
    # backlinks to linked experiments
    experiments: list[str] = Field(
        ..., title="Experiment IDs", description="Experiments which link to this experiment result."
    )
    # backlink to phenopacket
    phenopacket: str | None = Field(..., title="Phenopacket ID")


class MatchExperiment(BaseMatchModel):
    """
    Compact representation of an experiment for returning/rendering search responses.
    """

    id: str = Field(..., title="Experiment ID")
    description: str | None = Field(..., title="Description")
    experiment_type: str = Field(..., title="Experiment Type")
    experiment_ontology: OntologyClass | None = Field(..., title="Experiment Type (Ontology)")
    study_type: str | None = Field(..., title="Study Type")
    molecule: str | None = Field(..., title="Molecule")
    molecule_ontology: OntologyClass | None = Field(..., title="Molecule (Ontology)")
    extra_properties: dict = Field(..., title="Extra properties")
    # nested entities:
    results: list[MatchExperimentResult]
    # backlinks:
    biosample: str | None = Field(..., title="Biosample ID")
    phenopacket: str | None = Field(..., title="Phenopacket ID")


class MatchBiosample(BaseMatchModel):
    """
    Compact representation of a biosample for returning/rendering search responses.
    """

    id: str = Field(..., title="Biosample ID")
    description: str = Field(..., title="Description")
    sampled_tissue: OntologyClass | None = Field(..., title="Sampled Tissue")
    sample_type: OntologyClass | None = Field(..., title="Sample Type")
    taxonomy: OntologyClass | None = Field(..., title="Taxonomy")
    extra_properties: dict = Field(..., title="Extra Properties")
    # nested entities:
    experiments: list[MatchExperiment] | None
    # backlinks:
    individual_id: str | None = Field(..., title="Individual ID")
    phenopacket: str | None = Field(..., title="Phenopacket ID")


class MatchPhenopacket(BaseMatchModel):
    """
    Compact representation of a phenopacket for returning/rendering search responses.
    """

    id: str = Field(..., title="Phenopacket ID")
    subject: str | None = Field(..., title="Subject ID")
    biosamples: list[MatchBiosample]
    extra_properties: dict = Field(..., title="Extra Properties")


class MatchIndividual(BaseMatchModel):
    """
    Compact representation of a subject for returning/rendering search responses.
    """

    id: str = Field(..., title="Subject ID")
    sex: str | None = Field(..., title="Sex")
    karyotypic_sex: str | None = Field(..., title="Karyotypic Sex")
    phenopackets: list[MatchPhenopacket]
    extra_properties: dict = Field(..., title="Extra properties")


type MatchObject = (
    list[MatchPhenopacket]
    | list[MatchIndividual]
    | list[MatchBiosample]
    | list[MatchExperiment]
    | list[MatchExperimentResult]
)


class DiscoveryMatches(RootModel):
    root: MatchObject


class DiscoveryPagination(BaseModel):
    model_config = ConfigDict(frozen=True)

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
        EntityCountOrBoolResponse
        | dict[str, EntityCountOrBoolResponse]
        | dict[str, dict[str, EntityCountOrBoolResponse]]
    )
    counts_by_dataset: dict[str, EntityCountOrBoolResponse] = Field(default_factory=dict)


class DiscoveryMatchesPaginatedResponse(BaseModel):
    results_entity: DiscoveryEntity
    results: DiscoveryMatches | dict[str, DiscoveryMatches] | dict[str, dict[str, DiscoveryMatches]]
    pagination: DiscoveryPagination


class DiscoverySearchSectionWithOptions(SearchSection):
    fields: list[DiscoveryFieldAndOptions]


class DiscoverySearchFieldsResponse(BaseModel):
    sections: list[DiscoverySearchSectionWithOptions]


class DiscoveryQueryFilterBase(BaseModel):
    model_config = ConfigDict(frozen=True)

    filter_type: Literal["one_of"]
    negated: bool = False


class DiscoveryQueryFilterOneOf(DiscoveryQueryFilterBase):
    model_config = ConfigDict(frozen=True)

    filter_type: Literal["one_of"]  # really more like "one or more of" - essentially Boolean Or for filter values
    values: list[str] = Field(..., min_length=1)  # must have at least one value specified


class DiscoveryQuery(BaseModel):
    """
    Model for discovery filtering queries. Right now, this is just a dictionary of {discovery field ID: value} extracted
    from query parameters minus project/dataset, but this could be extended in the future.
    """

    # Full text search query + search type. We cap the maximum FTS query length to something reasonable to prevent
    # unlimited-length queries taking up too much memory with any caching we may do. A blank value for `fts` means no
    # FTS query will be executed.
    # See:
    #  - https://docs.djangoproject.com/en/5.2/ref/contrib/postgres/search/#searchquery
    #  - https://www.postgresql.org/docs/18/textsearch-controls.html#TEXTSEARCH-PARSING-QUERIES
    fts: str = Field(default="", title="Full-text search query", max_length=256)
    fts_type: FTSType = Field(default="plain", title="Full-text search query type")

    # Filter query parameters:
    #  - Keys in this dictionary must be the IDs of filters in the corresponding discovery config.
    #  - Values can be either a string, or (with query:data permissions) a more advanced filter structure.
    filters: dict[str, str | DiscoveryQueryFilterOneOf] = Field(default_factory=dict, title="Filters")

    def queried_filter_fields(self) -> list[str]:
        return list(self.filters.keys())

    def n_filter_parameters(self) -> int:
        """
        Returns the number of filter parameters in the query; more than one query to the same field in an OR fashion
        counts as multiple parameters.
        """
        n = 0
        for f in self.filters.values():
            if isinstance(f, DiscoveryQueryFilterOneOf):
                # this branch shouldn't happen in real use since _required_global_permission_level will block OneOf
                # filters with before this function can be called.
                # the subtraction is to prevent us going over our stated filter limit in the censorship rules even with
                # uncensored search (where the maximum number of filters is set to sys.maxsize).
                n = sys.maxsize - len(self.filters)  # cannot be used in a censored discovery context
                break
            elif isinstance(f, str):
                n += 1
            else:  # pragma: no cover
                raise NotImplementedError()
        return n

    def is_empty(self) -> bool:
        """
        Returns whether the query instance is equivalent to an empty query.
        """
        return not self.fts and len(self.filters) == 0

    @staticmethod
    def _filter_query_param(qp: str):
        # - remove project/dataset (i.e., scope) query parameters; otherwise, they get included in the fields and
        #   the response yields an error, as they are (presumably) not queryable fields in the discovery config.
        # - remove "special" query parameters, which start with "_" (for pagination or other non-filter uses)
        return qp and qp not in ("project", "dataset") and qp[0] != "_"

    @property
    def _required_global_permission_level(self) -> DataPermissionsLevel:
        """
        Get the "global" minimum required permission level required to execute this query, irrespective of field-level
        permission information. If full-text search is specified, or we're using an advanced filter (OR/AND/etc...)
        we need query:data permissions.
        """
        if self.fts or any(not isinstance(f, str) for f in self.filters.values()):
            return "data"
        return "bool_"

    def _get_field_set_permissions(
        self,
        discovery_or_scope: DiscoveryConfig | ValidatedDiscoveryScope,
        dt_permissions: DataTypeDiscoveryPermissions,
    ) -> tuple[DataPermissions, FieldDiscoveryPermissions]:
        """
        Returns a tuple of (
            DataPermissions for running the query 'globally', i.e., every field + FTS,
            {field id: DataPermissions},  (for filters)
        ).
        """
        return get_discovery_field_set_permissions(
            discovery_or_scope, self.queried_filter_fields(), bool(self.fts), dt_permissions
        )

    def get_and_validate_permissions(
        self, scope: ValidatedDiscoveryScope, dt_permissions: DataTypeDiscoveryPermissions
    ) -> tuple[DataPermissions, FieldDiscoveryPermissions]:
        """
        Gets overall and field permissions for the query, and validate that we have the sufficient permissions to
        execute the query at the same time
        """

        discovery = scope.discovery
        scope_repr = repr(scope)  # TODO: in the future, scope repr passing to exceptions should be structured data:

        # get permissions needed for our query
        overall_permissions, qf_permissions = self._get_field_set_permissions(discovery, dt_permissions)

        if not overall_permissions.has_permissions_level(self._required_global_permission_level):
            raise ValidationError(f"Insufficient permissions to access discovery ({scope_repr})")

        # TODO: advanced per-field permissions could go here

        if (n_queried := self.n_filter_parameters()) > get_max_query_parameters(discovery, overall_permissions):
            raise ValidationError(f"Wrong number of fields: {n_queried} ({scope_repr})")

        return overall_permissions, qf_permissions

    @classmethod
    def from_drf_request(cls, request: DrfRequest) -> Self:
        """
        Given a Django REST Framework request object from a discovery/discovery-matches request, return a validated
        DiscoveryQuery object.
        """

        if request.method not in ("GET", "POST"):
            raise NotImplementedError("from_drf_request implemented for GET|POST only")

        params: QueryDict | dict = request.query_params if request.method == "GET" else request.data

        # TODO: post JSON - directly validate with Pydantic

        # Process query parameters and check validity
        filters: dict[str, str | DiscoveryQueryFilterOneOf] = {}
        for k in filter(cls._filter_query_param, params.keys()):
            v = params.getlist(k) if isinstance(params, QueryDict) else params.get(k, [])
            if isinstance(v, dict):
                # dictionary (so passed in via JSON)
                filters[k] = DiscoveryQueryFilterOneOf.model_validate(v)
            else:
                if not isinstance(v, list):
                    v = [v]
                match len(v):
                    case 0:
                        pass  # ignore empty lists if these somehow occur
                    case 1:
                        filters[k] = v[0]
                    case _:
                        # TODO: will we be able to support AllOf queries with GET, or just OneOf?
                        filters[k] = DiscoveryQueryFilterOneOf(filter_type="one_of", values=v)

        return cls.model_validate(
            {
                "fts": params.get("_fts", ""),
                "fts_type": params.get("_fts_type") or "plain",
                "filters": filters,
            }
        )


class DiscoveryUIHintsResponse(BaseModel):
    """
    Model representing the UI hints discovery response, which gives any API consumer some hints/suggestions on how to
    make the UI nicer by, e.g., selectively hiding parts.
    """

    model_config = ConfigDict(frozen=True)

    entities_with_data: frozenset[DiscoveryEntity]
    # biosample_location_present: bool  TODO
