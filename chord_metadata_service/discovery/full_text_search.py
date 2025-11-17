from __future__ import annotations
from bento_lib.discovery import DiscoveryEntity
from django.contrib.postgres.search import SearchVector
from django.db import models
from django.db.models import Field, TextField
from django.db.models.functions import Cast
from typing import Type, TypeAlias

from chord_metadata_service.discovery.field_paths.utils import field_path_to_django_mapping

__all__ = [
    "FULL_TEXT_SEARCH_FIELDS",
    "full_text_search_vector",
    "BaseFTSModel",
    "ToFTSReprMixin",
]


GENOMIC_INTERPRETATION_PATH = ("interpretations", "diagnosis", "genomic_interpretations")
GENE_DESCRIPTOR_PATH = (*GENOMIC_INTERPRETATION_PATH, "gene_descriptor")
VARIANT_INTERPRETATION_PATH = (*GENOMIC_INTERPRETATION_PATH, "variant_interpretation")
VARIATION_DESCRIPTOR_PATH = (*VARIANT_INTERPRETATION_PATH, "variation_descriptor")

FTSFieldDescriptor: TypeAlias = list[str] | tuple[list[str], Type[Field]]


def _prefix_fts_field_descriptor(prefix: tuple[str, ...], f: FTSFieldDescriptor) -> FTSFieldDescriptor:
    return [*prefix, *f] if isinstance(f, list) else ([*prefix, *f], f[1])


FULL_TEXT_SEARCH_FIELDS: dict[DiscoveryEntity, tuple[FTSFieldDescriptor, ...]] = {
    "phenopacket": (
        ["id"],
        (["measurements"], TextField),
        (["medical_actions"], TextField),
        (["extra_properties"], TextField),
        # Phenotypic features, interpretations, and diseases are in fts_extra
        #  - the corresponding model classes implement ToFTSReprMixin
        #  - get_fts_extra(...) returns values from these many-to-many relationships to stringify into fts_extra
    ),
    "individual": (
        ["id"],
        ["alternate_ids"],
        ["date_of_birth"],
        ["sex"],
        ["karyotypic_sex"],
        (["gender"], TextField),
        (["taxonomy"], TextField),
        (["time_at_last_encounter"], TextField),
        (["time_at_last_encounter", "age"], TextField),
        (["time_at_last_encounter", "age_range"], TextField),
        # vital status is in fts_extra, as VitalStatus implements ToFTSReprMixin
        (["extra_properties"], TextField),
    ),
    "biosample": (
        ["id"],
        ["description"],
        (["sampled_tissue"], TextField),
        (["taxonomy"], TextField),
        (["time_of_collection"], TextField),
        # location_collected is in fts_extra, as GeoLocation implements ToFTSReprMixin
        (["histological_diagnosis"], TextField),
        (["tumor_progression"], TextField),
        (["tumor_grade"], TextField),
        (["diagnostic_markers"], TextField),
        (["extra_properties"], TextField),
        # Biosample -> Procedure
        (["procedure", "code"], TextField),
        (["procedure", "body_site"], TextField),
        (["procedure", "extra_properties"], TextField),
    ),
    "experiment": (
        # Experiment fields
        ["study_type"],
        ["experiment_type"],
        (["experiment_ontology"], TextField),
        ["molecule"],
        (["molecule_ontology"], TextField),
        ["library_strategy"],
        ["library_source"],
        ["library_selection"],
        ["library_layout"],
        ["extraction_protocol"],
        ["reference_registry_id"],
        (["extra_properties"], TextField),
        # instrument is in fts_extra, as Instrument implements ToFTSReprMixin
    ),
    "experiment_result": (
        ["description"],
        ["filename"],
        ["file_format"],
        ["genome_assembly_id"],
        ["data_output_type"],
        ["usage"],
        ["creation_date"],
        ["created_by"],
        (["extra_properties"], TextField),
    ),
}


