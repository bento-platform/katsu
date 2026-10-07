from enum import Enum


class CountPrecision(str, Enum):
    EXACT = "exact"
    IMPRECISE = "imprecise"
    ROUNDED = "rounded"


class Granularity(str, Enum):
    BOOLEAN = "boolean"
    COUNT = "count"
    RECORD = "record"
    AGGREGATED = "aggregated"
