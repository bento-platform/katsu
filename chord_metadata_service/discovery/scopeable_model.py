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

    @staticmethod
    def get_select_related() -> tuple[str, ...]:
        """
        Returns a tuple of Django-formatted field paths to pass to .select_related(...) when querying this model for
        "deep" access/serialization purposes.
        """
        return ()

    @staticmethod
    def get_prefetch(top_level: bool) -> tuple[str, ...]:
        """
        Returns a tuple of Django-formatted field paths to pass to .prefetch_related(...) when querying this model for
        "deep" access/serialization purposes.
        """
        return ()

    async def scope_contains_object(self, scope: ValidatedDiscoveryScope) -> bool:
        """
        Returns whether the scoped queryset for the model and the passed scope contains this particular object.
        Useful for checking permissions.
        """
        return await self.get_model_scoped_queryset(scope).filter(pk=self.pk).aexists()

    @staticmethod
    def _query_for_one_or_more_paths_to_the_same_field(field: str | tuple[str, ...], value: str) -> Q:
        """
        Helper utility for get_model_scoped_queryset(...). Builds a Django Q object using one or more paths to a field
        holding the same semantic information (e.g., one or multiple paths to the dataset ID field) that should be
        filtered to a specific value (e.g., a specific dataset ID).
        """
        q: Q
        if isinstance(field, tuple):
            # If filter is a tuple, the field contains multiple filters that are ORed together. This is useful for,
            # e.g., the Resource model, where there are multiple possible paths one can take from the object to the
            # parent dataset(s).
            q = Q(**{field[0]: value})
            for fq in field[1:]:
                q = q | Q(**{fq: value})
        else:
            # Just one filter to get the scoped queryset
            q = Q(**{field: value})
        return q

    @classmethod
    def get_model_scoped_queryset(
        cls,
        scope: ValidatedDiscoveryScope,
        # what related model fields to prefetch/select when building the queryset
        #  scope_only: only perform prefetches related to scope (`dataset` in most cases, to access dataset.project_id)
        #      nested: TODO
        #   top_level: TODO
        prefetch_and_select_related: Literal["scope_only", "nested", "top_level"] = "scope_only",
    ) -> QuerySet:
        """
        Returns a queryset (and subset) of objects of this model which belong to the passed scope. This method uses the
        defined get_scope_filters() function to narrow the queryset.
        """

        # We will progressively build up the queryset by adding prefetch_related/select_related/filters as needed given
        # the current scope and level of detail required by the caller.
        qs = cls.objects.distinct()

        class_scope_filters_and_prefetches = cls.get_scope_filters()

        base_prefetch_related = class_scope_filters_and_prefetches["base_prefetch_related"]
        data_prefetch_related = (
            cls.get_prefetch(top_level=prefetch_and_select_related == "top_level")
            if prefetch_and_select_related != "scope_only"
            else ()
        )

        prefetch_related: list[str] = [*base_prefetch_related, *data_prefetch_related]

        should_select_related = prefetch_and_select_related != "scope_only"

        filter_scope: PublicScopeFilterKeys
        value: str
        if (dataset_id := scope.dataset_id) is not None:
            filter_scope = "dataset"
            value = dataset_id
        elif (project_id := scope.project_id) is not None:  # and dataset_id is None, because of the above branch
            filter_scope = "project"
            value = project_id
        else:  # node-level scope - no filtering to be done, so just return the queryset
            qs = qs.prefetch_related(*prefetch_related)
            if should_select_related:
                qs = qs.select_related(*cls.get_select_related())
            return qs

        scope_filter_spec = class_scope_filters_and_prefetches[filter_scope]

        prefetch_related.extend(p for p in scope_filter_spec.get("prefetch_related", ()) if p not in prefetch_related)

        # We now have all prefetch_related/select_related fields we need based on the current parameters, so we can add
        # them to the queryset:
        qs = qs.prefetch_related(*prefetch_related)
        if should_select_related:
            qs = qs.select_related(*cls.get_select_related())

        # Finally, we need to build a filter query for the current discovery scope:
        filter_query = cls._query_for_one_or_more_paths_to_the_same_field(scope_filter_spec["filter"], value)

        # ... and we can return the finalized queryset:
        return qs.filter(filter_query)


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
