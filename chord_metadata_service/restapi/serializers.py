from collections import OrderedDict
from collections.abc import Sequence

from rest_framework import serializers

__all__ = ["WRITE_SCOPE_CONTEXT_KEY", "GenericSerializer"]

# Serializer context key holding the ValidatedDiscoveryScope a create/update is authorized for
WRITE_SCOPE_CONTEXT_KEY = "write_scope"


class GenericSerializer(serializers.ModelSerializer):
    """Subclass of ModelSerializer"""

    always_include: tuple[str, ...] = ()

    def __init__(self, *args, **kwargs):
        exclude_when_nested: Sequence[str] | None = kwargs.pop("exclude_when_nested", None)
        super().__init__(*args, **kwargs)

        if exclude_when_nested:
            for field_name in exclude_when_nested:
                self.fields.pop(field_name)

    def get_fields(self):
        """
        With a write scope in the context, narrow primary key relations to referenceable objects, so out-of-scope
        keys fail with the same "does not exist" error as missing ones.
        """
        fields = super().get_fields()

        if (scope := self.context.get(WRITE_SCOPE_CONTEXT_KEY)) is None:
            return fields

        for field in fields.values():
            relation = field.child_relation if isinstance(field, serializers.ManyRelatedField) else field
            if not isinstance(relation, serializers.PrimaryKeyRelatedField) or relation.queryset is None:
                continue
            if (get_referenceable := getattr(relation.queryset.model, "get_referenceable_queryset", None)) is not None:
                relation.queryset = get_referenceable(scope)

        return fields

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
