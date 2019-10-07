# Generated by Django 2.2.6 on 2019-10-07 16:02

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0016_auto_20191004_1430'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('project_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True)),
                ('data_use', django.contrib.postgres.fields.jsonb.JSONField()),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('dataset_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patients.Project')),
            ],
        ),
        migrations.AddField(
            model_name='phenopacket',
            name='dataset',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='patients.Dataset'),
        ),
    ]
