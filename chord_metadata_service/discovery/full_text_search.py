from __future__ import annotations
from bento_lib.discovery import DiscoveryEntity
from django.contrib.postgres.search import SearchVector, TrigramSimilarity, TrigramWordSimilarity, SearchQuery
from django.db import models
from django.db.models import Field, Func, TextField, QuerySet, Q
from django.db.models.functions import Cast, Greatest
from typing import Type, Callable

from .field_paths.utils import field_path_to_django_mapping
from .types import FTSType

__all__ = [
    "FULL_TEXT_SEARCH_FIELDS",
    "entity_search_fields",
    "full_text_search_vector",
    "normal_full_text_search",
    "trigram_similarity_search",
    "BaseFTSModel",
    "FTSHelpersMixin",
    "ToFTSReprMixin",
]

GENOMIC_INTERPRETATION_PATH = ("interpretations", "diagnosis", "genomic_interpretations")
GENE_DESCRIPTOR_PATH = (*GENOMIC_INTERPRETATION_PATH, "gene_descriptor")
VARIANT_INTERPRETATION_PATH = (*GENOMIC_INTERPRETATION_PATH, "variant_interpretation")
VARIATION_DESCRIPTOR_PATH = (*VARIANT_INTERPRETATION_PATH, "variation_descriptor")

type TrigramFunc = Type[TrigramWordSimilarity] | Type[TrigramSimilarity]
type FTSFieldDescriptor = tuple[list[str], Type[Field] | None, TrigramFunc | Callable[[str], TrigramFunc] | None]

FULL_TEXT_SEARCH_FIELDS: dict[DiscoveryEntity, tuple[FTSFieldDescriptor, ...]] = {
    "phenopacket": (
        (["id"], None, TrigramSimilarity),
        (["measurements"], TextField, TrigramWordSimilarity),
        (["medical_actions"], TextField, TrigramWordSimilarity),
        (["extra_properties"], TextField, TrigramWordSimilarity),
        # Phenotypic features, interpretations, and diseases are in fts_extra
        #  - the corresponding model classes implement ToFTSReprMixin
        #  - get_fts_extra(...) returns values from these many-to-many relationships to stringify into fts_extra
    ),
    "individual": (
        (["id"], None, TrigramSimilarity),
        (["alternate_ids"], TextField, TrigramWordSimilarity),
        (["date_of_birth"], TextField, TrigramWordSimilarity),
        # special case: for trigram search, we can't use word similarity in reciprocal search cases since these share
        # common roots (unknown, other) in their controlled vocabulary separated by underscores. of course, there are
        # other uses of "unknown" in phenopackets that we don't deal with...
        (["sex"], None, lambda q: TrigramSimilarity if "_ka" in q.lower() else TrigramWordSimilarity),
        (["karyotypic_sex"], None, lambda q: TrigramSimilarity if "_se" in q.lower() else TrigramWordSimilarity),
        # ---
        (["gender"], TextField, TrigramWordSimilarity),
        (["taxonomy"], TextField, TrigramWordSimilarity),
        (["time_at_last_encounter"], TextField, TrigramWordSimilarity),
        (["time_at_last_encounter", "age"], TextField, TrigramWordSimilarity),
        (["time_at_last_encounter", "age_range"], TextField, TrigramWordSimilarity),
        # vital status is in fts_extra, as VitalStatus implements ToFTSReprMixin
        (["extra_properties"], TextField, TrigramWordSimilarity),
    ),
    "biosample": (
        (["id"], None, TrigramSimilarity),
        (["description"], None, TrigramWordSimilarity),
        (["sampled_tissue"], TextField, TrigramWordSimilarity),
        (["taxonomy"], TextField, TrigramWordSimilarity),
        (["time_of_collection"], TextField, TrigramWordSimilarity),
        # location_collected is in fts_extra, as GeoLocation implements ToFTSReprMixin
        (["histological_diagnosis"], TextField, TrigramWordSimilarity),
        (["tumor_progression"], TextField, TrigramWordSimilarity),
        (["tumor_grade"], TextField, TrigramWordSimilarity),
        (["diagnostic_markers"], TextField, TrigramWordSimilarity),
        (["extra_properties"], TextField, TrigramWordSimilarity),
        # Biosample -> Procedure
        (["procedure", "code"], TextField, TrigramWordSimilarity),
        (["procedure", "body_site"], TextField, TrigramWordSimilarity),
        (["procedure", "extra_properties"], TextField, TrigramWordSimilarity),
    ),
    "experiment": (
        # Experiment fields
        (["description"], None, TrigramWordSimilarity),
        (["study_type"], None, TrigramSimilarity),
        (["experiment_type"], None, TrigramWordSimilarity),
        (["experiment_ontology"], TextField, TrigramWordSimilarity),
        (["molecule"], None, TrigramSimilarity),
        (["molecule_ontology"], TextField, TrigramWordSimilarity),
        (["library_id"], None, TrigramSimilarity),
        (["library_description"], None, TrigramWordSimilarity),
        (["library_strategy"], None, TrigramWordSimilarity),
        (["library_source"], None, TrigramWordSimilarity),
        (["library_selection"], None, TrigramWordSimilarity),
        (["library_layout"], None, TrigramWordSimilarity),
        (["library_extract_id"], None, TrigramWordSimilarity),
        (["extraction_protocol"], None, TrigramWordSimilarity),
        (["protocol_url"], None, TrigramWordSimilarity),
        (["reference_registry_id"], None, TrigramSimilarity),
        (["qc_flags"], TextField, TrigramWordSimilarity),
        (["extra_properties"], TextField, TrigramWordSimilarity),
        # instrument is in fts_extra, as Instrument implements ToFTSReprMixin
    ),
    "experiment_result": (
        (["description"], None, TrigramWordSimilarity),
        (["filename"], None, TrigramWordSimilarity),
        (["file_format"], None, TrigramSimilarity),
        (["genome_assembly_id"], None, TrigramSimilarity),
        (["data_output_type"], None, TrigramSimilarity),
        (["usage"], None, TrigramWordSimilarity),
        (["creation_date"], None, TrigramWordSimilarity),
        (["created_by"], None, TrigramWordSimilarity),
        (["extra_properties"], TextField, TrigramWordSimilarity),
    ),
}


