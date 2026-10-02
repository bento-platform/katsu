from enum import Enum

class Granularity(str, Enum):
    GRANULARITY_BOOLEAN = "boolean"
    GRANULARITY_COUNT = "count"
    GRANULARITY_RECORD = "record"
    GRANULARITY_AGGREGATED = "aggregated"
