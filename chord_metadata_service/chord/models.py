import uuid
from django.utils import timezone
from bento_lib.discovery import DiscoveryConfig
from bento_lib.provenance.dataset import ProjectScopedDatasetModel
from chord_metadata_service.chord.dataset_schema import KatsuDatasetModel
from django.core.exceptions import ValidationError
from django.db import models
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.models import Biosample, Phenopacket
from chord_metadata_service.resources.models import Resource
from chord_metadata_service.restapi.schema_ref import SchemaRefs
from chord_metadata_service.restapi.validators import JsonSchemaValidator
from chord_metadata_service.restapi.models import BaseTimeStamp, SchemaType
from chord_metadata_service.common.base_pydantic_jsonb import AbstractPydanticJSONBModel


__all__ = ["Project", "ProjectJsonSchema", "Dataset", "DatasetTranslation"]


# Referenced by chord/migrations/0001_v1_0_0.py — must remain for migration import compatibility.
def version_default():
    return f"version_{timezone.now()}"


#############################################################
#                                                           #
#                   Project Management                      #
#                                                           #
#############################################################


class DiscoveryJSONField(models.JSONField):
    """
    Custom JSON field which uses a DiscoveryConfig object as values' Python representation, and JSON as the stored
    representation.
    """

    def from_db_value(self, value, expression, connection):
        """
        Returns a DiscoveryConfig Pydantic model instance, or None if no discovery configuration has been set.
        """
        if value is None:
            return value
        return DiscoveryConfig.model_validate_json(value)

    def get_prep_value(self, value):
        return super().get_prep_value(value.model_dump(mode="json") if isinstance(value, DiscoveryConfig) else value)


class BaseProjectOrDataset(BaseTimeStamp):
    """
    Abstract base Django model representing the common underlying shared fields/methods for both projects and datasets,
    including common metadata (ID, title, description), timestamps, and discovery configuration storage/access.
    """

    class Meta:
        abstract = True

    identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    discovery = DiscoveryJSONField(
        blank=True,
        null=True,
        help_text="Discovery configuration",
        validators=[JsonSchemaValidator(schema_ref=SchemaRefs.DISCOVERY_SCHEMA)],
    )


class Project(BaseProjectOrDataset):
    """
    Class to represent a Project, which contains multiple
    Datasets which are each a group of Phenopackets.
    """

    def __str__(self):
        return f"{self.title} (ID: {self.identifier})"


class Dataset(AbstractPydanticJSONBModel):
    # --- AbstractPydanticJSONBModel configuration ---
    COLUMN_FIELDS = {
        "identifier",
        "project",
        "title",
        "release_date",
        "last_modified",
        "discovery",
    }
    JSONB_FIELD = "data"
    SCHEMA_CLASS = KatsuDatasetModel

    # --- Django fields ---
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,  # Delete dataset upon project deletion
        related_name="datasets",
    )

    identifier = models.CharField(
        primary_key=True,
        max_length=128,
        default=uuid.uuid4,
        blank=True,
        help_text="If from PCGL, inherit. Otherwise created in Katsu.",
    )

    title = models.CharField(max_length=512)

    release_date = models.DateField(db_index=True, null=True, blank=True)
    last_modified = models.DateField(db_index=True, null=True, blank=True)
    discovery = DiscoveryJSONField(blank=True, null=True, help_text="Dataset-level discovery configuration.")

    # Store the whole validated payload (English default, validated by Pydantic before saving)
    data = models.JSONField(help_text="Full DatasetModel payload validated by Pydantic before saving.")

    additional_resources = models.ManyToManyField(
        Resource,
        blank=True,
        help_text="Resource objects linked to this dataset that aren't specified by a phenopacket.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def resources(self):
        return Resource.objects.filter(
            id__in={
                *(r.id for r in self.additional_resources.all()),
                *(
                    r.id
                    for p in Phenopacket.objects.filter(dataset_id=self.identifier).prefetch_related(
                        "meta_data", "meta_data__resources"
                    )
                    for r in p.meta_data.resources.all()
                ),
            }
        )

    def __str__(self) -> str:
        return f"{self.identifier}: {self.title}"


class DatasetTranslation(AbstractPydanticJSONBModel):
    """Stores a translated Pydantic payload for a Dataset in a non-default language."""

    # --- Mixin configuration ---
    # 'dataset' is NOT in COLUMN_FIELDS — it has no matching field in ProjectScopedDatasetModel.
    # Callers pass dataset_id=<pk> as extra_column_kwargs to from_schema().
    COLUMN_FIELDS = {"language"}
    JSONB_FIELD = "data"
    SCHEMA_CLASS = ProjectScopedDatasetModel

    # --- Django fields ---
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name="translations",
    )
    language = models.CharField(max_length=8, db_index=True)
    data = models.JSONField(help_text="Full ProjectScopedDatasetModel payload for this language.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("dataset", "language")]

    def __str__(self) -> str:
        return f"{self.dataset_id}: {self.language}"


class ProjectJsonSchema(models.Model):
    id = models.CharField(primary_key=True, max_length=200, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_schemas")
    required = models.BooleanField(
        default=False, help_text="Determines if the extra_properties field is required or not."
    )
    json_schema = models.JSONField()
    schema_type = models.CharField(max_length=200, choices=SchemaType.choices)

    def clean(self):
        """
        Creation of ProjectJsonSchema is prohibited if the target project already
        contains data matching the schema_type
        """

        super().clean()

        target_count = 0
        if self.schema_type == SchemaType.PHENOPACKET:
            target_count = Phenopacket.objects.filter(dataset__project_id=self.project_id).count()
        elif self.schema_type == SchemaType.INDIVIDUAL:
            target_count = Individual.objects.filter(phenopackets__dataset__project_id=self.project_id).count()
        elif self.schema_type == SchemaType.BIOSAMPLE:
            target_count = Biosample.objects.filter(
                individual__phenopackets__dataset__project_id=self.project_id
            ).count()

        if target_count > 0:
            raise ValidationError(f"Project {self.project_id} already contains data for {self.schema_type}")

    def save(self, *args, **kwargs):
        # Override in order to call self.clean to validate data
        self.clean()
        return super().save(*args, **kwargs)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["project", "schema_type"], name="unique_project_schema")]
