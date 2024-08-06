from typing import TypedDict

__all__ = [
    "Bools",
    "DataPermissionsDict",
    "DataTypeDiscoveryPermissions",
    "FieldDiscoveryPermissions",
]


Bools = tuple[bool, ...]


class DataPermissionsDict(TypedDict):
    bool_: bool
    counts: bool
    data: bool


DataTypeDiscoveryPermissions = dict[str, DataPermissionsDict]  # str <=> data type
FieldDiscoveryPermissions = dict[str, DataPermissionsDict]  # str <=> field ID
