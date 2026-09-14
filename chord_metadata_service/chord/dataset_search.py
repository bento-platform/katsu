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
from .models import Dataset

__all__ = [
    "with_search_annotations",
    "apply_search",
    "SORT_OPTIONS",
    "DEFAULT_SORT",
    "COUNT_SORT_KEYS",
    "with_sort_annotations",
    "with_count_annotations",
    "sort_by_censored_counts",
    "compute_facets",
]


class Unaccent(Func):
    """Wraps an expression in Postgres' unaccent() SQL function (extension enabled in migration 0016)."""

    function = "unaccent"


# --- Search (?q=) --------------------------------------------------------------------------------------------------

# Fields searched, matching the client-side behaviour being replaced: title + description + long_description +
# domain + keywords, diacritic-stripped substring match.


def with_search_annotations(qs: QuerySet) -> QuerySet:
    return qs.annotate(
        _description_text=KeyTextTransform("description", "data"),
        _long_description_text=KeyTextTransform("content", KeyTextTransform("long_description", "data")),
        _domain_text=Func(F("domain"), Value(" "), function="array_to_string", output_field=TextField()),
        _keyword_text=Func(F("keyword_labels"), Value(" "), function="array_to_string", output_field=TextField()),
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


# --- Per-dataset individual/biosample counts, for sorting only -------------------------------------------------------
#
# Raw counts, annotated at the DB level. These are never returned or displayed directly — sort_by_censored_counts
# below re-derives a censored value from them per dataset before anything is ranked or returned, using the same
# small-cell censoring rules applied everywhere else in the API (see discovery/censorship.py).


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


# --- Censored count sort (individuals_desc / biosamples_desc) ------------------------------------------------------


async def sort_by_censored_counts(request: DrfRequest, qs: QuerySet, sort_key: str) -> list[Dataset]:
    datasets = [ds async for ds in qs]
    if not datasets:
        return datasets

    resources = tuple(ValidatedDiscoveryScope(ds.project, ds).as_authz_resource() for ds in datasets)
    permissions = (P_QUERY_DATASET_LEVEL_BOOLEAN, P_QUERY_DATASET_LEVEL_COUNTS, P_QUERY_DATA)
    results = await authz.async_evaluate_to_dict(request, resources, permissions)

    field = "individual_count" if sort_key == "individuals_desc" else "biosample_count"

    def censored_value(ds: Dataset, perms: dict) -> int:
        data_permissions = DataPermissions(
            bool_=perms[P_QUERY_DATASET_LEVEL_BOOLEAN],
            counts=perms[P_QUERY_DATASET_LEVEL_COUNTS],
            data=perms[P_QUERY_DATA],
        )
        threshold = get_threshold(ValidatedDiscoveryScope(ds.project, ds), data_permissions)
        if censor_count(ds.phenopacket_count, threshold) == 0:
            return 0  # phenopacket count itself is hidden, so nested counts must be hidden too
        return censor_count(getattr(ds, field), threshold)

    scored = [(censored_value(ds, perms), ds) for ds, perms in zip(datasets, results)]
    scored.sort(key=lambda sv: (-sv[0], str(sv[1].identifier)))
    return [ds for _, ds in scored]


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
