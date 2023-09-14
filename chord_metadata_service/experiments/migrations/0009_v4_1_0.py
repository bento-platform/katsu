from typing import List, Tuple
from django.db import migrations

LIB_STRATEGY_CONVERSIONS: List[Tuple[str, str]] = [
    # Convert WES -> WXS ...
    ("WES", "WXS"),
    ("Other", "OTHER"),
]

LIB_SELECTION_CONVERIONS: List[Tuple[str, str]] = [
    ("Random", "RANDOM"),
    ("Random PCR", "RANDOM PCR"),
    ("Exome capture", "other"), # 'Exome capture' no longer supported
    ("Other", "other"),
]

def set_experiment_library(apps, _schema_editor):
    Experiment = apps.get_model("experiments", "Experiment")
    for (old_val, new_val) in LIB_STRATEGY_CONVERSIONS:
        # Modify library_strategy if necessary
        for exp in Experiment.objects.filter(library_strategy=old_val):
            exp.library_strategy = new_val
            exp.save()
    
    for (old_val, new_val) in LIB_SELECTION_CONVERIONS:
        # Modify library_selection if necessary
        for exp in Experiment.objects.filter(library_selection=old_val):
            exp.library_selection = new_val
            exp.save()

class Migration(migrations.Migration):
    dependencies = [
        ('experiments', '0007_v4_0_0'),
    ]

    operations = [
        migrations.RunPython(set_experiment_library)
    ]
