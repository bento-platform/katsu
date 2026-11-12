from __future__ import annotations  # need to use string-based annotations to make the below type-checking imports work
from abc import abstractmethod
from dataclasses import dataclass
from django.core.exceptions import FieldDoesNotExist
from django.db.models import FETCH_PEERS, ForeignObjectRel, Model, Prefetch, Q, QuerySet
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

    @classmethod
    def get_model_scoped_queryset(cls, scope: ValidatedDiscoveryScope) -> QuerySet:
        """
        Returns a queryset (and subset) of objects of this model which belong to the passed scope. This method uses the
        defined get_scope_filters() function to narrow the queryset.
        """

        class_scope_filters_and_prefetches = cls.get_scope_filters()

        base_prefetch_related = class_scope_filters_and_prefetches["base_prefetch_related"]

        filter_scope: PublicScopeFilterKeys
        if scope.dataset_id:
            filter_scope = "dataset"
            value = scope.dataset_id
        elif scope.project_id and not scope.dataset_id:
            filter_scope = "project"
            value = scope.project_id
        else:
            return cls.objects.distinct().prefetch_related(*_expand_prefetch_paths(cls, base_prefetch_related))

        scope_filter_spec = class_scope_filters_and_prefetches[filter_scope]

        prefetch = (
            *base_prefetch_related,
            *(p for p in scope_filter_spec.get("prefetch_related", ()) if p not in base_prefetch_related),
        )

        filter_query = scope_filter_spec["filter"]
        if isinstance(filter_query, tuple):
            # If filter is a tuple, the field contains multiple filters that are ORed together. This is useful for,
            # e.g., the Resource model, where there are multiple possible paths one can take from the object to the
            # parent dataset(s).
            obj_q = Q(**{filter_query[0]: value})
            for fq in filter_query[1:]:
                obj_q = obj_q | Q(**{fq: value})
        else:
            # Just one filter to get the scoped queryset
            obj_q = Q(**{filter_query: value})

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
