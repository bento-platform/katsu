# Generated by Django 4.2.6 on 2023-10-13 19:41

from django.db import migrations, models


def migrate_procedure_json(apps, schema_editor):
    """
    Forward data migration for Biosample.procedure.
    Migrating from a Django Model to a JSON field.
    """
    Biosample = apps.get_model("phenopackets", "Biosample")
    for bios in Biosample.objects.all():
        procedure = bios.procedure

        procedure_json = {"code": procedure.code}
        if procedure.body_site:
            procedure_json["body_site"] = procedure.body_site
        if procedure.performed:
            procedure_json["performed"] = procedure.performed
        
        procedure.procedure_json = procedure_json
        procedure.save()

class Migration(migrations.Migration):

    dependencies = [
        ('phenopackets', '0007_remove_phenopacket_table'),
    ]

    operations = [
        # Temporary field to store migration data, Django cannot auto AlterField Biosample.procedure from FK to JSON field
        migrations.AddField(
            model_name='biosample',
            name='procedure_json',
            field=models.JSONField(blank=True, help_text='A description of a clinical procedure performed on a subject in order to extract a biosample.', null=True),
        ),
        # Migrate from model to JSON field
        migrations.RunPython(migrate_procedure_json),
        # Remove FK field, rename JSON one
        migrations.RemoveField(
            model_name="biosample", 
            name="procedure",
        ),
        migrations.RenameField(
            model_name='biosample', 
            old_name='procedure_json', 
            new_name='procedure',
        ),
        migrations.DeleteModel(
            name='Procedure',
        ),
    ]
