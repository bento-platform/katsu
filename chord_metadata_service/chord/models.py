import collections
import uuid
from bento_lib.discovery import DiscoveryConfig
from bento_lib.provenance.dataset import ProjectScopedDatasetModel
from chord_metadata_service.chord.dataset_schema import KatsuDatasetModel
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.models import Biosample, Phenopacket
from chord_metadata_service.resources.models import Resource
from chord_metadata_service.restapi.schema_ref import SchemaRefs
from chord_metadata_service.restapi.validators import JsonSchemaValidator
from chord_metadata_service.restapi.models import BaseTimeStamp, SchemaType
from chord_metadata_service.common.base_pydantic_jsonb import AbstractPydanticJSONBModel


__all__ = ["Project", "Dataset", "ProjectJsonSchema", "DatasetV2", "DatasetV2Translation"]


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
        blank=True, null=True, help_text="Discovery configuration",
        validators=[JsonSchemaValidator(schema_ref=SchemaRefs.DISCOVERY_SCHEMA)]
    )


class Project(BaseProjectOrDataset):
    """
    Class to represent a Project, which contains multiple
    Datasets which are each a group of Phenopackets.
    """

    def __str__(self):
        return f"{self.title} (ID: {self.identifier})"


class Dataset(BaseProjectOrDataset):
    """
    Class to represent a Dataset, which contains multiple Phenopackets.
    """

    contact_info = models.TextField(blank=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,  # Delete dataset upon project deletion
        related_name="datasets"
    )

    data_use = models.JSONField()
    linked_field_sets = models.JSONField(blank=True, default=list,
                                         help_text="Data type fields which are linked together.")

    conditions_of_access = models.TextField(blank=True, default="",
                                            help_text="The data access requests link(s), "
                                            "as defined in https://schema.org/conditionsOfAccess")

    additional_resources = models.ManyToManyField(Resource, blank=True, help_text="Any resource objects linked to this "
                                                                                  "dataset that aren't specified by a "
                                                                                  "phenopacket in the dataset.")

    @property
    def resources(self):
        # Union of phenopacket resources and any additional resources for other table types
        return Resource.objects.filter(id__in={
            *(r.id for r in self.additional_resources.all()),
            *(
                # r.id
                # for p in Phenopacket.objects.filter(
                #     table_id__in={t.table_id for t in self.table_ownership.all()}
                # ).prefetch_related("meta_data", "meta_data__resources")
                # for r in p.meta_data.resources.all()
                r.id
                for p in Phenopacket.objects.filter(
                    dataset_id=self.identifier
                ).prefetch_related("meta_data", "meta_data__resources")
                for r in p.meta_data.resources.all()
            ),
        })

    # --------------------------- DATS model fields ---------------------------

    alternate_identifiers = models.JSONField(blank=True, default=list,
                                             help_text="Alternate identifiers for the dataset.")
    related_identifiers = models.JSONField(blank=True, default=list, help_text="Related identifiers for the dataset.")
    dates = models.JSONField(blank=True, default=list,
                             help_text="Relevant dates for the datasets, a date must be added, e.g. "
                             "creation date or last modification date should be added.")
    # TODO: Can this be auto-synthesized? (Specified in settings)
    stored_in = models.JSONField(blank=True, null=True, help_text="The data repository hosting the dataset.")
    spatial_coverage = models.JSONField(blank=True, default=list,
                                        help_text="The geographical extension and span covered "
                                        "by the dataset and its measured dimensions/variables.")
    types = models.JSONField(blank=True, default=list,
                             help_text="A term, ideally from a controlled terminology, identifying "
                             "the dataset type or nature of the data, placing it in a typology.")
    # TODO: Can this be derived from / combined with DUO stuff?
    availability = models.CharField(max_length=200, blank=True,
                                    help_text="A qualifier indicating the different types of availability for a "
                                              "dataset (available, unavailable, embargoed, available with restriction, "
                                              "information not available).")
    refinement = models.CharField(max_length=200, blank=True,
                                  help_text="A qualifier to describe the level of data processing of the dataset and "
                                            "its distributions.")
    aggregation = models.CharField(max_length=200, blank=True,
                                   help_text="A qualifier indicating if the entity represents an 'instance of dataset' "
                                             "or a 'collection of datasets'.")
    privacy = models.CharField(max_length=200, blank=True,
                               help_text="A qualifier to describe the data protection applied to the dataset. This is "
                                         "relevant for clinical data.")
    distributions = models.JSONField(blank=True, default=list,
                                     help_text="The distribution(s) by which datasets are made "
                                     "available (for example: mySQL dump).")
    dimensions = models.JSONField(blank=True, default=list,
                                  help_text="The different dimensions (granular components) making up a dataset.")
    primary_publications = models.JSONField(blank=True, default=list,
                                            help_text="The primary publication(s) associated with "
                                            "the dataset, usually describing how the dataset was produced.")
    citations = models.JSONField(blank=True, default=list, help_text="The publication(s) that cite this dataset.")
    citation_count = models.IntegerField(blank=True, null=True,
                                         help_text="The number of publications that cite this dataset (enumerated in "
                                                   "the citations property).")
    produced_by = models.JSONField(blank=True, null=True,
                                   help_text="A study process which generated a given dataset, if any.")
    creators = models.JSONField(blank=True, default=list,
                                help_text="The person(s) or organization(s) which contributed to "
                                "the creation of the dataset.")
    # TODO: How to reconcile this and data_use?
    licenses = models.JSONField(blank=True, default=list, help_text="The terms of use of the dataset.")
    # is_about this field will be calculated based on sample field
    # in tableOwnership
    has_part = models.ManyToManyField("self", blank=True, help_text="A Dataset that is a subset of this Dataset; "
                                                                    "Datasets declaring the 'hasPart' relationship are "
                                                                    "considered a collection of Datasets, the "
                                                                    "aggregation criteria could be included in "
                                                                    "the 'description' field.")
    acknowledges = models.JSONField(blank=True, default=list,
                                    help_text="The grant(s) which funded the work reported by the dataset.")
    keywords = models.JSONField(blank=True, default=list,
                                help_text="Tags associated with the dataset, which will help in its discovery.")
    version = models.CharField(max_length=200, blank=True, default=version_default,
                               help_text="A release point for the dataset when applicable.")
    dats_file = models.JSONField(blank=True, null=True,
                                 help_text="Content of a valid DATS file, in JSON format, "
                                           "that specifies the dataset provenance.")

    # -------------------------------------------------------------------------

    extra_properties = models.JSONField(blank=True, null=True,
                                        help_text="Extra properties that do not fit in the previous "
                                        "specified attributes.")

    def clean(self):
        # Check that all namespace prefices are unique within a dataset
        c = collections.Counter(r.namespace_prefix for r in self.resources)
        mc = (*c.most_common(1), (None, 0))[0]
        if mc[1] > 1:
            raise ValidationError(f"Dataset {self.identifier} cannot have ambiguous resource namespace prefix {mc[0]}")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} (ID: {self.identifier})"


