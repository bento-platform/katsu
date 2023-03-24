from chord_metadata_service.phenopackets.schemas import PHENOPACKET_REF_RESOLVER, VRS_VARIATION_SCHEMA
from chord_metadata_service.restapi.validators import JsonSchemaValidator

ALL = [
    "vrs_variation_validator"
]

# VRS Variations are abstract and self referencing, thus cannot be expressed without a json-schema def resolver
# Uses jsonschema.RefResolver to dynamically resolve/validate concrete Variation classes
vrs_variation_validator = JsonSchemaValidator(VRS_VARIATION_SCHEMA, resolver=PHENOPACKET_REF_RESOLVER)
