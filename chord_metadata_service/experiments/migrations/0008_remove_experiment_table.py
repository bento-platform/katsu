# Generated by Django 4.2.1 on 2023-06-12 19:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0007_experiment_dataset'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='experiment',
            name='table',
        ),
    ]
