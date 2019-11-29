import uuid

from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models


__all__ = ["Project", "Dataset", "TableOwnership"]


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
    data_use = JSONField()

    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (ID: {self.identifier})"


class Dataset(models.Model):
    """
    Class to represent a Dataset, which contains multiple Phenopackets.
    """

    identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,  # Delete dataset upon project deletion
        related_name="datasets"
    )
    ########################## DATS model fields #############################
    alternate_identifiers = ArrayField(JSONField(null=True, blank=True),
        blank=True, null=True,
        help_text='Alternate identifiers for the dataset.')
    related_identifiers = ArrayField(JSONField(null=True, blank=True),
        blank=True, null=True,
        help_text='Related identifiers for the dataset.')
    dates = ArrayField(JSONField(null=True, blank=True),
        blank=True, null=True,
        help_text='Relevant dates for the datasets, a date must be added, '
        'e.g. creation date or last modification date should be added.')
    stored_in = JSONField(blank=True, null=True,
        help_text='The data repository hosting the dataset.')
    spatial_coverage = ArrayField(JSONField(null=True, blank=True),
        blank=True, null=True,
        help_text='The geographical extension and span covered '
        'by the dataset and its measured dimensions/variables.')
    types = ArrayField(JSONField(null=True, blank=True),
        blank=True, null=True,
        help_text='A term, ideally from a controlled terminology, '
        'identifying the dataset type or nature of the data, placing it in a typology.')
    availability = models.CharField(max_length=200, blank=True,
        help_text='A qualifier indicating the different types of availability '
        'for a dataset (available, unavailable, embargoed, available with '
        'restriction, information not available).')
    refinement = models.CharField(max_length=200, blank=True,
        help_text='A qualifier to describe the level of data '
        'processing of the dataset and its distributions.')
    aggregation = models.CharField(max_length=200, blank=True,
        help_text='A qualifier indicating if the entity represents '
        'an \'instance of dataset\' or a \'collection of datasets\'.')
    privacy = models.CharField(max_length=200, blank=True,
        help_text='A qualifier to describe the data protection applied '
        'to the dataset. This is relevant for clinical data.')
    distributions = ArrayField(JSONField(null=True, blank=True),
        blank=True, null=True,
        help_text='The distribution(s) by which datasets are made available (for example: mySQL dump).')
    dimensions = ArrayField(JSONField(null=True, blank=True),
        blank=True, null=True,
        help_text='The different dimensions (granular components)  making up a dataset.')
    primary_publications = ArrayField(JSONField(null=True, blank=True),
        blank=True, null=True,
        help_text='The primary publication(s) associated with the dataset, '
        'usually describing how the dataset was produced.')
    citations = ArrayField(JSONField(null=True, blank=True),
        blank=True, null=True,
        help_text='The publication(s) that cite this dataset.')
    citation_count = models.IntegerField(blank=True, null=True,
        help_text='The number of publications that cite this dataset '
        '(enumerated in the citations property).')
    produced_by = JSONField(blank=True, null=True,
        help_text='A study process which generated a given dataset, if any.')
    creators = ArrayField(JSONField(null=True, blank=True),
        blank=True, null=True,
        help_text='The person(s) or organization(s) which contributed to the creation of the dataset.')
    licenses = ArrayField(JSONField(null=True, blank=True),
        blank=True, null=True,
        help_text='The terms of use of the dataset.')
    # is_about this field will be calculated based on sample field
    # in tableOwnership
    has_part = models.ManyToManyField("self", blank=True,
        help_text='A Dataset that is a subset of this Dataset; '
        'Datasets declaring the \'hasPart\' relationship are considered a collection '
        'of Datasets, the aggregation criteria could be included in the \'description\' field.')
    acknowledges = ArrayField(JSONField(null=True, blank=True),
        blank=True, null=True,
        help_text='The grant(s) which funded and supported the work reported by the dataset.')
    keywords = ArrayField(JSONField(null=True, blank=True),
        blank=True, null=True,
        help_text='Tags associated with the dataset, which will help in its discovery.')
    extra_properties = JSONField(blank=True, null=True,
        help_text='Extra properties that do not fit in the previous specified attributes.')

    ##########################################################################
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (ID: {self.identifier})"


class TableOwnership(models.Model):
    """
    Class to represent a Table, which are organizationally part of a Dataset and can optionally be
    attached to a Phenopacket (and possibly a Biosample).
    """

    table_id = models.CharField(primary_key=True, max_length=200)
    service_id = models.UUIDField(max_length=200)
    service_artifact = models.CharField(max_length=200, default="")
    data_type = models.CharField(max_length=200)  # TODO: Is this needed?

    # Delete table ownership upon project/dataset deletion
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE,
        related_name='table_ownerships')
    # If not specified, compound table which may link to many samples TODO: ???
    sample = models.ForeignKey("phenopackets.Biosample", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.dataset if not self.sample else self.sample} -> {self.table_id}"
