from __future__ import annotations  # need to use string-based annotations to make the below type-checking imports work
from abc import abstractmethod
from django.db.models import Model, Q, QuerySet
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    # gross hack to make type-checking possible without causing circular import issues.
    # see: https://stackoverflow.com/a/39757388
    from .scope import ValidatedDiscoveryScope
    from .types import ModelScopeFilters

__all__ = ["BaseScopeableModel", "TOP_LEVEL_MODEL_SCOPE_FILTERS"]

PublicScopeFilterKeys = Literal["project", "dataset"]


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
        # If filter is a tuple, the field contains multiple filters that are ORed together. This is useful for, e.g.,
        # the Resource model, where there are multiple possible paths one can take from the object to the parent
        # dataset(s).
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
        Returns the filter which narrows objects of this model to the passed scope, or None for a whole-instance scope.
        Note that the filter may follow multi-valued relations, so it can yield duplicate rows if used with filter(...)
        directly; use get_model_scoped_queryset(...) or a pk__in subquery when that matters.
        """
        if (key := cls._scope_filter_key(scope)) is None:
            return None
        filter_scope, value = key
        return cls._or_lookups(cls.get_scope_filters()[filter_scope]["filter"], value)

    @classmethod
    def get_dataset_link_lookups(cls) -> tuple[str, ...]:
        """
        Returns the lookups (ending in a dataset ID) through which objects of this model can be linked to a dataset.
        By default, these are the lookups used for dataset scoping; models which can also be linked to a dataset some
        other way (and so expose that dataset's data when referenced) should override this.
        """
        filter_query = cls.get_scope_filters()["dataset"]["filter"]
        return filter_query if isinstance(filter_query, tuple) else (filter_query,)

    @classmethod
    def get_referenceable_queryset(cls, scope: ValidatedDiscoveryScope) -> QuerySet:
        """
        Returns the objects of this model which a write made under the passed scope may reference or produce: objects
        inside the scope, plus objects which are not linked to any dataset at all (e.g., a newly created individual
        without any phenopackets yet), since those cannot expose any dataset's data.
        """
        if (scope_q := cls.get_scope_q(scope)) is None:
            return cls.objects.all()
        linked_q = Q()
        for lookup in cls.get_dataset_link_lookups():
            linked_q |= Q(**{f"{lookup}__isnull": False})
        return cls.objects.filter(
            Q(pk__in=cls.objects.filter(scope_q).values("pk")) | ~Q(pk__in=cls.objects.filter(linked_q).values("pk"))
        )

    @classmethod
    def get_model_scoped_queryset(cls, scope: ValidatedDiscoveryScope) -> QuerySet:
        """
        Returns a queryset (and subset) of objects of this model which belong to the passed scope. This method uses the
        defined get_scope_filters() function to narrow the queryset.
        """

        class_scope_filters_and_prefetches = cls.get_scope_filters()

        base_prefetch_related = class_scope_filters_and_prefetches["base_prefetch_related"]

        if (key := cls._scope_filter_key(scope)) is None:
            return cls.objects.distinct().prefetch_related(*base_prefetch_related)

        filter_scope, value = key
        scope_filter_spec = class_scope_filters_and_prefetches[filter_scope]

        prefetch = (
            *base_prefetch_related,
            *(p for p in scope_filter_spec.get("prefetch_related", ()) if p not in base_prefetch_related),
        )

        obj_q = cls._or_lookups(scope_filter_spec["filter"], value)
        return cls.objects.distinct().prefetch_related(*prefetch).filter(obj_q)


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
