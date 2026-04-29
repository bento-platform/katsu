# Generated manually 2026-04-29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chord', '0015_remove_datasetv2_language_remove_datasetv2_pk_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasetv2',
            name='release_date',
            field=models.DateField(db_index=True, null=True, blank=True),
        ),
    ]
