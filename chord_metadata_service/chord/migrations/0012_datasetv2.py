import uuid

import chord_metadata_service.chord.models
import django.db.models.deletion
from django.db import migrations, models


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
        ("chord", "0011_v13_1_0"),
        ("resources", "0002_v2_14_0"),
    ]

    operations = [
        migrations.CreateModel(
            name="DatasetV2",
            fields=[
                (
                    "identifier",
                    models.CharField(
                        blank=True,
                        default=uuid.uuid4,
                        help_text="If from PCGL, inherit. Otherwise created in Katsu.",
                        max_length=128,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=512)),
                ("release_date", models.DateField(blank=True, db_index=True, null=True)),
                ("last_modified", models.DateField(blank=True, db_index=True, null=True)),
                (
                    "data",
                    models.JSONField(help_text="Full DatasetModel payload validated by Pydantic before saving."),
                ),
                (
                    "discovery",
                    chord_metadata_service.chord.models.DiscoveryJSONField(
                        blank=True,
                        help_text="Dataset-level discovery configuration.",
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dv2",
                        to="chord.project",
                    ),
                ),
                (
                    "additional_resources",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Resource objects linked to this dataset that aren't specified by a phenopacket.",
                        to="resources.resource",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="DatasetV2Translation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("language", models.CharField(db_index=True, max_length=8)),
                (
                    "data",
                    models.JSONField(help_text="Full ProjectScopedDatasetModel payload for this language."),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "dataset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="chord.datasetv2",
                    ),
                ),
            ],
            options={
                "unique_together": {("dataset", "language")},
            },
        ),
        migrations.RunPython(backfill_discovery, migrations.RunPython.noop),
    ]