def get_trigram_min_similarity(query_len: int) -> tuple[float, float]:
    """
    Given the length of a trigram full-text search query, returns the minimum trigram similarity and minimum trigram
    word similarity for matches. Which function is used depends on the field and sometimes the query.
    This helps give fewer false positives with short queries, since two-letter overlaps become significant.
    """
    if query_len <= 2:
        return 1.0, 1.0
    elif query_len <= 4:
        return 0.65, 0.75
    elif query_len <= 10:
        return 0.5, 0.55
    else:
        return 0.4, 0.45


def entity_search_fields(queryset_entity: DiscoveryEntity, trigram_query: str | None = None) -> list[str | Cast | Func]:
    """
    Given a discovery entity, returns a list of fields to be used for full-text search - either just the field name, if
    they're already text fields/compatible, or a Cast to TextField if they need to be cast as text in Postgres.
    """

    args: list[str | Cast | TrigramSimilarity | TrigramWordSimilarity] = []

    fields: tuple[FTSFieldDescriptor, ...] = (
        *FULL_TEXT_SEARCH_FIELDS[queryset_entity],
        (["fts_extra"], None, TrigramWordSimilarity),
    )

    for f in fields:
        field: list[str]
        fc: Type[Field] | None

        # Our fields listed in FULL_TEXT_SEARCH_FIELDS[entity] contain the following entries:
        #  list[str]
        #  Type[Field]: a cast to a specific type of field for searching if needed, otherwise None if string-like
        #  Type[TrigramWordSimilarity] | Type[TrigramSimilarity] | lambda --> aforementioned:
        #   trigram search function (or lambda from query --> trigram search function) to use for this field/query
        field = f[0]
        fc = f[1]
        trigram_func = f[2]

        # re-write the field from a list[str] to a Django path, resolved to the current entity being queried.
        #  e.g, individual [sex] would be rewritten to "subject__sex" for a phenopacket queryset entity.
        field_str = field_path_to_django_mapping(field)
        arg = field_str
        if fc is not None:
            arg = Cast(arg, fc())
        if trigram_query and trigram_func is not None:
            if trigram_func.__name__ == "<lambda>":
                trigram_func = trigram_func(trigram_query)
            if trigram_func == TrigramWordSimilarity:
                arg = trigram_func(trigram_query, arg)
            else:  # trigram_func == TrigramSimilarity:
                arg = trigram_func(arg, trigram_query)  # django/postgres why the inconsistent argument order...

        args.append(arg)

    return args


def full_text_search_vector(queryset_entity: DiscoveryEntity) -> SearchVector:
    """
    Given a queryset entity (most likely phenopacket or individual, since they're more "top-level"), generate a Postgres
    SearchVector object for full-text search across the entity/linked entities (that aren't other discovery entities).
    """
    return SearchVector(*entity_search_fields(queryset_entity))


