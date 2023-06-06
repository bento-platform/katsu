# Generated by Django 4.2.1 on 2023-06-06 15:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chord', '0005_v3_0_0'),
        ('experiments', '0006_v2_14_0'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='dataset',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='chord.dataset'),
        ),
    ]
