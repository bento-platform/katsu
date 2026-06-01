from django.core.management import call_command
from django.db import migrations


def migrate_datasets_to_v2(apps, schema_editor):
    call_command("migrate_datasets_to_v2")


class Migration(migrations.Migration):

    dependencies = [
        ("chord", "0012_datasetv2"),
    ]

    operations = [
        migrations.RunPython(migrate_datasets_to_v2, migrations.RunPython.noop),
    ]