def full_text_search_vector(queryset_entity: DiscoveryEntity) -> SearchVector:
    """
    Given a queryset entity (most likely phenopacket or individual, since they're more "top-level"), generate a Postgres
    SearchVector object for full-text search across the entity/linked entities (that aren't other discovery entities).
    """

    args = []

    fields: tuple[FTSFieldDescriptor, ...] = (*FULL_TEXT_SEARCH_FIELDS[queryset_entity], ["fts_extra"])
    for f in fields:
        field: list[str]
        fc: Type[Field] | None

        # Our fields listed in FULL_TEXT_SEARCH_FIELDS[entity] come in two forms:
        #  list[str]: a straight-up field path; doesn't need any casting for searching
        #  tuple[list[str], Type[Field]]: a field-path that must be cast to a specific type of field for searching
        if isinstance(f, list):
            field = f
            fc = None
        else:
            field = f[0]
            fc = f[-1]

        # re-write the field from a list[str] to a Django path, resolved to the current entity being queried.
        #  e.g, individual [sex] would be rewritten to "subject__sex" for a phenopacket queryset entity.
        field_str = field_path_to_django_mapping(field)
        args.append(Cast(field_str, fc()) if fc is not None else field_str)

    # TODO: explain

    return SearchVector(*args)


ONTOLOGY_CLASS_KEYS = frozenset({"id", "label"})


class FTSHelpersMixin:
    """Mixin class with helper utility methods for full-text search, shared between BaseFTSModel and ToFTSReprMixin."""

    @classmethod
    def fts_repr_value_to_str(cls, v) -> str:
        """
        Stringify a value to put as part of an FTS representation string. In special cases, this may perform a specific
        stringification procedure; e.g., if isinstance(v, ToFTSReprMixin), we call the fts_repr_values_to_str() function
        on v to get the values to include in its stringification.
        """

        if isinstance(v, dict) and frozenset(v.keys()) == ONTOLOGY_CLASS_KEYS:  # duck-type as ontology class
            return f"{v['id']} {v['label']}"
        elif isinstance(v, ToFTSReprMixin):
            return cls.fts_repr_values_to_str(*v.fts_repr_values())
        elif isinstance(v, list) or isinstance(v, tuple):
            return cls.fts_repr_values_to_str(*v)
        return str(v)

    @classmethod
    def fts_repr_should_be_skipped(cls, v) -> bool:
        """
        Given a potential full-text search value (to be part of a full-text search string), return whether it should be
        skipped (presumably since it would not be informative for the search, e.g., an empty string or "True").
        If value is falsey, an integer, or a boolean, the value is not useful for full-text search (FTS) and shouldn't
        be included in any FTS representation.
        """
        return (not v) or isinstance(v, int) or isinstance(v, bool)

    @classmethod
    def fts_repr_values_to_str(cls, *args) -> str:
        """
        Given a list of full-text search values, convert them into a string, skipping anything that doesn't make sense
        to include (e.g., context-free integers/booleans).
        """
        return " ".join(map(cls.fts_repr_value_to_str, filter(lambda x: not cls.fts_repr_should_be_skipped(x), args)))


class BaseFTSModel(models.Model, FTSHelpersMixin):
    """
    Abstract base Django model containing a field definition and function definitions for full-text-search models.
    Really, in this case, the set of models inheriting this should be 1:1 with Discovery Entity models (which also
    all inherit BaseScopeableModel) currently. This should probably be cleaned up into a single abstract
    "Discovery Entity base model" class.
    """

    # to be used for full-text/trigram search only; not any source of truth!
    fts_extra = models.TextField(blank=True, null=False, default="")

    class Meta:
        # Abstract prevents the creation of a BaseTimeStamp table
        abstract = True

    def get_fts_extra(self) -> tuple:
        return ()

    def save(self, *args, **kwargs):
        vals = self.get_fts_extra()
        self.fts_extra = self.fts_repr_values_to_str(*vals) if vals else ""
        super().save(*args, **kwargs)


class ToFTSReprMixin:
    """
    Mixin class for Django models implementing <...>.fts_repr_values(), which converts a model instance to a list of
    values to be then converted to a string by <...>.fts_repr_values_to_str(). This is for full-text search purposes.
    """

    def fts_repr_values(self) -> tuple:
        return ()
