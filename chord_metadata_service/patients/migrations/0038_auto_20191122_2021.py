# Generated by Django 2.2.6 on 2019-11-22 20:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0037_auto_20191028_1740'),
    ]

    operations = [
        migrations.RenameField(
            model_name='individual',
            old_name='individual_id',
            new_name='id',
        ),
    ]
