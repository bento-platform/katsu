from collections import OrderedDict
from collections.abc import Iterable, Sequence
from typing import ClassVar

from django.db.models import Prefetch, QuerySet
from rest_framework import serializers

RelatedLookup = str | Prefetch


def _prefixed_lookup(prefix: str, lookup: RelatedLookup) -> RelatedLookup:
    if isinstance(lookup, Prefetch):
        return Prefetch(f"{prefix}__{lookup.prefetch_through}", queryset=lookup.queryset)
    return f"{prefix}__{lookup}"


def prefixed_lookups(prefix: str, *lookup_groups: Iterable[RelatedLookup]) -> tuple[RelatedLookup, ...]:
    """Nests a (nested) serializer's related lookups under the relation it is reached through from the parent."""
    return tuple(_prefixed_lookup(prefix, lookup) for lookups in lookup_groups for lookup in lookups)


class GenericSerializer(serializers.ModelSerializer):
    """Subclass of ModelSerializer"""

    always_include: tuple[str, ...] = ()

    # Related lookups which serializing an instance (including any nested serializers) walks. Applied to a queryset
    # via setup_eager_loading(...) to avoid N+1 queries when serializing many instances, e.g., for CSV exports.
    select_related_fields: ClassVar[tuple[str, ...]] = ()
    # Prefetch objects with an ordered queryset keep to-many relations in a stable (primary key) order; a Prefetch must
    # come before any string lookups which traverse through it.
    prefetch_related_fields: ClassVar[tuple[RelatedLookup, ...]] = ()

    @classmethod
    def setup_eager_loading(cls, queryset: QuerySet) -> QuerySet:
        # guard: select_related() with no arguments follows *every* non-null foreign key instead of none
        if cls.select_related_fields:
            queryset = queryset.select_related(*cls.select_related_fields)
        return queryset.prefetch_related(*cls.prefetch_related_fields)

    def __init__(self, *args, **kwargs):
        exclude_when_nested: Sequence[str] | None = kwargs.pop("exclude_when_nested", None)
        super().__init__(*args, **kwargs)

        if exclude_when_nested:
            for field_name in exclude_when_nested:
                self.fields.pop(field_name)

        self._nested_serializers: dict[tuple, serializers.BaseSerializer] = {}

    def nested_data(self, serializer_cls: type[serializers.BaseSerializer], instance, **kwargs):
        """
        Serializes a related instance (or many=True relation) from within to_representation. Re-uses one nested
        serializer per (class, options) instead of instantiating one per object, since building a serializer's fields
        is expensive and otherwise dominates the time taken to serialize many objects.
        """
        if instance is None:
            return serializer_cls(instance, **kwargs).data  # preserve .data's behaviour for a missing instance
        key = (serializer_cls, repr(kwargs))
        if (nested := self._nested_serializers.get(key)) is None:
            nested = self._nested_serializers[key] = serializer_cls(**kwargs)
        return nested.to_representation(instance)

    def to_representation(self, instance):
        """Return only not empty fields"""
        final_object = super().to_representation(instance)
        # filter null/falsey values and create new dict - but keep any integers/floats, even if 0
        final_object = OrderedDict(
            list(
                filter(
                    lambda x: x[1] or isinstance(x[1], (int, float)) or x[0] in self.always_include,
                    final_object.items(),
                )
            )
        )
        return final_object
