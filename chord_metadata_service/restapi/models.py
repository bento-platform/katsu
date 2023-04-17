from chord_metadata_service.chord.models import Project
from django.db import models
from abc import ABC, abstractproperty, abstractmethod
from enum import Enum


class IndexableMixin:
    @property
    def index_id(self):
        return f"{self.__class__.__name__}|{self.__str__()}"


class SchemaType(models.TextChoices):
    PHENOPACKET = "PHENOPACKET"
    BIOSAMPLE = "BIOSAMPLE"
    INDIVIDUAL = "INDIVIDUAL"


class ExtraSchema(models.Model):
    id = models.CharField(primary_key=True, max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_schemas")
    extra_schema = models.JSONField()
    schema_type = models.CharField(max_length=200, choices=SchemaType)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["project", "schema_type"], name="unique_project_schema")
        ]


class BaseExtraProperties(models.Model):
    extra_properties = models.JSONField()
    extra_schema = models.ForeignKey(ExtraSchema, on_delete=models.CASCADE, related_name="")

    class Meta:
        abstract = True

    @property
    @abstractmethod
    def schema_type(self) -> SchemaType:
        pass

    def clean(self):
        super().clean()
        # TODO: json-schema validation

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)
