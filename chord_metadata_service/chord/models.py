import collections
import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.models import Biosample, Phenopacket
from chord_metadata_service.resources.models import Resource
from ..restapi.models import SchemaType


__all__ = ["Project", "Dataset", "ProjectJsonSchema"]


def version_default():
    return f"version_{timezone.now()}"


#############################################################
#                                                           #
#                   Project Management                      #
#                                                           #
#############################################################

class Project(models.Model):
    """
    Class to represent a Project, which contains multiple
    Datasets which are each a group of Phenopackets.
    """

    identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (ID: {self.identifier})"


class Dataset(models.Model):
    """
    Class to represent a Dataset, which contains multiple Phenopackets.
    """

    identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    contact_info = models.TextField(blank=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,  # Delete dataset upon project deletion
        related_name="datasets"
    )

    data_use = models.JSONField()
    linked_field_sets = models.JSONField(blank=True, default=list,
                                         help_text="Data type fields which are linked together.")

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
    dats_file = models.JSONField(blank=True, default=dict,
                                 help_text="Content of a valid DATS file, in JSON format, "
                                           "that specifies the dataset provenance.")
    extra_properties = models.JSONField(blank=True, null=True,
                                        help_text="Extra properties that do not fit in the previous "
                                        "specified attributes.")

    # -------------------------------------------------------------------------

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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
