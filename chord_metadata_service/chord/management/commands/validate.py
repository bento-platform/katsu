import json

from django.core.management.base import BaseCommand
from chord_metadata_service.chord.ingest.constants import DATA_TYPE_TO_VALIDATOR_FN
from chord_metadata_service.chord.ingest.utils import workflow_file_output_to_path, get_output_or_raise
from humps import decamelize


class Command(BaseCommand):

    help = """
        Validates a JSON file against json-schemas (Phenopackets V2)
    """

    def add_arguments(self, parser):
        parser.add_argument("data", action="store", type=str, help="JSON data file or DRS URI to validate.")
        parser.add_argument("type", action="store", type=str, help="phenopacket or experiment")

    def handle(self, *args, **options):
        data_type = options["type"].lower().strip()
        data = {
            "json_document": options["data"]
        }
        with workflow_file_output_to_path(get_output_or_raise(data, "json_document")) as doc_path:
            with open(doc_path, "r") as json_file:
                json_data = json.load(json_file)
        # Converts camelCase keys to snake_case
        json_data = decamelize(json_data)

        if isinstance(json_data, list):
            for pheno_item in json_data:
                print(f"Subject id: {pheno_item['subject']['id']}")
                DATA_TYPE_TO_VALIDATOR_FN[data_type](pheno_item)
        else:
            DATA_TYPE_TO_VALIDATOR_FN[data_type](json_data)
