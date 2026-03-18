from typing import Set, Type, override

from django.core.exceptions import ImproperlyConfigured
from django.db.models.options import Options
from pydantic import BaseModel, ValidationError as PydanticValidationError
from rest_framework import serializers
from rest_framework.settings import api_settings
from django.db import models


class PydanticJSONBModelMixin(models.Model):
    """
    Mixin for models that store some Pydantic fields in a JSONB column.

    Requires:
        - COLUMN_FIELDS: set of field names stored as actual columns
        - JSONB_FIELD: name of the JSONField (default: 'other_data')
        - SCHEMA_CLASS: the Pydantic model class
    """
    _meta: Options  # for pylance

    COLUMN_FIELDS: Set[str] = set()
    JSONB_FIELD: str = 'other_data'
    SCHEMA_CLASS: Type[BaseModel] | None = None

    class Meta:
        abstract = True

    @classmethod
    def from_schema(cls, schema: BaseModel, **extra_column_kwargs):
        data = schema.model_dump(exclude_unset=True, mode='json')

        # Translation to model fields (1 to 1 schema to column name match required)
        column_data = {}
        for k, v in data.items():
            if k not in cls.COLUMN_FIELDS or v is None:
                continue

            model_field = cls._meta.get_field(k)
            if model_field.is_relation:  # Handling Foreign Keys by providing ids
                column_data[f"{k}_id"] = v
            else:
                column_data[k] = v

        column_data.update(extra_column_kwargs)

        # Data to be put in JSONB_FIELD
        jsonb_data = {
            k: v for k, v in data.items()
            if k not in cls.COLUMN_FIELDS
        }
        instance = cls(**column_data, **{cls.JSONB_FIELD: jsonb_data})

        return instance

    def to_schema(self) -> BaseModel:
        data = {}
        for field in self.COLUMN_FIELDS:
            if not hasattr(self, field):
                continue
            model_field = self._meta.get_field(field)
            if model_field.is_relation:
                data[field] = getattr(self, f"{field}_id")
            else:
                data[field] = getattr(self, field)

        jsonb_data = getattr(self, self.JSONB_FIELD, {})
        data.update(jsonb_data)

        if self.SCHEMA_CLASS is None:
            raise NotImplementedError(f"{self.__class__.__name__} must define SCHEMA_CLASS")

        return self.SCHEMA_CLASS(**data)

    def update_from_schema(self, schema: BaseModel):
        data = schema.model_dump(exclude_unset=True, mode='json')
        for k, v in data.items():
            if k in self.COLUMN_FIELDS and k != 'id':
                model_field = self._meta.get_field(k)
                if model_field.is_relation:
                    setattr(self, f"{k}_id", v)
                else:
                    setattr(self, k, v)
        jsonb_data = {k: v for k, v in data.items() if k not in self.COLUMN_FIELDS}
        setattr(self, self.JSONB_FIELD, jsonb_data)


class PydanticJSONBSerializer(serializers.ModelSerializer):
    """
    Generic serializer mixin for models using PydanticJSONBMixin.

    Subclasses must define Meta.model (which should use PydanticJSONBMixin)
    and may set `schema_class` if it differs from model.SCHEMA_CLASS.
    """

    class Meta:
        model: type[PydanticJSONBModelMixin]
        fields: str | list[str]
        read_only_fields: list[str]

    schema_class: type[BaseModel] | None = None

    def get_schema_class(self) -> type[BaseModel]:
        cls = self.schema_class or self.Meta.model.SCHEMA_CLASS
        if cls is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} requires either `schema_class` or "
                f"`Meta.model.SCHEMA_CLASS` to be set."
            )
        return cls

    @override
    def to_internal_value(self, data):
        try:
            schema = self.get_schema_class().model_validate(data)
            self._validated_schema = schema
            return schema.model_dump(mode='json')
        except PydanticValidationError as e:
            drf_errors = {}
            for err in e.errors():
                loc = err.get("loc", ())
                field = str(loc[0]) if loc else api_settings.NON_FIELD_ERRORS_KEY
                drf_errors.setdefault(field, []).append(err["msg"])
            raise serializers.ValidationError(drf_errors)

    @override
    def to_representation(self, instance):
        schema = instance.to_schema()
        return schema.model_dump(mode='json')

    @override
    def create(self, _validated_data):
        instance = self.Meta.model.from_schema(self._validated_schema)
        instance.save()
        return instance

    @override
    def update(self, instance, _validated_data):
        instance.update_from_schema(self._validated_schema)
        instance.save()
        return instance
