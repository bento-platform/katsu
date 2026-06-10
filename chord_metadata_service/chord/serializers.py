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

from .models import Project, ProjectJsonSchema, Dataset, DatasetTranslation
from .utils import get_censored_counts_for_serializer

__all__ = [
    "ProjectSerializer",
    "ProjectJsonSchemaSerializer",
    "DatasetSerializer",
    "DatasetTranslationSerializer",
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


class DatasetSerializer(PydanticJSONBSerializer):
    schema_class = KatsuDatasetModel

    counts_by_entity = serializers.SerializerMethodField()

    class Meta:
        model = Dataset
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
                    translation = DatasetTranslation.objects.get(
                        dataset_id=instance.identifier, language=language
                    )
                except DatasetTranslation.DoesNotExist:
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
        data['translations'] = [t.language for t in instance.translations.all()]
        return data

    def get_counts_by_entity(self, obj):
        request = self.context.get("request")
        if not request or request.method not in ("GET", "HEAD", "OPTIONS"):
            return {}
        scope = ValidatedDiscoveryScope(obj.project, obj)
        return get_censored_counts_for_serializer(request, scope, logger)

    def _sync_schema_resources(self, instance: Dataset) -> None:
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


def _roles_for(contact) -> list:
    return getattr(contact, "roles", []) or []


_IMMUTABLE_FIELDS = frozenset({"version", "release_date", "last_modified", "study_status", "study_context",
                               "discovery", "pcgl_dac_id"})


def _check_translation_constraints(translation: ProjectScopedDatasetModel):
    """
    Validate three invariants that translations must respect vs. the canonical (English) dataset:
      1. roles on primary_contact and each stakeholder cannot change.
      2. no field present in canonical may be removed (set to None) in a translation;
         for list fields, lengths must also match exactly.
      3. non-translatable fields (version, release_date, last_modified, study_status,
         study_context, discovery, dac_id) must equal the canonical value exactly if
         provided; omitting them is allowed.
    """
    try:
        dataset = Dataset.objects.get(identifier=str(translation.identifier))
    except Dataset.DoesNotExist:
        return

    canonical = dataset.to_schema()
    errors = {}

    # Rule 1: roles immutable
    c_roles = _roles_for(canonical.primary_contact)
    t_roles = _roles_for(translation.primary_contact)
    if c_roles != t_roles:
        errors["primary_contact"] = ["Roles cannot change in a translation."]

    c_stakeholders = canonical.stakeholders or []
    t_stakeholders = translation.stakeholders or []
    for i, (c_sh, t_sh) in enumerate(zip(c_stakeholders, t_stakeholders)):
        if _roles_for(c_sh) != _roles_for(t_sh):
            errors.setdefault("stakeholders", []).append(
                f"Stakeholder at index {i}: roles cannot change in a translation."
            )

    # Rule 2: translations cannot remove or add data to any shared field
    # (immutable fields are exempt — omitting them is always allowed)
    shared_fields = canonical.model_fields.keys() & translation.model_fields.keys()
    for field in shared_fields:
        if field in _IMMUTABLE_FIELDS:
            continue

        c_val = getattr(canonical, field, None)
        t_val = getattr(translation, field, None)

        if c_val is None or (isinstance(c_val, list) and len(c_val) == 0):
            continue  # canonical has nothing here; translation free to omit too

        if t_val is None:
            errors[field] = [f"Translation cannot remove '{field}' (present in canonical)."]
        elif isinstance(c_val, list):
            t_len = len(t_val) if isinstance(t_val, list) else 0
            if t_len != len(c_val):
                errors[field] = [
                    f"Translation must have the same number of items in '{field}' as canonical "
                    f"(canonical has {len(c_val)}, translation has {t_len})."
                ]

    # Rule 3: if an immutable field is present in the translation it must match canonical exactly
    for field in _IMMUTABLE_FIELDS:
        c_val = getattr(canonical, field, None)
        t_val = getattr(translation, field, None)
        if t_val is not None and t_val != c_val:
            errors[field] = [
                f"'{field}' cannot change in a translation "
                f"(expected {c_val!r}, got {t_val!r})."
            ]

    if errors:
        raise serializers.ValidationError(errors)


class DatasetTranslationSerializer(PydanticJSONBSerializer):
    schema_class = ProjectScopedDatasetModel

    class Meta:
        model = DatasetTranslation
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at', 'dataset']

    def _resolve_dataset_id(self) -> str | None:
        if self.instance is not None:
            return str(self.instance.dataset_id)
        view = self.context.get("view")
        if view is not None:
            return view.kwargs.get("identifier")
        return None

    def to_internal_value(self, data):
        if "discovery" in data:
            raise serializers.ValidationError({"discovery": ["Translations cannot include a discovery configuration."]})
        dataset_id = self._resolve_dataset_id()
        if dataset_id is not None:
            try:
                dataset = Dataset.objects.get(identifier=dataset_id)
                data = {**data, "identifier": dataset_id, "project": str(dataset.project_id)}
            except Dataset.DoesNotExist:
                pass  # view handles 404
        result = super().to_internal_value(data)
        _check_translation_constraints(self._validated_schema)
        return result

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
    datasets = DatasetSerializer(read_only=True, many=True)
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
