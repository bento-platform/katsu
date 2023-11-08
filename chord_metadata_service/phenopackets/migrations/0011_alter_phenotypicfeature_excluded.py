# Generated by Django 4.2.7 on 2023-11-08 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phenopackets', '0010_alter_biosample_diagnostic_markers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phenotypicfeature',
            name='excluded',
            field=models.BooleanField(default=False, help_text='Whether the feature is present (false) or absent (true, feature is excluded); default false.'),
        ),
    ]
