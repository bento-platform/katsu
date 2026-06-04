from django.db import migrations


class Migration(migrations.Migration):
    """
    Data migration from Dataset → DatasetV2 was a one-time operation already applied to all
    existing deployments. On fresh installs there is no Dataset data to migrate. Safe no-op.
    """

    dependencies = [
        ("chord", "0012_datasetv2"),
    ]

    operations = []
