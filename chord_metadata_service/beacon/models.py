from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .constants import Granularity

# Request:  ---------------------------------------------------------------------------------


class BeaconPagination(BaseModel):
    """Pagination parameters for a Beacon request or response."""

    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=0)


class BeaconOntologyFilter(BaseModel):
    id: str
    include_descendant_terms: bool = Field(default=True, alias="includeDescendantTerms")
    similarity: Literal["exact", "high", "medium", "low"] = "exact"
    scope: str | None = None

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class BeaconAlphanumericFilter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    operator: Literal["=", "<", ">", "!", ">=", "<="] = "="
    value: str
    scope: str | None = None


class BeaconCustomFilter(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    scope: str | None = None


# Beacon spec is not robust enough to distinguish these correctly in all cases
# see https://github.com/ga4gh-beacon/beacon-v2/issues/56
BeaconFilter = Annotated[
    BeaconOntologyFilter | BeaconAlphanumericFilter | BeaconCustomFilter,
    Field(union_mode="left_to_right"),
]


class BeaconRequestMeta(BaseModel):
    # schema_: str | None = Field(default=None, alias="$schema")
    api_version: str = Field(alias="apiVersion")
    requested_schemas: list[dict[str, str]] | None = Field(default=None, alias="requestedSchemas")

    model_config = ConfigDict(populate_by_name=True)


class BeaconGenomicVariantRequestParameters(BaseModel):
    assembly_id: str | None = Field(default=None, alias="assemblyId")
    reference_name: str | None = Field(default=None, alias="referenceName")
    start: list[Annotated[int, Field(ge=0)]] | None = Field(default=None, min_length=1, max_length=2)
    end: list[Annotated[int, Field(ge=1)]] | None = Field(default=None, min_length=1, max_length=2)

    # beacon schema has contradictory properties for "reference_bases" and "alternate_bases":
    # they have description: "Accepted values: `[ACGTN]*" but also a pattern regex "^([ACGTUNRYSWKMBDHV\-\.]*)$"
    # for now accept the broader options and leave it to variants service to accept or reject
    reference_bases: str | None = Field(default=None, alias="referenceBases", pattern=r"^([ACGTUNRYSWKMBDHV\-\.]*)$")
    alternate_bases: str | None = Field(default=None, alias="alternateBases", pattern=r"^([ACGTUNRYSWKMBDHV\-\.]*)$")
    variant_type: str | None = Field(default=None, alias="variantType")
    variant_min_length: int | None = Field(default=None, alias="variantMinLength", ge=0)
    variant_max_length: int | None = Field(default=None, alias="variantMaxLength", ge=1)
    mate_name: str | None = Field(default=None, alias="mateName")
    gene_id: str | None = Field(default=None, alias="geneId")
    aminoacid_change: str | None = Field(default=None, alias="aminoacidChange")
    genomic_allele_short_form: str | None = Field(default=None, alias="genomicAlleleShortForm")

    model_config = ConfigDict(populate_by_name=True)


class BeaconRequestParameters(BaseModel):
    g_variant: BeaconGenomicVariantRequestParameters | None = None

    model_config = ConfigDict(populate_by_name=True)


class BeaconQuery(BaseModel):
    request_parameters: BeaconRequestParameters | None = Field(default=None, alias="requestParameters")

    filters: list[BeaconFilter] | None = None
    include_resultset_responses: Literal["ALL", "HIT", "MISS", "NONE"] = Field(
        default="HIT", alias="includeResultsetResponses"
    )
    pagination: BeaconPagination | None = None
    requested_granularity: Granularity = Field(default=Granularity.GRANULARITY_BOOLEAN, alias="requestedGranularity")
    test_mode: bool = Field(default=False, alias="testMode")

    model_config = ConfigDict(populate_by_name=True)


class BeaconRequest(BaseModel):
    """Beacon v2 request body."""

    # schema_: str | None = Field(default=None, alias="$schema")
    meta: BeaconRequestMeta
    query: BeaconQuery | None = None

    model_config = ConfigDict(populate_by_name=True)


# Response:  ---------------------------------------------------------------------------------


class BeaconReceivedRequestSummary(BaseModel):
    api_version: str = Field(alias="apiVersion")
    requested_schemas: list[dict[str, Any]] = Field(alias="requestedSchemas")
    filters: list[dict[str, Any]] | None = None
    request_parameters: dict[str, Any] | None = Field(default=None, alias="requestParameters")
    include_resultset_responses: Literal["ALL", "HIT", "MISS", "NONE"] | None = Field(
        default=None, alias="includeResultsetResponses"
    )
    pagination: BeaconPagination
    requested_granularity: Literal["boolean", "count", "record"] = Field(alias="requestedGranularity")
    test_mode: bool | None = Field(default=None, alias="testMode")

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class BeaconResponseMeta(BaseModel):
    beacon_id: str = Field(alias="beaconId")
    api_version: str = Field(alias="apiVersion")
    returned_schemas: list[dict[str, Any]] = Field(alias="returnedSchemas")
    returned_granularity: Literal["boolean", "count", "record"] = Field(alias="returnedGranularity")
    received_request_summary: BeaconReceivedRequestSummary = Field(alias="receivedRequestSummary")
    test_mode: bool | None = Field(default=None, alias="testMode")

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class BeaconBooleanResponseSection(BaseModel):
    exists: bool

    model_config = ConfigDict(extra="allow")


class BeaconCountResponseSection(BeaconBooleanResponseSection):
    num_total_results: int = Field(alias="numTotalResults", ge=0)
    count_adjusted_to: str | None = Field(default=None, alias="countAdjustedTo")
    count_precision: str | None = Field(default=None, alias="countPrecision")

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class BeaconSummaryResponseSection(BeaconBooleanResponseSection):
    num_total_results: int | None = Field(default=None, alias="numTotalResults", ge=0)

    model_config = ConfigDict(extra="allow", populate_by_name=True)


# any response granularity can return ResultsetResponse, although this is not at all clear from the schema
# see https://github.com/ga4gh-beacon/beacon-v2/pull/231
class BeaconResultset(BaseModel):
    id: str
    set_type: str = Field(alias="setType")
    exists: bool
    results_count: int | None = Field(default=None, alias="resultsCount", ge=0)
    count_adjusted_to: str | None = Field(default=None, alias="countAdjustedTo")
    count_precision: str | None = Field(default=None, alias="countPrecision")
    results_handovers: list[dict[str, Any]] | None = Field(default=None, alias="resultsHandovers")
    info: dict[str, Any] | None = None
    results: list[dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class BeaconResultsets(BaseModel):
    result_sets: list[BeaconResultset] = Field(alias="resultSets", min_length=0)

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class BeaconResponseBase(BaseModel):
    meta: BeaconResponseMeta
    info: dict[str, Any] | None = None
    beacon_handovers: list[dict[str, Any]] | None = Field(default=None, alias="beaconHandovers")

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class BeaconBooleanResponse(BeaconResponseBase):
    response_summary: BeaconBooleanResponseSection = Field(alias="responseSummary")


class BeaconCountResponse(BeaconResponseBase):
    response_summary: BeaconCountResponseSection = Field(alias="responseSummary")


class BeaconResultsetsResponse(BeaconResponseBase):
    response_summary: BeaconSummaryResponseSection = Field(alias="responseSummary")
    response: BeaconResultsets


__all__ = [
    "BeaconAlphanumericFilter",
    "BeaconCustomFilter",
    "BeaconGenomicVariantRequestParameters",
    "BeaconFilter",
    "BeaconOntologyFilter",
    "BeaconPagination",
    "BeaconQuery",
    "BeaconRequest",
    "BeaconRequestMeta",
    "BeaconRequestParameters",
    "BeaconBooleanResponse",
    "BeaconBooleanResponseSection",
    "BeaconCountResponse",
    "BeaconCountResponseSection",
    "BeaconReceivedRequestSummary",
    "BeaconResponseBase",
    "BeaconResponseMeta",
    "BeaconResultset",
    "BeaconResultsets",
    "BeaconResultsetsResponse",
    "BeaconSummaryResponseSection",
]

# add aggregation response
# ideally the front end will render charts from beacon-format aggregation response
# possibly may need an interim response that is closer to current katsu response
