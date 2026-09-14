"""
Shared query-building helpers behind the searchable/facetable/sortable GET /datasets listing
(chord/api_views.py::DatasetViewSet.list). Split out from the view itself so they stay unit-testable independently of
DRF request/response plumbing.
"""

from bento_lib.auth.permissions import P_QUERY_DATA, P_QUERY_DATASET_LEVEL_BOOLEAN, P_QUERY_DATASET_LEVEL_COUNTS
from django.db.models import (
    Count,
    DateTimeField,
    F,
    Func,
    IntegerField,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    TextField,
    Value,
)
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Coalesce
from rest_framework.request import Request as DrfRequest

from chord_metadata_service.authz.middleware import authz_middleware as authz
from chord_metadata_service.authz.types import DataPermissions
from chord_metadata_service.discovery.censorship import censor_count, get_threshold
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope
from chord_metadata_service.phenopackets.models import Phenopacket

from .dataset_facets import FACET_FIELDS, apply_facets
from .models import Dataset, DatasetTranslation

__all__ = [
    "with_search_annotations",
    "apply_search",
    "SORT_OPTIONS",
    "DEFAULT_SORT",
    "COUNT_SORT_KEYS",
    "CENSORED_COUNT_FIELDS",
    "with_sort_annotations",
    "with_count_annotations",
    "compute_censored_counts",
    "sort_datasets_by_censored_count",
    "compute_totals",
    "compute_facets",
]


class Unaccent(Func):
    """Wraps an expression in Postgres' unaccent() SQL function (extension enabled in migration 0016)."""

    function = "unaccent"


# --- Search (?q=) --------------------------------------------------------------------------------------------------

# Fields searched, matching the client-side behaviour being replaced: title + description + long_description +
# domain + keywords, diacritic-stripped substring match — against both the dataset's base (English) record and its
# French translation (chord.DatasetTranslation), if one exists, so a query matches whichever language it was typed
# in regardless of the viewer's own display language. Domain/keyword are structured/categorical rather than prose,
# so they're only searched on the base record for now — only title/description/long_description are duplicated
# per-translation.


def _translation_text_subquery(language: str, *key_path: str) -> Subquery:
    """Per-dataset, correlated lookup of one text field from a specific-language DatasetTranslation row, if any."""
    expr = KeyTextTransform(key_path[0], "data")
    for key in key_path[1:]:
        expr = KeyTextTransform(key, expr)
    translation = DatasetTranslation.objects.filter(dataset_id=OuterRef("identifier"), language=language)
    return Subquery(translation.annotate(_v=expr).values("_v")[:1], output_field=TextField())


def with_search_annotations(qs: QuerySet) -> QuerySet:
    return qs.annotate(
        _description_text=KeyTextTransform("description", "data"),
        _long_description_text=KeyTextTransform("content", KeyTextTransform("long_description", "data")),
        _domain_text=Func(F("domain"), Value(" "), function="array_to_string", output_field=TextField()),
        _keyword_text=Func(F("keyword_labels"), Value(" "), function="array_to_string", output_field=TextField()),
        _fr_title=_translation_text_subquery("fr", "title"),
        _fr_description_text=_translation_text_subquery("fr", "description"),
        _fr_long_description_text=_translation_text_subquery("fr", "long_description", "content"),
    )


def apply_search(qs: QuerySet, q: str) -> QuerySet:
    if not q:
        return qs
    uq = Unaccent(Value(q))
    return qs.filter(
        Q(title__unaccent__icontains=uq)
        | Q(_description_text__unaccent__icontains=uq)
        | Q(_long_description_text__unaccent__icontains=uq)
        | Q(_domain_text__unaccent__icontains=uq)
        | Q(_keyword_text__unaccent__icontains=uq)
        | Q(_fr_title__unaccent__icontains=uq)
        | Q(_fr_description_text__unaccent__icontains=uq)
        | Q(_fr_long_description_text__unaccent__icontains=uq)
    )


# --- Sorting (?sort=) -----------------------------------------------------------------------------------------------

SORT_OPTIONS: dict[str, tuple[str, bool]] = {
    "updated_desc": ("_sort_updated", True),
    "created_desc": ("_sort_created", True),
    "title_az": ("title", False),
    "individuals_desc": ("individual_count", True),
    "biosamples_desc": ("biosample_count", True),
}
DEFAULT_SORT = "updated_desc"

COUNT_SORT_KEYS: frozenset[str] = frozenset({"individuals_desc", "biosamples_desc"})


def with_sort_annotations(qs: QuerySet) -> QuerySet:
    return qs.annotate(
        _sort_updated=Coalesce(F("last_modified"), F("updated_at"), output_field=DateTimeField()),
        _sort_created=Coalesce(F("release_date"), F("created_at"), output_field=DateTimeField()),
    )


# --- Per-dataset phenopacket/individual/biosample counts, for sort/totals only -----------------------------------
#
# Raw counts, annotated at the DB level. These are never returned or displayed directly — compute_censored_counts
# below re-derives a censored value from them per dataset before anything is ranked, summed, or returned, using the
# same small-cell censoring rules applied everywhere else in the API (see discovery/censorship.py).


