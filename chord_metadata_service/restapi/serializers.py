from collections import OrderedDict
from rest_framework import serializers
from typing import Tuple


class GenericSerializer(serializers.ModelSerializer):
    """ Subclass of ModelSerializer """
    always_include: Tuple[str, ...] = ()

    def __init__(self, *args, **kwargs):
        exclude_when_nested = kwargs.pop('exclude_when_nested', None)
        # fields to include
        fields = kwargs.pop('fields', None)
        super(GenericSerializer, self).__init__(*args, **kwargs)

        if exclude_when_nested:
            for field_name in exclude_when_nested:
                self.fields.pop(field_name)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_representation(self, instance):
        """ Return only not empty fields """
        final_object = super().to_representation(instance)
        # filter null values and create new dict
        final_object = OrderedDict(list(filter(lambda x: x[1] or x[0] in self.always_include, final_object.items())))
        return final_object
