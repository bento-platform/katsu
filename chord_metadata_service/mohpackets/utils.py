import yaml
from django.core.cache import cache


def get_schema_version():
    schema_version = cache.get("schema_version")
    if schema_version is None:
        try:
            with open(
                "chord_metadata_service/mohpackets/docs/schema.yml", "r"
            ) as yaml_file:
                data = yaml.safe_load(yaml_file)
                schema_version = data["info"]["version"]
                # Cache the schema_version so we won't read it each time
                cache.set("schema_version", schema_version)
        except Exception as e:
            schema_version = None
    return schema_version
