# Generated by Django 4.2.6 on 2023-10-16 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phenopackets', '0008_alter_biosample_procedure_delete_procedure'),
    ]

    operations = [
        migrations.RenameField(
            model_name='phenotypicfeature',
            old_name='modifier',
            new_name='modifiers',
        ),
    ]
