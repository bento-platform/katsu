from abc import abstractmethod
from django.db import models


class IndexableMixin:
    @property
    def index_id(self):
        return f"{self.__class__.__name__}|{self.__str__()}"


class SchemaType(models.TextChoices):
    PHENOPACKET = ("PHENOPACKET", "PHENOPACKET")
    BIOSAMPLE = ("BIOSAMPLE", "BIOSAMPLE")
    INDIVIDUAL = ("INDIVIDUAL", "INDIVIDUAL")


class BaseExtraProperties(models.Model):
    extra_properties = models.JSONField()

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