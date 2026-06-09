from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("chord", "0014_remove_dataset_model"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="DatasetV2",
            new_name="Dataset",
        ),
        migrations.RenameModel(
            old_name="DatasetV2Translation",
            new_name="DatasetTranslation",
        ),
    ]