class DatasetV2(AbstractPydanticJSONBModel):

    # --- AbstractPydanticJSONBModel configuration ---
    COLUMN_FIELDS = {
        'identifier',
        'project',
        'title',
        'release_date',
        'last_modified',
        'discovery',
    }
    JSONB_FIELD = 'data'
    SCHEMA_CLASS = KatsuDatasetModel

    # --- Django fields ---
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,  # Delete dataset upon project deletion
        related_name="dv2"
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
        return Resource.objects.filter(id__in={
            *(r.id for r in self.additional_resources.all()),
            *(
                r.id
                for p in Phenopacket.objects.filter(
                    dataset_id=self.identifier
                ).prefetch_related("meta_data", "meta_data__resources")
                for r in p.meta_data.resources.all()
            ),
        })

    def __str__(self) -> str:
        return f"{self.identifier}: {self.title}"


class DatasetV2Translation(AbstractPydanticJSONBModel):
    """Stores a translated Pydantic payload for a DatasetV2 in a non-default language."""

    # --- Mixin configuration ---
    # 'dataset' is NOT in COLUMN_FIELDS — it has no matching field in ProjectScopedDatasetModel.
    # Callers pass dataset_id=<pk> as extra_column_kwargs to from_schema().
    COLUMN_FIELDS = {'language'}
    JSONB_FIELD = 'data'
    SCHEMA_CLASS = ProjectScopedDatasetModel

    # --- Django fields ---
    dataset = models.ForeignKey(
        DatasetV2,
        on_delete=models.CASCADE,
        related_name='translations',
    )
    language = models.CharField(max_length=8, db_index=True)
    data = models.JSONField(help_text="Full ProjectScopedDatasetModel payload for this language.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('dataset', 'language')]

    def __str__(self) -> str:
        return f"{self.dataset_id}: {self.language}"


class ProjectJsonSchema(models.Model):
    id = models.CharField(primary_key=True, max_length=200, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_schemas")
    required = models.BooleanField(default=False,
                                   help_text="Determines if the extra_properties field is required or not.")
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
            target_count = Phenopacket.objects.filter(
                dataset__project_id=self.project_id
            ).count()
        elif self.schema_type == SchemaType.INDIVIDUAL:
            target_count = Individual.objects.filter(
                phenopackets__dataset__project_id=self.project_id
            ).count()
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
        constraints = [
            models.UniqueConstraint(fields=["project", "schema_type"], name="unique_project_schema")
        ]
