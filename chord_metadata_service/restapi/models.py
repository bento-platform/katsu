import logging
from abc import abstractmethod
from django.apps import apps
from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from jsonschema import Draft7Validator

logger = logging.getLogger(__name__)


class IndexableMixin:
    @property
    def index_id(self):
        return f"{self.__class__.__name__}|{self.__str__()}"


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
    def schema_type(self) -> SchemaType:
        """
        Returns the SchemaType of the model.
        Template method design pattern, implementation left to inheritors.
        """
        pass

    @abstractmethod
    def get_project_id(self) -> str:
        """
        Returns the Project.identifier of the project that owns this object.
        Template method design pattern, implementation left to inheritors.
        """
        pass

    def get_json_schema(self):
        """
        Returns a QuerySet[ProjectJsonSchema] containing schemas to validate
        Template method design pattern, uses concrete defs of schema_type 
        and get_project_id.
        """
        project_id = self.get_project_id()
        # Use apps.get_model to avoid circular import issues.
        model = apps.get_model("chord", "ProjectJsonSchema")
        project_json_schema = model.objects.get(
            Q(project_id=project_id) &
            Q(schema_type=self.schema_type)
        )
        return project_id, project_json_schema.json_schema
    
    def validate_json_schema(self):
        project_id, json_schema = self.get_json_schema()
        validator = Draft7Validator(json_schema)
        errors = []
        for err in validator.iter_errors(self.extra_properties):
            errors.append(err)
            logger.error(("JSON schema vaildation error on extra_properties for type "
                          f"{self.schema_type}, in project {project_id}: {err.message}"))
        return errors

    def clean(self):
        super().clean()
        if len(errors := self.validate_json_schema()) > 0:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Override in order to call self.clean to validate data
        self.clean()
        return super().save(*args, **kwargs)
