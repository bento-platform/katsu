from chord_metadata_service.chord.models import Project
from django.db import models


class IndexableMixin:
    @property
    def index_id(self):
        return f"{self.__class__.__name__}|{self.__str__()}"


class ExtraSchema(models.Model):
    id = models.CharField(primary_key=True, max_length=200)
    # The json-schema $id of the parent object
    parent_schema_id = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project_schemas")
    json_schema = models.JSONField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["project", "parent_schema_id"], name="unique_project_schema")
        ]


class BaseExtraProperties(models.Model):
    extra_properties = models.JSONField()
    extra_schema = models.ForeignKey(ExtraSchema, on_delete=models.CASCADE, related_name="")

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        # TODO: json-schema validation

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)