def normal_full_text_search(queryset_entity: DiscoveryEntity, qs: QuerySet, query: str, fts_type: FTSType) -> QuerySet:
    """
    Given a queryset for a particular discovery entity, apply a Postgres full-text search for a query, using the
    specified full-text search type. See also:
    https://www.postgresql.org/docs/18/textsearch-controls.html#TEXTSEARCH-PARSING-QUERIES
    """
    return qs.annotate(search=full_text_search_vector(queryset_entity)).filter(
        search=SearchQuery(query, search_type=fts_type)
    )


def greatest_or_only(fs: list[Func]) -> Func:
    """
    The ORM Greatest function only works with more than one term; if there's only one term, we just use it directly.
    """
    return Greatest(*fs) if len(fs) > 1 else fs[0]


def trigram_similarity_search(queryset_entity: DiscoveryEntity, qs: QuerySet, query: str) -> QuerySet:
    """
    Given a queryset for a particular discovery entity, apply a text query using a trigram word similarity search,
    taking the greatest trigram word similarity of all text search fields as the overall record similarity.
    Word similarity measures whether the query matches any word/token within the field, making it suitable for
    searching within long strings such as file paths.
    """

    # we need to be more strict with shorter queries since otherwise we get weird false positives.
    # we also get different thresholds for similarity vs. word similarity - the latter should be more strict.
    min_similarity, min_word_similarity = get_trigram_min_similarity(len(query))

    # get entity search fields to split them up according to trigram function type, since we have different thresholds
    # for each:

    trigram_fields = entity_search_fields(queryset_entity, trigram_query=query)

    similarity_fields = []
    word_similarity_fields = []

    for t in trigram_fields:
        if isinstance(t, TrigramSimilarity):
            similarity_fields.append(t)
        else:  # isinstance(t, TrigramWordSimilarity)
            word_similarity_fields.append(t)

    return qs.annotate(
        similarity=greatest_or_only(similarity_fields),
        word_similarity=greatest_or_only(word_similarity_fields),
    ).filter(Q(similarity__gte=min_similarity) | Q(word_similarity__gte=min_word_similarity))


AGE_KEY = frozenset({"age"})
ISO_8601_DURATION_KEY = frozenset({"iso8601duration"})
UNHELPFUL_KEYS = frozenset({"id", "description", "label", "ontology_class"})


class FTSHelpersMixin:
    """Mixin class with helper utility methods for full-text search, shared between BaseFTSModel and ToFTSReprMixin."""

    @classmethod
    def fts_repr_value_to_str(cls, v) -> str:
        """
        Stringify a value to put as part of an FTS representation string. In special cases, this may perform a specific
        stringification procedure; e.g., if isinstance(v, ToFTSReprMixin), we call the fts_repr_values_to_str() function
        on v to get the values to include in its stringification.
        """

        if isinstance(v, dict):
            items = []
            for kk, vv in v.items():
                if kk not in UNHELPFUL_KEYS:
                    items.append(kk)
                items.append(vv)
            return cls.fts_repr_values_to_str(*items)
        elif isinstance(v, ToFTSReprMixin):  # helps recursively populate fts_extra fields
            return cls.fts_repr_values_to_str(*v.fts_repr_values())
        elif isinstance(v, list) or isinstance(v, tuple):
            return cls.fts_repr_values_to_str(*v)
        return str(v).strip()

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
        if len(args) == 1 and isinstance(args[0], ToFTSReprMixin):
            args = args[0].fts_repr_values()
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
        # Abstract prevents the creation of a BaseFTSModel table
        abstract = True

    def get_fts_extra(self) -> tuple:
        # This will in general be overridden to return a mixture of fields from the current model, and other model
        # objects (which can be thought of as "sub-models" of this main model, e.g., a phenotypic feature) that
        # themselves implement the below ToFTSReprMixin class, allowing them to specify their own FTS fields/values.
        return ()

    def populate_fts_extra(self):
        vals = self.get_fts_extra()
        self.fts_extra = self.fts_repr_values_to_str(*vals) if vals else ""
        # must call save()!


class ToFTSReprMixin:
    """
    Mixin class for Django models implementing <...>.fts_repr_values(), which converts a model instance to a list of
    values to be then converted to a string by <...>.fts_repr_values_to_str(). This is for full-text search purposes.

    In general, the Django models implementing this mixin are NOT discovery entity models, but rather "sub-models"
    (non-top-level concepts) linked from discovery entity models.
    """

    def fts_repr_values(self) -> tuple:  # pragma no cover
        return ()
