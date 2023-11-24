import json
import logging
import re
from enum import Enum

from django.core.cache import cache

logger = logging.getLogger(__name__)


def get_schema_url():
    """
    Retrieve the schema URL either from cached or by parsing the first 10 lines of a JSON file.
    It first checks if the URL is cached in "schema_url".
    If not cached, it reads the first 6 lines of the JSON file and extracts the URL from the "description".
    """

    schema_url = cache.get("schema_url")
    url_pattern = r"https://[^\s]+"  # get everything after https

    if schema_url is None:
        try:
            with open(
                "chord_metadata_service/mohpackets/docs/schema.json", "r"
            ) as json_file:
                # Read the first 6 lines of the JSON file only
                # The line we are looking for is on the 6th
                first_6_lines = [next(json_file) for _ in range(6)]
                first_6_lines.extend(["}", "}"])  # make valid JSON
                # Concatenate the lines to form a JSON string
                json_str = "".join(first_6_lines)
                data = json.loads(json_str)
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


def list_to_enum(enum_name, value_list):
    enum_dict = {}
    for item in value_list:
        enum_member_name = item.upper().replace(" ", "_")
        enum_dict[enum_member_name] = item
    return Enum(enum_name, enum_dict)
