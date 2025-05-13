from dataclasses import dataclass
from typing import TypeAlias

__all__ = [
    "DataPermissions",
    "DataTypeDiscoveryPermissions",
    "FieldDiscoveryPermissions",
]


@dataclass
class DataPermissions:
    bool_: bool
    counts: bool
    data: bool

    def any_permissions(self):
        return self.bool_ or self.counts or self.data


DataTypeDiscoveryPermissions: TypeAlias = dict[str, DataPermissions]  # str <=> data type
FieldDiscoveryPermissions: TypeAlias = dict[str, DataPermissions]  # str <=> field ID
