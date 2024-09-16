import json
from typing import Any
from django.core.management.base import BaseCommand, CommandParser

from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT, DATA_TYPE_PHENOPACKET
from chord_metadata_service.discovery.schemas import DISCOVERY_SCHEMA
from chord_metadata_service.experiments.schemas import EXPERIMENT_SCHEMA
from chord_metadata_service.phenopackets.schemas import PHENOPACKET_SCHEMA

NAME_TO_SCHEMA: dict[str, object] = {
  DATA_TYPE_PHENOPACKET: PHENOPACKET_SCHEMA,
  DATA_TYPE_EXPERIMENT: EXPERIMENT_SCHEMA,
  "discovery": DISCOVERY_SCHEMA,
}


class Command(BaseCommand):
    help = """
        Compiles and returns a JSON-schema in a single JSON file for artifact.
        Use in GitHub Actions in order to publish usable schemas on releases.
    """

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("schema", action="store", type=str, choices=NAME_TO_SCHEMA.keys())

    def handle(self, *args: Any, **options: Any) -> str | None:
        schema = NAME_TO_SCHEMA[options["schema"]]
        self.stdout.write(json.dumps(schema))
