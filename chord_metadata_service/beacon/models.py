from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field


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


BeaconFilter = Annotated[
	BeaconOntologyFilter | BeaconAlphanumericFilter | BeaconCustomFilter,
	Field(union_mode="left_to_right"),
]


class BeaconRequestMeta(BaseModel):
	schema_: str | None = Field(default=None, alias="$schema")
	api_version: str = Field(alias="apiVersion")
	requested_schemas: list[dict[str, str]] | None = Field(default=None, alias="requestedSchemas")

	model_config = ConfigDict(populate_by_name=True)


class BeaconQuery(BaseModel):
	request_parameters: dict[str, dict[str, object]] | None = Field(default=None, alias="requestParameters")
	filters: list[BeaconFilter] | None = None
	include_resultset_responses: Literal["ALL", "HIT", "MISS", "NONE"] = Field(
		default="HIT", alias="includeResultsetResponses"
	)
	pagination: BeaconPagination | None = None
	requested_granularity: Literal["boolean", "count", "record"] = Field(default="boolean", alias="requestedGranularity")
	test_mode: bool = Field(default=False, alias="testMode")

	model_config = ConfigDict(populate_by_name=True)


class BeaconRequest(BaseModel):
	"""Beacon v2 request body."""

	schema_: str | None = Field(default=None, alias="$schema")
	meta: BeaconRequestMeta
	query: BeaconQuery | None = None

	model_config = ConfigDict(populate_by_name=True)


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
	"BeaconFilter",
	"BeaconOntologyFilter",
	"BeaconPagination",
	"BeaconQuery",
	"BeaconRequest",
	"BeaconRequestMeta",
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
