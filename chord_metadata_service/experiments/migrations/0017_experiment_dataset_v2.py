from django.db import migrations, models
import django.db.models.deletion


_DROP_EXPERIMENT_DATASET_FK = """
DO $$
DECLARE r RECORD;
BEGIN
  FOR r IN (
    SELECT tc.constraint_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    WHERE tc.table_name = 'experiments_experiment'
      AND tc.constraint_type = 'FOREIGN KEY'
      AND kcu.column_name = 'dataset_id'
  ) LOOP
    EXECUTE 'ALTER TABLE experiments_experiment DROP CONSTRAINT ' || quote_ident(r.constraint_name);
  END LOOP;
END $$;
"""

_ALTER_EXPERIMENT_DATASET_COL = """
ALTER TABLE experiments_experiment
    ALTER COLUMN dataset_id TYPE varchar(128)
    USING dataset_id::text;
"""

_ADD_EXPERIMENT_DATASET_FK = """
ALTER TABLE experiments_experiment
    ADD CONSTRAINT experiments_experiment_dataset_id_fk_datasetv2
    FOREIGN KEY (dataset_id) REFERENCES chord_datasetv2(identifier)
    DEFERRABLE INITIALLY DEFERRED;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("chord", "0012_datasetv2"),
        ("experiments", "0016_v13_2_0"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="experiment",
                    name="dataset",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="experiments",
                        to="chord.datasetv2",
                    ),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql=_DROP_EXPERIMENT_DATASET_FK
                        + _ALTER_EXPERIMENT_DATASET_COL
                        + _ADD_EXPERIMENT_DATASET_FK,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
        ),
    ]
