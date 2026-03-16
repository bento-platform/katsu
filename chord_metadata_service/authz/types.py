from dataclasses import dataclass
from typing import Literal

from chord_metadata_service.chord.data_types import KatsuDataType

__all__ = [
    "DataPermissionsLevel",
    "DataPermissions",
    "DataTypeDiscoveryPermissions",
    "FieldDiscoveryPermissions",
]


type DataPermissionsLevel = Literal["bool_", "counts", "data"]


@dataclass(frozen=True)
class DataPermissions:
    bool_: bool
    counts: bool
    data: bool

    def any_permissions(self):
        return self.bool_ or self.counts or self.data

    def has_permissions_level(self, level: DataPermissionsLevel) -> bool:
        return getattr(self, level)


type DataTypeDiscoveryPermissions = dict[KatsuDataType, DataPermissions]
type FieldDiscoveryPermissions = dict[str, DataPermissions]  # str <=> field ID
