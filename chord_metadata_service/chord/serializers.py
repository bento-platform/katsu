from chord_lib.schemas.chord import CHORD_DATA_USE_SCHEMA
from chord_metadata_service.restapi.serializers import GenericSerializer
from jsonschema import Draft7Validator
from rest_framework import serializers

from .models import *


__all__ = ["ProjectSerializer", "DatasetSerializer", "TableOwnershipSerializer"]


#############################################################
#                                                           #
#              Project Management  Serializers              #
#                                                           #
#############################################################

class DatasetSerializer(GenericSerializer):
    # noinspection PyMethodMayBeStatic
    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters")
        return value.strip()

    class Meta:
        model = Dataset
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    # Don't inherit GenericSerializer to not pop empty fields

    datasets = DatasetSerializer(
        read_only=True, many=True, exclude_when_nested=["project"])

    # noinspection PyMethodMayBeStatic
    def validate_data_use(self, value):
        validation = Draft7Validator(CHORD_DATA_USE_SCHEMA).is_valid(value)
        if not validation:
            raise serializers.ValidationError("Data use is not valid")
        return value

    # noinspection PyMethodMayBeStatic
    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters")
        return value.strip()

    class Meta:
        model = Project
        fields = '__all__'


class TableOwnershipSerializer(GenericSerializer):
    class Meta:
        model = TableOwnership
        fields = '__all__'
