# Generated by Django 4.2.1 on 2023-06-13 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chord', '0005_v3_0_0'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tableownership',
            name='dataset',
        ),
    ]
