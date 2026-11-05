from collections import OrderedDict
from collections.abc import Sequence

from rest_framework import serializers


class GenericSerializer(serializers.ModelSerializer):
    """Subclass of ModelSerializer"""

    always_include: tuple[str, ...] = ()

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
