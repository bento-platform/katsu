from bento_lib.discovery import DiscoveryConfig, FieldDefinition

__all__ = ["FieldDefinitionProvider"]


class FieldDefinitionProvider:
    def __init__(self, discovery: DiscoveryConfig, additional_definitions: dict[str, FieldDefinition] | None = None):
        self._discovery = discovery
        self._defs: dict[str, FieldDefinition] = additional_definitions or {}

    def __getitem__(self, item: str) -> FieldDefinition:
        return self._defs.get(item, self._discovery.fields[item])

    @property
    def searchable_fields(self) -> frozenset[str]:
        return frozenset(self._discovery.get_searchable_field_ids()).union(frozenset(self._defs.keys()))
