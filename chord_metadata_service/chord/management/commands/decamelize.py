import json
from django.core.management.base import BaseCommand
from humps import decamelize


class Command(BaseCommand):

    help = "Converts the keys of a json document from camelCase to snake_case"

    def add_arguments(self, parser):
        parser.add_argument("data", action="store", type=str, help="JSON data file or DRS URI to validate.")

    def handle(self, *args, **options):
        data = options["data"]

        with open(data, "r") as json_file:
            json_data = json.load(json_file)

        json_data = decamelize(json_data)

        with open(data, "w") as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=4)

        print(f"Decamelized file: {data}")
