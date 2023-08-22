# Generated by Django 4.2.1 on 2023-08-22 17:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('phenopackets', '0005_phenopacket_dataset'), ('phenopackets', '0006_phenopacket_unique_pheno_dataset'), ('phenopackets', '0007_remove_phenopacket_table')]

    dependencies = [
        ('phenopackets', '0004_v2_17_0'),
        ('chord', '0005_v3_0_0'),
    ]

    operations = [
        migrations.AddField(
            model_name='phenopacket',
            name='dataset',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='chord.dataset'),
        ),
        migrations.AddConstraint(
            model_name='phenopacket',
            constraint=models.UniqueConstraint(fields=('id', 'dataset_id'), name='unique_pheno_dataset'),
        ),
        migrations.RemoveField(
            model_name='phenopacket',
            name='table',
        ),
    ]
