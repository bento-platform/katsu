from django.conf import settings
from bento_lib.discovery import DiscoveryConfig
from chord_metadata_service.restapi.schema_utils import sub_schema_uri

__all__ = ["discovery_base_uri", "DISCOVERY_SCHEMA"]

discovery_base_uri = sub_schema_uri(settings.SCHEMAS_BASE_URL, "discovery")

# A JSON schema export of the bento_lib DiscoveryConfig Pydantic model with an ID consistent with other Katsu schemas.
DISCOVERY_SCHEMA = {**DiscoveryConfig.model_json_schema(), "$id": discovery_base_uri}
