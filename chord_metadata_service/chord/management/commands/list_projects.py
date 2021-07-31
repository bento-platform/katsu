from django.core.management.base import BaseCommand
from tabulate import tabulate

from chord_metadata_service.chord.models import Project


class Command(BaseCommand):
    help = """
        Creates a Katsu/Bento project in the database.
        Arguments: "title" "description"
    """

    def handle(self, *args, **options):
        print(tabulate(Project.objects.values(), headers="keys"))
