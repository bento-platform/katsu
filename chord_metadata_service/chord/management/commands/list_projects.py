from django.core.management.base import BaseCommand
from tabulate import tabulate

from chord_metadata_service.chord.models import Project


class Command(BaseCommand):
    help = """
        Lists all projects in the database.
    """

    def handle(self, *args, **options):
        print(tabulate(Project.objects.values(), headers="keys"))
