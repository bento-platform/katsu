from bento_lib.discovery import FieldDefinition
from pydantic import BaseModel, RootModel


__all__ = [
    "BinWithValue",
    "DiscoveryFieldResponse",
    "DiscoveryFieldResponses",
]


class BinWithValue(BaseModel):
    label: str
    value: int


class DiscoveryFieldResponse(BaseModel):
    id: str
    definition: FieldDefinition
    data: list[BinWithValue]


class DiscoveryFieldResponses(RootModel):
    root: dict[str, DiscoveryFieldResponse]
