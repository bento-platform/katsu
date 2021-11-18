from django.core.management.base import BaseCommand
from tabulate import tabulate

from chord_metadata_service.chord.models import Dataset, Table


class Command(BaseCommand):
    help = """
        Lists all tables that belong to a particular dataset.
        Arguments: "dataset-id"
    """

    def add_arguments(self, parser):
        parser.add_argument("dataset", action="store", type=str, help="Dataset identifier to list tables of")

    def handle(self, *args, **options):
        print(tabulate(
            Table.objects.select_related("ownership_record").filter(
                ownership_record__dataset=Dataset.objects.get(identifier=options["dataset"].strip())
            ).values("ownership_record__table_id", "name", "data_type", "created", "updated"), headers="keys"))
