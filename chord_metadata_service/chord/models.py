import uuid

from django.contrib.postgres.fields import JSONField
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

    project_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    data_use = JSONField()

    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (ID: {self.project_id})"


class Dataset(models.Model):
    """
    Class to represent a Dataset, which contains multiple Phenopackets.
    """

    dataset_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    project = models.ForeignKey(Project, on_delete=models.CASCADE)  # Delete dataset upon project deletion

    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (ID: {self.dataset_id})"


class TableOwnership(models.Model):
    """
    Class to represent a Table, which are organizationally part of a Dataset and can optionally be
    attached to a Phenopacket (and possibly a Biosample).
    """

    table_id = models.UUIDField(primary_key=True)
    service_id = models.UUIDField()
    data_type = models.CharField(max_length=200)  # TODO: Is this needed?

    # Delete table ownership upon project/dataset deletion
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    # If not specified, compound table which may link to many samples TODO: ???
    sample = models.ForeignKey("phenopackets.Biosample", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.dataset if not self.sample else self.sample} -> {self.table_id}"
