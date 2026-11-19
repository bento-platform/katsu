from __future__ import annotations  # need to use string-based annotations to make the below type-checking imports work
from abc import abstractmethod
from dataclasses import dataclass
from django.core.exceptions import FieldDoesNotExist
from django.db.models import FETCH_PEERS, Exists, ForeignObjectRel, Model, OuterRef, Prefetch, Q, QuerySet
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    # gross hack to make type-checking possible without causing circular import issues.
    # see: https://stackoverflow.com/a/39757388
    from .scope import ValidatedDiscoveryScope
    from .types import ModelScopeFilters

__all__ = ["Prefetches", "BaseScopeableModel", "TOP_LEVEL_MODEL_SCOPE_FILTERS"]

PublicScopeFilterKeys = Literal["project", "dataset"]


def _related_model(model: type[Model], name: str) -> type[Model]:
    # Match on the name prefetch_related uses: the accessor name for reverse relations (e.g., "dataset_set"), which
    # _meta.get_field(...) does not accept, and the field name for forward ones.
    for f in model._meta.get_fields():
        if (f.get_accessor_name() if isinstance(f, ForeignObjectRel) else f.name) == name:
            return f.related_model
    raise FieldDoesNotExist(f"{model.__name__} has no relation '{name}'")


def _expand_prefetch_paths(model: type[Model], paths: tuple[str, ...], skip: frozenset[str] = frozenset()) -> list:
    """
    Turns relation paths into one Prefetch per path segment (parents before children), each loading its objects in
    primary key order and in FETCH_PEERS mode. Fetch modes don't carry over to objects loaded by a plain prefetch, so
    this is what lets foreign keys on prefetched objects be batch-loaded on first access instead of one by one.
    """
    lookups: dict[str, Prefetch] = {}
    for path in paths:
        current = model
        parts = path.split("__")
        for i, name in enumerate(parts):
            current = _related_model(current, name)
            prefix = "__".join(parts[: i + 1])
            if prefix not in skip and prefix not in lookups:
                queryset = current._default_manager.fetch_mode(FETCH_PEERS).order_by("pk")
                lookups[prefix] = Prefetch(prefix, queryset=queryset)
    return list(lookups.values())


def _path_prefixes(paths: tuple[str, ...]) -> frozenset[str]:
    return frozenset("__".join(p.split("__")[: i + 1]) for p in paths for i in range(p.count("__") + 1))


@dataclass(frozen=True)
class Prefetches:
    """
    The relations to eagerly load for one output shape of a model (e.g., the full JSON representation, or a CSV
    export), to avoid N+1 queries when serializing many objects. List only to-many relations (many-to-many, reverse
    foreign keys) and the relations leading to them; foreign keys and one-to-one fields are batch-loaded on first
    access via Django's FETCH_PEERS fetch mode instead.
    """

    paths: tuple[str, ...] = ()

    def setup_eager_loading(self, queryset: QuerySet) -> QuerySet:
        model = queryset.model
        # Querysets from get_model_scoped_queryset(...) already prefetch the model's scope relations, and Django
        # refuses a second Prefetch for an already-prefetched path, so we leave those to the scoped queryset.
        skip = (
            _path_prefixes(model.get_scope_filters()["base_prefetch_related"])
            if issubclass(model, BaseScopeableModel)
            else frozenset()
        )
        return queryset.fetch_mode(FETCH_PEERS).prefetch_related(*_expand_prefetch_paths(model, self.paths, skip))


