from __future__ import annotations  # need to use string-based annotations to make the below type-checking imports work
from abc import abstractmethod
from django.db.models import Model, QuerySet
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
        TODO
        """
        pass

    def scope_contains_object(self, scope: ValidatedDiscoveryScope) -> bool:
        """
        TODO
        """
        return self.get_model_scoped_queryset(scope).filter(pk=self.pk).exists()

    async def scope_contains_object_async(self, scope: ValidatedDiscoveryScope) -> bool:
        return await self.get_model_scoped_queryset(scope).filter(pk=self.pk).aexists()

    @classmethod
    def get_model_scoped_queryset(cls, scope: ValidatedDiscoveryScope) -> QuerySet:
        """
        TODO
        """

        filter_scope: PublicScopeFilterKeys
        if scope.dataset_id:
            filter_scope = "dataset"
            value = scope.dataset_id
        elif scope.project_id and not scope.dataset_id:
            filter_scope = "project"
            value = scope.project_id
        else:
            return cls.objects.all()

        scope_filter_spec = cls.get_scope_filters()[filter_scope]

        filter_query = scope_filter_spec["filter"]
        prefetch = scope_filter_spec["prefetch_related"]

        return cls.objects.prefetch_related(*prefetch).filter(**{filter_query: value})


# Common model scope filters for phenopacket + experiment, which share a top-level dataset property.
TOP_LEVEL_MODEL_SCOPE_FILTERS: ModelScopeFilters = {
    "project": {
        "filter": "dataset__project__identifier",
        "prefetch_related": ("dataset__project",),
    },
    "dataset": {
        "filter": "dataset__identifier",
        "prefetch_related": ("dataset",),
    },
}
