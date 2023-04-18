import logging
from abc import abstractmethod
from django.apps import apps
from django.db import models
from django.db.models import Q

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
        pass

    @abstractmethod
    def get_project_id(self) -> str:
        pass

    def get_json_schemas(self):
        _project_id = self.get_project_id()
        model = apps.get_model("chord", "ProjectJsonSchema")
        field_schemas = model.objects.filter(
            Q(project_id=_project_id) &
            Q(schema_type=self.schema_type)
        )
        logger.debug("ProjectJsonSchema objects to be used", field_schemas)
        return field_schemas

    def clean(self):
        super().clean()
        logger.debug("BaseExtraProperties schema validation")

        # TODO: json-schema validation

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)