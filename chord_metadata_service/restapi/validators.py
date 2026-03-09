from rest_framework import serializers
from jsonschema import Draft7Validator, FormatChecker
from .schema_ref import SchemaRefs


__all__ = [
    "JsonSchemaValidator",
    "age_or_age_range_validator",
    "ontology_validator",
    "ontology_list_validator",
    "base_extra_properties_validator",
]


class JsonSchemaValidator:
    """Custom class based validator to validate against Json schema for JSONField"""

    def __init__(self, schema: dict = None, schema_ref: SchemaRefs | str = None, formats=None, registry=None):
        """
        Validators should be constructed from a `SchemaRefs` enum value.
        DeprecationWarning!: Construction from full `schema` is supported to ensure that the method is backwards
            compatible and allows older migrations to be made.
        """
        if (not schema and not schema_ref) or (schema and schema_ref):
            raise ValueError("Must provide a schema OR a schema_ref argument. Preferably a schema_ref.")
        elif schema:
            # Initialization via `schema` kept for backward compatibility for older migrations!
            # Instead, init via `schema_ref` argument.
            self.schema = schema
        elif schema_ref:
            schema_ref = SchemaRefs[schema_ref] if isinstance(schema_ref, str) else schema_ref
            self.schema_name, self.schema = schema_ref.name, schema_ref.value

        self.formats = formats
        self.validator_args = {
            "schema": self.schema,
            "format_checker": FormatChecker(formats=self.formats),
        }
        if registry:
            self.validator_args["registry"] = registry
        self.validator = Draft7Validator(**self.validator_args)

    def __call__(self, value):
        if not self.validator.is_valid(value):
            raise serializers.ValidationError("Not valid JSON schema for this field.")
        return value

    def __eq__(self, other):
        return self.schema == other.schema

    def deconstruct(self):
        if hasattr(self, "schema_name"):
            # deconstruct using schema reference
            return (
                "chord_metadata_service.restapi.validators.JsonSchemaValidator",
                [],
                {"schema_ref": self.schema_name, "formats": self.formats},
            )

        # Deconstruct via `schema` kept for backward compatibility for older migrations ONLY.
        return (
            "chord_metadata_service.restapi.validators.JsonSchemaValidator",
            [self.schema],
            {"formats": self.formats},
        )


age_or_age_range_validator = JsonSchemaValidator(schema_ref=SchemaRefs.AGE_OR_AGE_RANGE)
ontology_validator = JsonSchemaValidator(schema_ref=SchemaRefs.ONTOLOGY_CLASS)
ontology_list_validator = JsonSchemaValidator(schema_ref=SchemaRefs.ONTOLOGY_CLASS_LIST)
base_extra_properties_validator = JsonSchemaValidator(schema_ref=SchemaRefs.EXTRA_PROPERTIES_SCHEMA)
