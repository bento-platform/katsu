from typing import TypedDict

__all__ = [
    "DataPermissionsDict",
    "DataTypeDiscoveryPermissions",
    "FieldDiscoveryPermissions",
]


class DataPermissionsDict(TypedDict):
    bool_: bool
    counts: bool
    data: bool


DataTypeDiscoveryPermissions = dict[str, DataPermissionsDict]  # str <=> data type
FieldDiscoveryPermissions = dict[str, DataPermissionsDict]  # str <=> field ID
