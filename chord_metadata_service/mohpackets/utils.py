import logging
import re

import yaml
from django.core.cache import cache

logger = logging.getLogger(__name__)


def get_schema_url():
    """
    Retrieve the schema URL either from cached or by parsing a YAML file.
    It first checks if the URL is cached in "schema_url".
    If not cached, it reads the YAML file and extracts the URL from the "description".
    """

    schema_url = cache.get("schema_url")
    url_pattern = r"https://[^\s]+"  # get everything after https

    if schema_url is None:
        try:
            with open(
                "chord_metadata_service/mohpackets/docs/schema.yml", "r"
            ) as yaml_file:
                data = yaml.safe_load(yaml_file)
                desc_str = data["info"]["description"]
                schema_url = re.search(url_pattern, desc_str).group()
                # Cache the schema_version so we won't read it each time
                cache.set("schema_url", schema_url)
        except Exception as e:
            logger.debug(
                f"An error occurred while fetching the schema URL. Details: {str(e)}"
            )
            schema_url = None
    return schema_url
