__all__ = ["DATASET_ID_REGEX", "LinkedFieldSet", "KatsuDatasetModel"]

from pydantic import BaseModel, Field
from bento_lib.provenance.dataset import ProjectScopedDatasetModel

# Dataset IDs may be UUIDs (created in katsu) or external IDs such as PCGL study IDs (e.g. STUDY0002).
# Restricted to a safe charset so IDs can be used in URLs and logged; length (1-128) matches Dataset.identifier.
# Letters, digits, "_" and "-" only, starting with a letter or digit. In particular:
#  - no ":", which separates the IDs in "<project id>:<dataset id>" workflow inputs (see chord/workflows/wdls);
#  - no ".", which separates the format suffix in API routes (/api/datasets/<id>.json).
DATASET_ID_REGEX = r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}"


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

    identifier: str = Field(min_length=1, max_length=128, pattern=rf"^{DATASET_ID_REGEX}$")

    linked_field_sets: list[LinkedFieldSet] = Field(
        default_factory=list,
        description="Data type fields which are linked together for cross-table joins.",
    )
