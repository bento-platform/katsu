from django.core.management.base import BaseCommand
from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT, DATA_TYPE_PHENOPACKET
from chord_metadata_service.chord.ingest.constants import DATA_TYPE_TO_INGESTION_FN


class Command(BaseCommand):
    help = """
        Ingests a JSON file into a Katsu/Bento dataset.
        Arguments: "dataset" "type" ./path/to/data.json
    """

    def add_arguments(self, parser):
        parser.add_argument("dataset", action="store", type=str, help="The dataset ID to ingest into")
        parser.add_argument("type", action="store", type=str, choices=[DATA_TYPE_EXPERIMENT, DATA_TYPE_PHENOPACKET],
                            help=f"The type of data to be ingested, {DATA_TYPE_PHENOPACKET} or {DATA_TYPE_EXPERIMENT}")
        parser.add_argument("data", action="store", type=str, help="JSON data file or DRS URI to ingest")

    def handle(self, *args, **options):
        DATA_TYPE_TO_INGESTION_FN[options["type"]]({"json_document": options["data"]}, options["dataset"])

        print("Ingested data successfully.")
