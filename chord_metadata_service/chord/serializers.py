import uuid
from pydantic import ValidationError as PydValidationError
from bento_lib.discovery import DiscoveryConfig
from bento_lib.provenance.dataset import ProjectScopedDatasetModel
from chord_metadata_service.chord.dataset_schema import KatsuDatasetModel
from chord_metadata_service.common.base_pydantic_jsonb import PydanticJSONBSerializer
from chord_metadata_service.resources.ingest import ingest_resource
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope
from chord_metadata_service.logger import logger
from chord_metadata_service.restapi.serializers import GenericSerializer
from rest_framework import serializers

from .models import Project, ProjectJsonSchema, DatasetV2, DatasetV2Translation
from .utils import get_censored_counts_for_serializer

__all__ = [
    "ProjectSerializer",
    "ProjectJsonSchemaSerializer",
    "DatasetV2Serializer",
    "DatasetV2TranslationSerializer",
]


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


class DatasetV2Serializer(PydanticJSONBSerializer):
    schema_class = KatsuDatasetModel

    counts_by_entity = serializers.SerializerMethodField()

    class Meta:
        model = DatasetV2
        exclude = ['additional_resources']
        read_only_fields = ['created_at', 'updated_at']

    def to_internal_value(self, data):
        if self.instance:
            data = {**data, "identifier": str(self.instance.identifier)}
        elif not data.get("identifier"):
            data = {**data, "identifier": str(uuid.uuid4())}
        return super().to_internal_value(data)

    def to_representation(self, instance):
        language = self.context.get("language", "en")

        if language != "en":
            prefetched = getattr(instance, "prefetched_translations", None)
            if prefetched is not None:
                translation = prefetched[0] if prefetched else None
            else:
                try:
                    translation = DatasetV2Translation.objects.get(
                        dataset_id=instance.identifier, language=language
                    )
                except DatasetV2Translation.DoesNotExist:
                    translation = None

            if translation is not None:
                data = translation.to_schema().model_dump(mode="json")
                self.context["_content_language"] = language
            else:
                data = super().to_representation(instance)
                self.context.setdefault("_content_language", "en")
        else:
            data = super().to_representation(instance)
            self.context.setdefault("_content_language", "en")

        data['created_at'] = instance.created_at
        data['updated_at'] = instance.updated_at
        data['counts_by_entity'] = self.get_counts_by_entity(instance)
        return data

    def get_counts_by_entity(self, obj):
        request = self.context.get("request")
        if not request or request.method not in ("GET", "HEAD", "OPTIONS"):
            return {}
        scope = ValidatedDiscoveryScope(obj.project, obj)
        return get_censored_counts_for_serializer(request, scope, logger)

    def _sync_schema_resources(self, instance: DatasetV2) -> None:
        schema: KatsuDatasetModel = self._validated_schema
        if not schema.resources:
            return
        for vr in schema.resources:
            r = ingest_resource(
                {
                    "namespace_prefix": vr.namespace_prefix,
                    "version": vr.version,
                    "name": vr.name,
                    "url": str(vr.url),
                    "iri_prefix": str(vr.iri_prefix),
                },
                logger,
            )
            instance.additional_resources.add(r)

    def create(self, validated_data):
        instance = super().create(validated_data)
        self._sync_schema_resources(instance)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        self._sync_schema_resources(instance)
        return instance


class DatasetV2TranslationSerializer(PydanticJSONBSerializer):
    schema_class = ProjectScopedDatasetModel

    class Meta:
        model = DatasetV2Translation
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at', 'dataset']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_at'] = instance.created_at
        data['updated_at'] = instance.updated_at
        return data


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
    datasets = DatasetV2Serializer(read_only=True, many=True)
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
