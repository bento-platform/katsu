from bento_lib.discovery import DiscoveryConfig
from bento_lib.schemas.bento import BENTO_DATA_USE_SCHEMA
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope
from chord_metadata_service.logger import logger
from chord_metadata_service.restapi.serializers import GenericSerializer
from jsonschema import Draft7Validator, Draft4Validator
from pydantic import ValidationError as PydValidationError
from rest_framework import serializers
from chord_metadata_service.restapi.dats_schemas import get_dats_schema_validator, CREATORS
from chord_metadata_service.restapi.utils import transform_keys

from .models import Project, Dataset, ProjectJsonSchema
from .schemas import LINKED_FIELD_SETS_SCHEMA
from .utils import get_censored_counts_for_serializer


__all__ = [
    "ProjectSerializer",
    "ProjectJsonSchemaSerializer",
    "DatasetSerializer",
]


BENTO_DATA_USE_SCHEMA_VALIDATOR = Draft7Validator(BENTO_DATA_USE_SCHEMA)
LINKED_FIELD_SETS_SCHEMA_VALIDATOR = Draft7Validator(LINKED_FIELD_SETS_SCHEMA)


class DiscoveryConfigField(serializers.Field):
    """
    Custom field serializer/deserializer for the DiscoveryConfig Pydantic model, used as the value for discovery fields
    on the Project/Dataset models.
    """

    def to_representation(self, value):
        return value.model_dump(mode="json")

    def to_internal_value(self, data):
        try:
            return DiscoveryConfig.model_validate(data)
        except PydValidationError as e:
            raise serializers.ValidationError(detail=str(e))


#############################################################
#                                                           #
#              Project Management  Serializers              #
#                                                           #
#############################################################


class DatasetSerializer(GenericSerializer):
    discovery = DiscoveryConfigField(required=False, allow_null=True)

    always_include = (
        "description",
        "contact_info",
        "linked_field_sets",
        "dats_file",
        "project",
        "discovery",
        "conditions_of_access",
        "counts",
    )

    counts = serializers.SerializerMethodField()

    # noinspection PyMethodMayBeStatic
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters")
        return value.strip()

    def validate_creators(self, value):
        if isinstance(value, list):
            transformed_value = [transform_keys(item) for item in value]
            validation = self.jsonschema_validation(transformed_value, CREATORS)
            if validation:
                raise serializers.ValidationError(validation)
        return value

    # noinspection PyMethodMayBeStatic
    def validate_data_use(self, value):
        validation = BENTO_DATA_USE_SCHEMA_VALIDATOR.is_valid(value)
        if not validation:
            raise serializers.ValidationError("Data use is not valid")
        return value

    # noinspection PyMethodMayBeStatic
    def validate_linked_field_sets(self, value):
        if errors := [str(error.message) for error in LINKED_FIELD_SETS_SCHEMA_VALIDATOR.iter_errors(value)]:
            # if we have >=1 error, raise serializers.ValidationError with them
            raise serializers.ValidationError(errors)
        return value

    def validate(self, data):
        """ Validate all fields against DATS schemas. """

        dataset_dats_fields = (
            "alternate_identifiers",
            "related_identifiers",
            "dates",
            "stored_in",
            "spatial_coverage",
            "types",
            "distributions",
            "dimensions",
            "primary_publications",
            "citations",
            "produced_by",
            "licenses",
            "acknowledges",
            "keywords",
        )

        errors = {}
        for field in dataset_dats_fields:
            if not data.get(field):
                continue

            if isinstance(data.get(field), list):
                for item in data.get(field):
                    call_validation = self.jsonschema_validation(
                        value=transform_keys(item),
                        schema_or_validator=get_dats_schema_validator(field),
                        field_name=field
                    )

                    if call_validation:
                        errors.update(call_validation)

            else:
                call_validation = self.jsonschema_validation(
                    value=data.get(field),
                    schema_or_validator=get_dats_schema_validator(field),
                    field_name=field
                )

                if call_validation:
                    errors.update(call_validation)
        if errors:
            raise serializers.ValidationError(errors)

        return data

    @staticmethod
    def jsonschema_validation(
        value, schema_or_validator: dict | Draft4Validator, field_name: str | None = None
    ) -> dict | None:
        """ Generic validation. Returns errors dict if validation is False, otherwise returns None. """

        if isinstance(schema_or_validator, dict):
            validator = Draft4Validator(schema_or_validator)
        else:  # Draft4Validator
            validator = schema_or_validator

        if errors := [str(error.message) for error in validator.iter_errors(value)]:
            # If we have >=1 error, return this error dictionary
            return {field_name: errors}

        return None

    def get_counts(self, obj):
        # TODO: with more datasets, refactor to batch queries (currently N queries for N datasets)
        request = self.context.get("request")
        scope = ValidatedDiscoveryScope(obj.project, obj)
        return get_censored_counts_for_serializer(request, scope, logger)

    class Meta:
        model = Dataset
        fields = '__all__'


class ProjectJsonSchemaSerializer(GenericSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = ProjectJsonSchema
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    # Don't inherit GenericSerializer to not pop empty fields

    always_include = (
        "title",
        "description",
        "discovery",
        "counts",
    )

    discovery = DiscoveryConfigField(required=False, allow_null=True)
    datasets = DatasetSerializer(read_only=True, many=True, exclude_when_nested=["project"])
    project_schemas = ProjectJsonSchemaSerializer(read_only=True, many=True)

    counts = serializers.SerializerMethodField()

    # noinspection PyMethodMayBeStatic
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters")
        return value.strip()

    def get_counts(self, obj):
        # TODO: with more projects, refactor to batch queries (currently N queries for N projects)
        request = self.context.get("request")
        scope = ValidatedDiscoveryScope(obj, None)
        return get_censored_counts_for_serializer(request, scope, logger)

    class Meta:
        model = Project
        fields = '__all__'
