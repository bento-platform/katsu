import json
from django.core.management.base import BaseCommand
from datetime import datetime
from tabulate import tabulate

from chord_metadata_service.chord.views_search import chord_table_search


class Command(BaseCommand):
    help = """
        Executes a bento-lib-query-style search on a table.
        Arguments: "table-id" "query"
    """

    def add_arguments(self, parser):
        parser.add_argument("table", action="store", type=str, help="Table to search on.")
        parser.add_argument("query", action="store", type=str, help="Query to execute.")

    def handle(self, *args, **options):
        start = datetime.now()
        query = json.loads(options["query"].strip())
        print("Executing query:", query)
        print(tabulate(chord_table_search(query, options["table"].strip(), start, internal=True)[0]))
