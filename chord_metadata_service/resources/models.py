from django.contrib.postgres.fields import JSONField
from django.db import models

from chord_metadata_service.restapi.description_utils import rec_help

from . import descriptions as d


class Resource(models.Model):
    """
    Class to represent a description of an external resource
    used for referencing an object

    FHIR: CodeSystem
    """

    # resource_id e.g. "id": "uniprot"
    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.RESOURCE, "id"))
    name = models.CharField(max_length=200, help_text=rec_help(d.RESOURCE, "name"))
    namespace_prefix = models.CharField(max_length=200, help_text=rec_help(d.RESOURCE, "namespace_prefix"))
    url = models.URLField(max_length=200, help_text=rec_help(d.RESOURCE, "url"))
    version = models.CharField(max_length=200, help_text=rec_help(d.RESOURCE, "version"))
    iri_prefix = models.URLField(max_length=200, help_text=rec_help(d.RESOURCE, "iri_prefix"))
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.RESOURCE, "extra_properties"))
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
