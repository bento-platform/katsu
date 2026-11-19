import chord_metadata_service.restapi.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phenopackets', '0021_phenopacket_links'),
    ]

    operations = [
        migrations.AddField(
            model_name='biosample',
            name='links',
            field=models.JSONField(blank=True, help_text='A list of links to external web resources related to the biosample.', null=True, validators=[chord_metadata_service.restapi.validators.JsonSchemaValidator(formats=['uri'], schema_ref='VALIDATION_LINK_SCHEMA')]),
        ),
    ]
