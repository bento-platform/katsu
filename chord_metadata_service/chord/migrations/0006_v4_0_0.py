# Generated by Django 4.2.1 on 2023-08-22 17:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phenopackets', '0005_v4_0_0'),
        ('chord', '0005_v3_0_0'),
        ('mcode', '0006_v4_0_0'),
        ('experiments', '0007_v4_0_0'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tableownership',
            name='dataset',
        ),
        migrations.DeleteModel(
            name='Table',
        ),
        migrations.DeleteModel(
            name='TableOwnership',
        ),
    ]
