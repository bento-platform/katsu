from bento_lib.discovery import DiscoveryConfig, FieldDefinition

__all__ = ["FieldDefinitionProvider"]


class FieldDefinitionProvider:
    """
    Container class which encapsulates FieldDefinition access when we have a mix of discovery-config-defined fields and
    possible ad-hoc definitions which can amend/overwrite the config. Access is done via square brackets:
    fdp["field"] --> FieldDefinition
    """
    def __init__(self, discovery: DiscoveryConfig, additional_definitions: dict[str, FieldDefinition] | None = None):
        self._discovery = discovery
        self._defs: dict[str, FieldDefinition] = additional_definitions or {}

    def __getitem__(self, item: str) -> FieldDefinition:
        """
        Returns a field definition for the item, or raises a KeyError if the field is not present.
        """
        return self._defs.get(item, self._discovery.fields[item])

    @property
    def searchable_fields(self) -> frozenset[str]:
        """
        Returns a frozenset of field IDs that can be searched on (filtered by).
        """
        return frozenset(self._discovery.get_searchable_field_ids()).union(frozenset(self._defs.keys()))
