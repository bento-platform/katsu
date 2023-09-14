from django.db import migrations


def set_experiment_library_strategy(apps, _schema_editor):
    Experiment = apps.get_model("experiments", "Experiment")
    for exp in Experiment.objects.filter(library_strategy="WES"):
        exp.library_strategy = "WXS"
        exp.save()

class Migration(migrations.Migration):
    dependencies = [
        ('experiments', '0007_v4_0_0'),
    ]

    operations = [
        migrations.RunPython(set_experiment_library_strategy)
    ]
