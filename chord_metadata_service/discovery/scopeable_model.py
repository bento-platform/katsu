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

    @classmethod
    def get_model_scoped_queryset(cls, scope: ValidatedDiscoveryScope) -> QuerySet:
        """
        Returns a queryset (and subset) of objects of this model which belong to the passed scope. This method uses the
        defined get_scope_filters() function to narrow the queryset.
        """

        filter_scope: PublicScopeFilterKeys
        if scope.dataset_id:
            filter_scope = "dataset"
            value = scope.dataset_id
        elif scope.project_id and not scope.dataset_id:
            filter_scope = "project"
            value = scope.project_id
        else:
            return cls.objects.distinct()

        scope_filter_spec = cls.get_scope_filters()[filter_scope]

        prefetch = scope_filter_spec["prefetch_related"]

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

        return cls.objects.distinct().prefetch_related(*prefetch).filter(obj_q)


# Common model scope filters for phenopacket + experiment, which share a top-level dataset property.
TOP_LEVEL_MODEL_SCOPE_FILTERS: ModelScopeFilters = {
    "project": {
        "filter": "dataset__project_id",
        "prefetch_related": ("dataset",),
    },
    "dataset": {
        "filter": "dataset_id",
        "prefetch_related": (),
    },
}
