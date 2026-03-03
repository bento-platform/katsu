from collections import OrderedDict
from rest_framework import serializers
from typing import Sequence


class GenericSerializer(serializers.ModelSerializer):
    """Subclass of ModelSerializer"""

    always_include: tuple[str, ...] = ()

    def __init__(self, *args, **kwargs):
        exclude_when_nested: Sequence[str] | None = kwargs.pop("exclude_when_nested", None)
        super(GenericSerializer, self).__init__(*args, **kwargs)

        if exclude_when_nested:
            for field_name in exclude_when_nested:
                self.fields.pop(field_name)

    def to_representation(self, instance):
        """Return only not empty fields"""
        final_object = super().to_representation(instance)
        # filter null/falsey values and create new dict - but keep any integers/floats, even if 0
        final_object = OrderedDict(
            list(
                filter(
                    lambda x: x[1] or isinstance(x[1], int) or isinstance(x[1], float) or x[0] in self.always_include,
                    final_object.items(),
                )
            )
        )
        return final_object
