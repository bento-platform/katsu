__all__ = ["LinkedFieldSet", "KatsuDatasetModel"]

from pydantic import BaseModel, Field
from bento_lib.discovery import DiscoveryConfig
from bento_lib.provenance.dataset import ProjectScopedDatasetModel


class LinkedFieldSet(BaseModel):
    """
    Declares which fields across different data types share the same subject identity,
    enabling pre-defined cross-table joins within a dataset.

    Example:
        {
            "name": "subject IDs",
            "fields": {
                "phenopacket": ["subject", "id"],
                "biosample": ["individual_id"]
            }
        }
    """

    name: str = Field(min_length=3)
    fields: dict[str, list[str]] = Field(
        min_length=2,
        description="Map of data type name to field path (array of path segments).",
    )


class KatsuDatasetModel(ProjectScopedDatasetModel):
    """ProjectScopedDatasetModel extended with Katsu-internal fields."""

    linked_field_sets: list[LinkedFieldSet] = Field(
        default_factory=list,
        description="Data type fields which are linked together for cross-table joins.",
    )
    discovery: DiscoveryConfig | None = Field(
        default=None,
        description="Dataset-level discovery configuration; falls back to project config if not set.",
    )
