from django.db import migrations


def backfill_discovery(apps, schema_editor):
    DatasetV2 = apps.get_model("chord", "DatasetV2")
    to_update = []
    for dataset in DatasetV2.objects.all():
        if isinstance(dataset.data, dict) and "discovery" in dataset.data:
            dataset.discovery = dataset.data.pop("discovery")
            to_update.append(dataset)
    if to_update:
        DatasetV2.objects.bulk_update(to_update, ["discovery", "data"])


class Migration(migrations.Migration):

    dependencies = [
        ("chord", "0019_datasetv2_discovery_column"),
    ]

    operations = [
        migrations.RunPython(backfill_discovery, migrations.RunPython.noop),
    ]
