import chord_metadata_service.restapi.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0017_experiment_dataset_v2'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='links',
            field=models.JSONField(blank=True, help_text='A list of links to external web resources related to the experiment.', null=True, validators=[chord_metadata_service.restapi.validators.JsonSchemaValidator(formats=['uri'], schema_ref='VALIDATION_LINK_SCHEMA')]),
        ),
        migrations.AddField(
            model_name='experimentresult',
            name='links',
            field=models.JSONField(blank=True, help_text='A list of links to external web resources related to the experiment result.', null=True, validators=[chord_metadata_service.restapi.validators.JsonSchemaValidator(formats=['uri'], schema_ref='VALIDATION_LINK_SCHEMA')]),
        ),
    ]
