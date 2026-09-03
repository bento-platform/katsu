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
from rest_framework.response import Response
from rest_framework.views import APIView

from chord_metadata_service.authz.middleware import authz_middleware as authz
from chord_metadata_service.authz.permissions import BentoAllowAnyReadOnly, BentoDeferToHandler
from chord_metadata_service.phenopackets.models import Phenopacket
from chord_metadata_service.restapi.pagination import CataloguePagination

from .catalogue_filters import FACET_FIELDS, active_facets, apply_facets
from .models import Dataset
from .serializers import DatasetSerializer

__all__ = ["CatalogueSearchView"]


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


def with_sort_annotations(qs: QuerySet) -> QuerySet:
    return qs.annotate(
        _sort_updated=Coalesce(F("last_modified"), F("updated_at"), output_field=DateTimeField()),
        _sort_created=Coalesce(F("release_date"), F("created_at"), output_field=DateTimeField()),
    )


# --- Per-dataset individual/biosample counts, for sorting only -------------------------------------------------------
#
# These are raw (uncensored) counts, used purely to rank the catalogue before pagination. The *displayed*
# counts_by_entity value for each result still comes from DatasetSerializer, which applies the same small-cell
# censoring used everywhere else in the API (see chord/utils.py::get_censored_counts_for_serializer). Sorting by the
# raw count is an accepted proxy-ranking trade-off: censoring is a display transform on top of true counts, not a
# rank-altering one.


def with_count_annotations(qs: QuerySet) -> QuerySet:
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
        individual_count=Coalesce(Subquery(individual_sq, output_field=IntegerField()), 0),
        biosample_count=Coalesce(Subquery(biosample_sq, output_field=IntegerField()), 0),
    )


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
        counts = {row["value"]: row["count"] for row in rows if row["value"]}
        for v in active.get(facet_id, []):
            counts.setdefault(v, 0)
        facets[facet_id] = [
            {"value": v, "count": c} for v, c in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        ]
    return facets


# --- View ----------------------------------------------------------------------------------------------------------


class CatalogueSearchView(APIView):
    """
    GET /catalogue?q=...&domain=X&domain=Y&status=Ongoing&sort=updated_desc&page=1&page_size=24

    Server-side search/facet/sort/pagination over the dataset catalogue, replacing the previous client-side
    implementation that fetched the full unpaginated dataset list.
    """

    permission_classes = [BentoAllowAnyReadOnly | BentoDeferToHandler]

    def get(self, request: DrfRequest, *args, **kwargs):
        authz.mark_authz_done(request)

        q = request.query_params.get("q", "").strip()
        sort_key = request.query_params.get("sort", DEFAULT_SORT)
        if sort_key not in SORT_OPTIONS:
            sort_key = DEFAULT_SORT

        active = active_facets(request.query_params)

        base_qs = with_search_annotations(Dataset.objects.select_related("project"))
        base_qs = apply_search(base_qs, q)

        facets = compute_facets(base_qs, active)

        results_qs = apply_facets(base_qs, active)
        results_qs = with_count_annotations(results_qs)
        results_qs = with_sort_annotations(results_qs)

        field_name, desc = SORT_OPTIONS[sort_key]
        order_field = f"-{field_name}" if desc else field_name
        results_qs = results_qs.order_by(order_field, "identifier")

        paginator = CataloguePagination()
        page = paginator.paginate_queryset(results_qs, request, view=self)

        serializer_context = {"request": request}
        results = [
            {
                "dataset": DatasetSerializer(ds, context=serializer_context).data,
                "project": {"identifier": str(ds.project_id), "title": ds.project.title},
            }
            for ds in page
        ]

        return Response(
            {
                "results": results,
                "pagination": {
                    "page": paginator.page.number,
                    "page_size": paginator.get_page_size(request),
                    "total": paginator.page.paginator.count,
                },
                "facets": facets,
            }
        )
