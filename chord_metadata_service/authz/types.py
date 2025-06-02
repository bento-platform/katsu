from dataclasses import dataclass
from typing import TypeAlias

from chord_metadata_service.chord.data_types import KatsuDataType

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


DataTypeDiscoveryPermissions: TypeAlias = dict[KatsuDataType, DataPermissions]
FieldDiscoveryPermissions: TypeAlias = dict[str, DataPermissions]  # str <=> field ID
