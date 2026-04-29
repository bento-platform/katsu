# Generated manually 2026-04-29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chord', '0016_alter_datasetv2_release_date_optional'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasetv2',
            name='last_modified',
            field=models.DateField(db_index=True, null=True, blank=True),
        ),
    ]