class BaseScopeableModel(Model):
    class Meta:
        abstract = True

    @staticmethod
    @abstractmethod
    def get_scope_filters() -> ModelScopeFilters:  # pragma: no cover
        """
        Abstract static method (essentially a property) which returns a dictionary matching the ModelScopeFilters
        format, which defines which lookups are used to filter a queryset of objects of this model to just those which
        fall under a given scope.
        """
        pass

    async def scope_contains_object(self, scope: ValidatedDiscoveryScope) -> bool:
        """
        Returns whether the scoped queryset for the model and the passed scope contains this particular object.
        Useful for checking permissions.
        """
        return await self.get_model_scoped_queryset(scope).filter(pk=self.pk).aexists()

    @staticmethod
    def _or_lookups(filter_query: str | tuple[str, ...], value) -> Q:
        # A tuple holds several paths to the parent dataset(s) (e.g. for Resource), ORed together.
        lookups = filter_query if isinstance(filter_query, tuple) else (filter_query,)
        q = Q()
        for lookup in lookups:
            q |= Q(**{lookup: value})
        return q

    @staticmethod
    def _scope_filter_key(scope: ValidatedDiscoveryScope) -> tuple[PublicScopeFilterKeys, str] | None:
        if scope.dataset_id:
            return "dataset", scope.dataset_id
        elif scope.project_id:
            return "project", scope.project_id
        return None  # whole-instance scope

    @classmethod
    def get_scope_q(cls, scope: ValidatedDiscoveryScope) -> Q | None:
        """
        Returns the filter for this model's objects in the scope, or None for a whole-instance scope.
        It may follow multi-valued relations, so use a pk__in subquery to avoid duplicate rows.
        """
        if (key := cls._scope_filter_key(scope)) is None:
            return None
        filter_scope, value = key
        return cls._or_lookups(cls.get_scope_filters()[filter_scope]["filter"], value)

    @classmethod
    def get_dataset_link_lookups(cls) -> tuple[str, ...]:
        """
        Returns the lookups (ending in a dataset ID) which link objects of this model to a dataset.
        Override this if a model has dataset links other than its dataset scope filter.
        """
        filter_query = cls.get_scope_filters()["dataset"]["filter"]
        return filter_query if isinstance(filter_query, tuple) else (filter_query,)

    @classmethod
    def get_referenceable_queryset(cls, scope: ValidatedDiscoveryScope) -> QuerySet:
        """
        Returns the objects which a write under the scope may reference or produce: objects in the scope, plus
        objects with no dataset link outside it (referencing those could expose another dataset's data).
        """
        if (scope_q := cls.get_scope_q(scope)) is None:
            return cls.objects.all()
        # Correlated EXISTS, so each primary key DRF looks up uses index lookups, not a full-table join.
        return cls.objects.filter(
            Exists(cls.objects.filter(scope_q, pk=OuterRef("pk"))) | cls.get_referenceable_outside_scope_q(scope)
        )

    @classmethod
    def get_referenceable_outside_scope_q(cls, scope: ValidatedDiscoveryScope) -> Q:
        """
        Returns the filter for objects outside the (non-instance) scope which a write under it may still reference.
        Models can extend this with extra conditions.
        """
        # Avoid a circular import: chord.models imports the models which subclass this one.
        from chord_metadata_service.chord.models import Dataset

        outside_datasets = Dataset.objects.exclude(pk__in=Dataset.get_referenceable_queryset(scope).values("pk"))
        linked_outside_q = cls._or_lookups(
            tuple(f"{lookup}__in" for lookup in cls.get_dataset_link_lookups()), outside_datasets.values("pk")
        )
        return ~Q(Exists(cls.objects.filter(linked_outside_q, pk=OuterRef("pk"))))

    @classmethod
    def get_model_scoped_queryset(cls, scope: ValidatedDiscoveryScope) -> QuerySet:
        """
        Returns a queryset (and subset) of objects of this model which belong to the passed scope. This method uses the
        defined get_scope_filters() function to narrow the queryset.
        """

        class_scope_filters_and_prefetches = cls.get_scope_filters()

        base_prefetch_related = class_scope_filters_and_prefetches["base_prefetch_related"]

        if (key := cls._scope_filter_key(scope)) is None:
            return cls.objects.distinct().prefetch_related(*_expand_prefetch_paths(cls, base_prefetch_related))

        filter_scope, value = key
        scope_filter_spec = class_scope_filters_and_prefetches[filter_scope]

        prefetch = (
            *base_prefetch_related,
            *(p for p in scope_filter_spec.get("prefetch_related", ()) if p not in base_prefetch_related),
        )

        obj_q = cls._or_lookups(scope_filter_spec["filter"], value)
        return cls.objects.distinct().prefetch_related(*_expand_prefetch_paths(cls, prefetch)).filter(obj_q)


# Common model scope filters for phenopacket + experiment, which share a top-level dataset property.
TOP_LEVEL_MODEL_SCOPE_FILTERS: ModelScopeFilters = {
    "base_prefetch_related": ("dataset",),
    "project": {
        "filter": "dataset__project_id",
    },
    "dataset": {
        "filter": "dataset_id",
    },
}
