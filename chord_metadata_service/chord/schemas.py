# e.g. PATCH
# {
#   "field_links": [
#     {
#       "name": "subject IDs",
#       "links": {"phenopacket": ["subject", "id"], "variant": ["sample_id"]}
#     }
#   ]
# }


FIELD_LINKS_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 3},
            "links": {
                "type": "object",
                "propertyNames": {
                    "pattern": r"^\S+$"  # TODO: synchronize pattern
                },
                "minProperties": 2,
                "additionalProperties": {  # Field specification, array format; e.g. ["biosamples", "[item]", "id"]
                    "type": "array",
                    "items": {"type": "string", "minLength": 1}
                }
            }
        },
        "required": ["name", "links"],
        "additionalProperties": False
    }
}