def with_count_annotations(qs: QuerySet) -> QuerySet:
    phenopacket_sq = (
        Phenopacket.objects.filter(dataset_id=OuterRef("identifier"))
        .order_by()
        .values("dataset_id")
        .annotate(c=Count("id"))
        .values("c")
    )
    individual_sq = (
        Phenopacket.objects.filter(dataset_id=OuterRef("identifier"))
        .order_by()
        .values("dataset_id")
        .annotate(c=Count("subject", distinct=True))
        .values("c")
    )
    biosample_sq = (
        Phenopacket.objects.filter(dataset_id=OuterRef("identifier"))
        .order_by()
        .values("dataset_id")
        .annotate(c=Count("biosamples", distinct=True))
        .values("c")
    )
    return qs.annotate(
        phenopacket_count=Coalesce(Subquery(phenopacket_sq, output_field=IntegerField()), 0),
        individual_count=Coalesce(Subquery(individual_sq, output_field=IntegerField()), 0),
        biosample_count=Coalesce(Subquery(biosample_sq, output_field=IntegerField()), 0),
    )


# --- Censored counts, shared by individuals_desc/biosamples_desc sort and ?include=totals --------------------------

# The entities a censored count is computed for. Both consumers below (sort, totals) key off these names.
CENSORED_COUNT_FIELDS: tuple[str, ...] = ("phenopacket", "individual", "biosample")

CensoredCounts = list[tuple[Dataset, dict[str, int]]]


async def compute_censored_counts(request: DrfRequest, qs: QuerySet) -> CensoredCounts:
    """
    Materializes `qs` (already annotated via with_count_annotations) and, for every dataset in it, censors its
    phenopacket/individual/biosample counts using the requester's real authz-evaluated permissions for that dataset
    — the same small-cell rules the display path applies (discovery/censorship.py), including: if a dataset's
    phenopacket count itself gets censored to 0, its nested individual/biosample counts are forced to 0 too, so they
    can't indirectly reveal a hidden phenopacket's existence.

    This needs a real per-dataset threshold (a project/dataset-level authz permission lookup), evaluated for every
    request regardless of whether it's authenticated — a public dataset can grant an anonymous caller counts-level
    access just as a logged-in one might be denied it — so it's one batched authz call up front rather than a
    single DB-level ORDER BY/SUM.
    """
    datasets = [ds async for ds in qs]
    if not datasets:
        return []

    resources = tuple(ValidatedDiscoveryScope(ds.project, ds).as_authz_resource() for ds in datasets)
    permissions = (P_QUERY_DATASET_LEVEL_BOOLEAN, P_QUERY_DATASET_LEVEL_COUNTS, P_QUERY_DATA)
    results = await authz.async_evaluate_to_dict(request, resources, permissions)

    def censored(ds: Dataset, perms: dict) -> dict[str, int]:
        data_permissions = DataPermissions(
            bool_=perms[P_QUERY_DATASET_LEVEL_BOOLEAN],
            counts=perms[P_QUERY_DATASET_LEVEL_COUNTS],
            data=perms[P_QUERY_DATA],
        )
        threshold = get_threshold(ValidatedDiscoveryScope(ds.project, ds), data_permissions)
        phenopacket = censor_count(ds.phenopacket_count, threshold)
        if phenopacket == 0:
            return dict.fromkeys(CENSORED_COUNT_FIELDS, 0)  # nested counts hidden too
        return {
            "phenopacket": phenopacket,
            "individual": censor_count(ds.individual_count, threshold),
            "biosample": censor_count(ds.biosample_count, threshold),
        }

    return [(ds, censored(ds, perms)) for ds, perms in zip(datasets, results)]


def sort_datasets_by_censored_count(censored_counts: CensoredCounts, sort_key: str) -> list[Dataset]:
    field = "individual" if sort_key == "individuals_desc" else "biosample"
    ordered = sorted(censored_counts, key=lambda dc: (-dc[1][field], str(dc[0].identifier)))
    return [ds for ds, _ in ordered]


def compute_totals(censored_counts: CensoredCounts) -> dict[str, int]:
    """Sums each entity's *censored* count across every dataset — never the raw one, so a total can't leak a count
    that wouldn't otherwise be shown for a dataset on its own (e.g. a single-dataset filtered result)."""
    totals = dict.fromkeys(CENSORED_COUNT_FIELDS, 0)
    for _, counts in censored_counts:
        for field in CENSORED_COUNT_FIELDS:
            totals[field] += counts[field]
    return totals


# --- Facets ------------------------------------------------------------------------------------------------------


def compute_facets(base_qs: QuerySet, active: dict[str, list[str]]) -> dict[str, list[dict]]:
    """
    Per-facet option counts. Each facet's counts exclude that facet's own active filter (but respect every other
    active facet + q), and any of the facet's currently-selected values are included even at count 0, so the UI can
    still offer to deselect them.
    """
    facets: dict[str, list[dict]] = {}
    for facet_id, (field_name, is_array) in FACET_FIELDS.items():
        scoped = apply_facets(base_qs, active, skip=facet_id)
        if is_array:
            rows = (
                scoped.annotate(value=Func(F(field_name), function="unnest"))
                .values("value")
                .annotate(count=Count("identifier", distinct=True))
            )
        else:
            rows = (
                scoped.exclude(**{f"{field_name}__isnull": True})
                .values(value=F(field_name))
                .annotate(count=Count("identifier", distinct=True))
            )
        # str(...) here, since e.g. the "project" facet's underlying field is a UUID FK: row["value"] comes back as a
        # uuid.UUID, but active facet values are always plain strings from the query params — without normalizing,
        # the zero-count backfill below would treat "same project, different type" as two distinct dict keys.
        counts = {str(row["value"]): row["count"] for row in rows if row["value"]}
        for v in active.get(facet_id, []):
            counts.setdefault(v, 0)
        facets[facet_id] = [
            {"value": v, "count": c} for v, c in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        ]
    return facets
