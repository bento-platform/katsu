from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.test import SimpleTestCase
from pydantic import BaseModel
from unittest.mock import MagicMock

from chord_metadata_service.common.base_pydantic_jsonb import AbstractPydanticJSONBModel, PydanticJSONBSerializer


class _SimpleSchema(BaseModel):
    name: str = ""


class AbstractPydanticJSONBModelTest(SimpleTestCase):
    def test_to_schema_raises_when_schema_class_is_none(self):
        inst = MagicMock(spec=AbstractPydanticJSONBModel)
        inst.COLUMN_FIELDS = set()
        inst.SCHEMA_CLASS = None
        inst.JSONB_FIELD = "other_data"
        inst.other_data = {}
        with self.assertRaises(NotImplementedError):
            AbstractPydanticJSONBModel.to_schema(inst)

    def test_to_schema_skips_nonexistent_column_field(self):
        inst = MagicMock(spec=AbstractPydanticJSONBModel)
        inst.COLUMN_FIELDS = {"ghost_field"}
        inst.SCHEMA_CLASS = _SimpleSchema
        inst.JSONB_FIELD = "other_data"
        inst.other_data = {}
        inst._meta.get_field.side_effect = FieldDoesNotExist()
        result = AbstractPydanticJSONBModel.to_schema(inst)
        self.assertIsInstance(result, _SimpleSchema)


class PydanticJSONBSerializerTest(SimpleTestCase):
    def test_get_schema_class_raises_when_not_configured(self):
        inst = MagicMock(spec=PydanticJSONBSerializer)
        inst.schema_class = None
        inst.Meta.model.SCHEMA_CLASS = None
        with self.assertRaises(ImproperlyConfigured):
            PydanticJSONBSerializer.get_schema_class(inst)
