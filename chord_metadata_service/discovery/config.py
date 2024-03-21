import json
import os
from django.conf import settings

from .types import DiscoveryConfig

__all__ = ["discovery_config"]


def parse_discovery_config() -> DiscoveryConfig:
    config_path = os.path.join(settings.BASE_DIR, "config.json")
    if not os.path.isfile(config_path):
        return None

    with open(config_path, "r") as config_file:
        if config_data := json.load(config_file):
            return config_data
        return None


# Discovery config singleton
discovery_config: DiscoveryConfig = parse_discovery_config()
