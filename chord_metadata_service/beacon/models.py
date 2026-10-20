import json
from typing import Annotated, Any, Literal, Self

from django.core.exceptions import ValidationError
from pydantic import BaseModel, ConfigDict, Field
from rest_framework.request import Request as DrfRequest

from chord_metadata_service.authz.types import DataPermissions, DataPermissionsLevel
from .constants import CountPrecision, Granularity

# Request:  ---------------------------------------------------------------------------------


class BeaconPagination(BaseModel):
    """Pagination parameters for a Beacon request or response."""

    # these map respectively to katsu "page" and "page_size"

    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=0)


class BeaconOntologyFilter(BaseModel):
    id: str
    include_descendant_terms: bool = Field(default=True, alias="includeDescendantTerms")
    similarity: Literal["exact", "high", "medium", "low"] = "exact"
    scope: str | None = None

    model_config = ConfigDict(extra="forbid")


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
    api_version: str = Field(default="v2.2.0", alias="apiVersion")
    requested_schemas: list[dict[str, str]] | None = Field(default=None, alias="requestedSchemas")


class BeaconGenomicVariantRequestParameters(BaseModel):
    assembly_id: str | None = Field(default=None, alias="assemblyId")
    reference_name: str | None = Field(default=None, alias="referenceName")

    # 0-based coordinates
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

class BeaconRequestParameters(BaseModel):
    g_variant: BeaconGenomicVariantRequestParameters | None = None

class BeaconQuery(BaseModel):
    request_parameters: BeaconRequestParameters | None = Field(default=None, alias="requestParameters")

    filters: list[BeaconFilter] | None = None
    include_resultset_responses: Literal["ALL", "HIT", "MISS", "NONE"] = Field(
        default="HIT", alias="includeResultsetResponses"
    )
    pagination: BeaconPagination | None = None
    requested_granularity: Granularity = Field(default=Granularity.BOOLEAN, alias="requestedGranularity")
    test_mode: bool = Field(default=False, alias="testMode")



class BeaconRequest(BaseModel):
    """Beacon v2 request body."""

    # schema_: str | None = Field(default=None, alias="$schema")
    meta: BeaconRequestMeta
    query: BeaconQuery | None = None

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_drf_request(cls, request: DrfRequest) -> Self:
        if request.method == "POST":
            payload = request.data
        elif request.method == "GET":
            params = request.query_params
            meta: dict[str, Any] = {}
            if api_version := params.get("apiVersion"):
                meta["apiVersion"] = api_version
            if requested_schemas := params.get("requestedSchemas"):
                meta["requestedSchemas"] = json.loads(requested_schemas)

            query: dict[str, Any] = {}
            variant_parameters: dict[str, Any] = {}
            for name, field in BeaconGenomicVariantRequestParameters.model_fields.items():
                alias = field.alias or name
                values = params.getlist(alias)
                if values:
                    variant_parameters[alias] = values if alias in ("start", "end") else values[-1]

            if variant_parameters:
                query["requestParameters"] = {"g_variant": variant_parameters}

            for name in ("includeResultsetResponses", "requestedGranularity", "testMode"):
                if name in params:
                    query[name] = params.get(name)

            filter_values = params.getlist("filters")
            if filter_values:
                query["filters"] = [json.loads(value) for value in filter_values]

            if "pagination" in params:
                query["pagination"] = json.loads(params.get("pagination"))
            elif "skip" in params or "limit" in params:
                query["pagination"] = {
                    key: params.get(key) for key in ("skip", "limit") if key in params
                }

            payload = {"meta": meta, "query": query or None}
        else:
            raise NotImplementedError("from_drf_request implemented for GET|POST only")

        return cls.model_validate(payload)

    def get_and_validate_permissions(self, permissions: DataPermissions) -> None:
        granularity = (self.query or BeaconQuery()).requested_granularity

        # map beacon -> katsu levels 
        required_level: DataPermissionsLevel = {
            Granularity.BOOLEAN: "bool_",
            Granularity.COUNT: "counts",
            Granularity.RECORD: "data",
            Granularity.AGGREGATED: "counts",
        }[granularity]

        if not permissions.has_permissions_level(required_level):
            raise ValidationError(f"Insufficient permissions to execute Beacon query at {granularity} granularity")



# Response:  ---------------------------------------------------------------------------------

# probably want serialize_by_alias=true everywhere there's an alias

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

    model_config = ConfigDict(extra="allow")


class BeaconResponseMeta(BaseModel):
    beacon_id: str = Field(alias="beaconId")
    api_version: str = Field(alias="apiVersion")
    returned_schemas: list[dict[str, Any]] = Field(alias="returnedSchemas")
    returned_granularity: Literal["boolean", "count", "record"] = Field(alias="returnedGranularity")
    received_request_summary: BeaconReceivedRequestSummary = Field(alias="receivedRequestSummary")
    test_mode: bool | None = Field(default=None, alias="testMode")

    model_config = ConfigDict(extra="allow")


class BeaconBooleanSummaryResponse(BaseModel):
    exists: bool

    model_config = ConfigDict(extra="allow")


class BeaconCountSummaryResponse(BeaconBooleanSummaryResponse):
    num_total_results: int = Field(alias="numTotalResults", ge=0)
    count_adjusted_to: str | None = Field(default=None, alias="countAdjustedTo")
    count_precision: CountPrecision | None = Field(default=CountPrecision.EXACT, alias="countPrecision")

    model_config = ConfigDict(extra="allow")


class BeaconResultSetSummaryResponse(BeaconBooleanSummaryResponse):
    num_total_results: int | None = Field(default=None, alias="numTotalResults", ge=0)

    model_config = ConfigDict(extra="allow")


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

    model_config = ConfigDict(extra="allow")


class BeaconResultsets(BaseModel):
    result_sets: list[BeaconResultset] = Field(alias="resultSets", min_length=0)

    model_config = ConfigDict(extra="allow")


class BeaconResponseBase(BaseModel):
    meta: BeaconResponseMeta
    info: dict[str, Any] | None = None
    beacon_handovers: list[dict[str, Any]] | None = Field(default=None, alias="beaconHandovers")

    model_config = ConfigDict(extra="allow")


class BeaconBooleanResponse(BeaconResponseBase):
    response_summary: BeaconBooleanSummaryResponse = Field(alias="responseSummary")


class BeaconCountResponse(BeaconResponseBase):
    response_summary: BeaconCountSummaryResponse = Field(alias="responseSummary")


class BeaconResultsetsResponse(BeaconResponseBase):
    response_summary: BeaconResultSetSummaryResponse = Field(alias="responseSummary")
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
    "BeaconBooleanSummaryResponse",
    "BeaconCountResponse",
    "BeaconCountSummaryResponse",
    "BeaconReceivedRequestSummary",
    "BeaconResponseBase",
    "BeaconResponseMeta",
    "BeaconResultset",
    "BeaconResultsets",
    "BeaconResultsetsResponse",
    "BeaconResultSetSummaryResponse",
]

# add aggregation response
# ideally the front end will render charts from beacon-format aggregation response
# possibly may need an interim response that is closer to current katsu response
