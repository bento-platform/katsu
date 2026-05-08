from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chord", "0017_alter_datasetv2_last_modified_optional"),
        ("resources", "0002_v2_14_0"),
    ]

    operations = [
        migrations.AddField(
            model_name="datasetv2",
            name="additional_resources",
            field=models.ManyToManyField(
                blank=True,
                help_text="Resource objects linked to this dataset that aren't specified by a phenopacket.",
                to="resources.resource",
            ),
        ),
    ]
