# Generated by Django 4.2 on 2023-05-11 19:39

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('chord', '0004_v2_14_0'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectJsonSchema',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=200, primary_key=True, serialize=False)),
                ('required', models.BooleanField(default=False, help_text='Determines if the extra_properties field is required or not.')),
                ('json_schema', models.JSONField()),
                ('schema_type', models.CharField(choices=[('PHENOPACKET', 'Phenopacket'), ('BIOSAMPLE', 'Biosample'), ('INDIVIDUAL', 'Individual')], max_length=200)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_schemas', to='chord.project')),
            ],
        ),
        migrations.AddConstraint(
            model_name='projectjsonschema',
            constraint=models.UniqueConstraint(fields=('project', 'schema_type'), name='unique_project_schema'),
        ),
    ]
