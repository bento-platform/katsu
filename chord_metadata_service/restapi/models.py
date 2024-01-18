from abc import abstractmethod
from django.apps import apps
from django.db import models
from django.db.models import Q, QuerySet
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from jsonschema import Draft7Validator
from typing import Optional, List
from chord_metadata_service.logger import logger


class IndexableMixin:
    @property
    def index_id(self):
        return f"{self.__class__.__name__}|{self.__str__()}"


class BaseTimeStamp(models.Model):
    """
    Abstract django model class for tables that should have
    columns for 'created' and 'updated' timestamps.
    Use in inheritance.
    """
    created = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        # Abstract prevents the creation of a BaseTimeStamp table
        abstract = True


class SchemaType(models.TextChoices):
    PHENOPACKET = "PHENOPACKET", "Phenopacket"
    BIOSAMPLE = "BIOSAMPLE", "Biosample"
    INDIVIDUAL = "INDIVIDUAL", "Individual"


class BaseExtraProperties(models.Model):
    extra_properties = models.JSONField()

    class Meta:
        abstract = True

    @property
    @abstractmethod
    def schema_type(self) -> SchemaType:  # pragma: no cover
        """
        Returns the SchemaType of the model.
        Template method design pattern, implementation left to inheritors.
        """
        pass

    @abstractmethod
    def get_project_id(self) -> Optional[str]:  # pragma: no cover
        """
        Returns the Project.identifier of the project that owns this object.
        Template method design pattern, implementation left to inheritors.
        """
        pass

    def get_json_schema(self) -> Optional[QuerySet]:
        """
        Returns a tuple (project_id, QuerySet[ProjectJsonSchema]) containing schemas to validate
        Template method design pattern, uses concrete defs of schema_type
        and get_project_id.
        """
        project_id = self.get_project_id()
        if not project_id:
            return None

        # Use apps.get_model to avoid circular import issues.
        model = apps.get_model("chord", "ProjectJsonSchema")
        json_schema = None
        try:
            project_json_schema = model.objects.get(
                Q(project_id=project_id) &
                Q(schema_type=self.schema_type)
            )
            json_schema = project_json_schema.json_schema
        except ObjectDoesNotExist:
            logger.debug(f"No ProjectJsonSchema found for project ID {project_id} and schema type {self.schema_type}")
        return json_schema

    def validate_json_schema(self) -> List[str]:
        json_schema = self.get_json_schema()
        project_id = self.get_project_id()
        if not project_id or not json_schema:
            # Skip if no JSON schema exists for this project/schema_type combination
            return []

        errors = []
        validator = Draft7Validator(json_schema)
        for err in validator.iter_errors(self.extra_properties):
            errors.append(err)
            logger.error(("JSON schema vaildation error on extra_properties for type "
                          f"{self.schema_type}, in project {project_id}: {err.message}"))
        return errors

    def clean(self):
        super().clean()
        if self.extra_properties and len(errors := self.validate_json_schema()) > 0:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Override in order to call self.clean to validate data
        self.clean()
        return super().save(*args, **kwargs)
