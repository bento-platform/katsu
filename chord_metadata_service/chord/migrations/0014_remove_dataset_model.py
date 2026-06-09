import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chord", "0013_migrate_datasets_to_v2"),
        ("experiments", "0017_experiment_dataset_v2"),
        ("phenopackets", "0019_phenopacket_dataset_v2"),
    ]

    operations = [
        migrations.AlterField(
            model_name="datasetv2",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="datasets",
                to="chord.project",
            ),
        ),
        migrations.DeleteModel(
            name="Dataset",
        ),
    ]
