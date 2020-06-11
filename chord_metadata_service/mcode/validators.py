from chord_metadata_service.restapi.validators import JsonSchemaValidator
from .schemas import *


quantity_validator = JsonSchemaValidator(schema=QUANTITY, formats=['uri'])
tumor_marker_data_value_validator = JsonSchemaValidator(schema=TUMOR_MARKER_DATA_VALUE)
complex_ontology_validator = JsonSchemaValidator(schema=COMPLEX_ONTOLOGY, formats=['uri'])
time_or_period_validator = JsonSchemaValidator(schema=TIME_OR_PERIOD, formats=['date-time'])
