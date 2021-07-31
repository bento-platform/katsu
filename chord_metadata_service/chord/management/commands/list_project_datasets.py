from django.core.management.base import BaseCommand
from tabulate import tabulate

from chord_metadata_service.chord.models import Project, Dataset


class Command(BaseCommand):
    help = """
        Lists all datasets that belong to a particular project.
        Arguments: "project-id"
    """

    def add_arguments(self, parser):
        parser.add_argument("project", action="store", type=str, help="Project identifier to list datasets of")

    def handle(self, *args, **options):
        print(tabulate([
            {k: str(v)[:100] for k, v in d.items() if k in {"identifier", "title", "description"}} for d in
            Dataset.objects.filter(project=Project.objects.get(identifier=options["project"].strip())).values()
        ], headers="keys"))
