from typing import Literal, TypedDict

__all__ = [
    "DiscoveryRules",
    "CompleteDiscoveryConfig",
    "DiscoveryConfig",
    "BinWithValue",
]


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
    config: dict[str, str | int]


class DiscoveryRules(TypedDict):
    max_query_parameters: int
    count_threshold: int


class CompleteDiscoveryConfig(TypedDict):
    overview: list[OverviewSection]
    search: list[SearchSection]
    fields: dict[str, DiscoveryFieldProps]
    rules: DiscoveryRules


DiscoveryConfig = CompleteDiscoveryConfig | None


class BinWithValue(TypedDict):
    label: str
    value: int
