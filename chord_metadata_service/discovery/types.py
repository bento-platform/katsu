from typing import Any, Literal, TypedDict

__all__ = [
    "BinWithValue",
    "OverviewSectionChart",
    "OverviewSection",
    "DiscoveryFieldProps",
    "DiscoveryRules",
    "DiscoveryConfig",
    "EmptyConfig",
    "DiscoveryOrEmptyConfig",
    "OptionalDiscoveryOrEmptyConfig",
    "ModelScopeFilters",
]


class BinWithValue(TypedDict):
    label: str
    value: int


class OverviewSectionChart(TypedDict):
    field: str
    chart_type: str
    # ...


class OverviewSection(TypedDict):
    section_title: str
    charts: list[OverviewSectionChart]


class SearchSection(TypedDict):
    section_title: str
    fields: list[str]


class DiscoveryFieldProps(TypedDict):
    mapping: str
    title: str
    description: str
    datatype: Literal["number", "string", "date"]
    config: dict[str, Any]


class DiscoveryRules(TypedDict):
    max_query_parameters: int
    count_threshold: int


class DiscoveryConfig(TypedDict):
    overview: list[OverviewSection]
    search: list[SearchSection]
    fields: dict[str, DiscoveryFieldProps]
    rules: DiscoveryRules


class EmptyConfig(TypedDict):
    pass


# TODO: py3.12: type keyword
DiscoveryOrEmptyConfig = DiscoveryConfig | EmptyConfig
OptionalDiscoveryOrEmptyConfig = DiscoveryOrEmptyConfig | None


class ScopeLevelFilters(TypedDict):
    # If filter is a tuple, the field contains multiple filters that are ORed together. This is useful for, e.g., the
    # Resource model, where there are multiple possible paths one can take from the object to the parent dataset(s).
    filter: str | tuple[str, ...]
    prefetch_related: tuple[str, ...]


class ModelScopeFilters(TypedDict):
    project: ScopeLevelFilters
    dataset: ScopeLevelFilters
