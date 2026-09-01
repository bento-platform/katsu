from chord_metadata_service.phenopackets.schemas import VRS_REF_REGISTRY
from chord_metadata_service.restapi.schema_ref import SchemaRefs
from chord_metadata_service.restapi.validators import JsonSchemaValidator

ALL = ["vrs_variation_validator"]

# VRS Variations are abstract and self referencing, thus cannot be expressed without a json-schema registry
# Uses the VRS registry to dynamically resolve/validate concrete Variation classes
vrs_variation_validator = JsonSchemaValidator(schema_ref=SchemaRefs.VRS_VARIATION_SCHEMA, registry=VRS_REF_REGISTRY)
