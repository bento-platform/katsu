# Generated by Django 4.2.3 on 2023-09-08 17:08

import chord_metadata_service.mohpackets.models
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Donor',
            fields=[
                ('submitter_donor_id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('gender', models.CharField(blank=True, max_length=32, null=True)),
                ('sex_at_birth', models.CharField(blank=True, max_length=32, null=True)),
                ('is_deceased', models.BooleanField(blank=True, null=True)),
                ('lost_to_followup_after_clinical_event_identifier', models.CharField(blank=True, max_length=255, null=True)),
                ('lost_to_followup_reason', models.CharField(blank=True, max_length=255, null=True)),
                ('date_alive_after_lost_to_followup', models.CharField(blank=True, max_length=32, null=True)),
                ('cause_of_death', models.CharField(blank=True, max_length=255, null=True)),
                ('date_of_birth', models.CharField(blank=True, max_length=32, null=True)),
                ('date_of_death', models.CharField(blank=True, max_length=32, null=True)),
                ('primary_site', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=255, null=True), blank=True, null=True, size=None)),
            ],
            options={
                'ordering': ['submitter_donor_id'],
            },
        ),
        migrations.CreateModel(
            name='PrimaryDiagnosis',
            fields=[
                ('submitter_primary_diagnosis_id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('date_of_diagnosis', models.CharField(blank=True, max_length=32, null=True)),
                ('cancer_type_code', models.CharField(blank=True, max_length=64, null=True)),
                ('basis_of_diagnosis', models.CharField(blank=True, max_length=128, null=True)),
                ('laterality', models.CharField(blank=True, max_length=128, null=True)),
                ('lymph_nodes_examined_status', models.CharField(blank=True, max_length=128, null=True)),
                ('lymph_nodes_examined_method', models.CharField(blank=True, max_length=64, null=True)),
                ('number_lymph_nodes_positive', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('clinical_tumour_staging_system', models.CharField(blank=True, max_length=128, null=True)),
                ('clinical_t_category', models.CharField(blank=True, max_length=64, null=True)),
                ('clinical_n_category', models.CharField(blank=True, max_length=64, null=True)),
                ('clinical_m_category', models.CharField(blank=True, max_length=64, null=True)),
                ('clinical_stage_group', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'ordering': ['submitter_primary_diagnosis_id'],
            },
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('program_id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated', chord_metadata_service.mohpackets.models.AutoDateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['program_id'],
            },
        ),
        migrations.CreateModel(
            name='Treatment',
            fields=[
                ('submitter_treatment_id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('treatment_type', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), blank=True, null=True, size=None)),
                ('is_primary_treatment', models.CharField(blank=True, max_length=32, null=True)),
                ('line_of_treatment', models.IntegerField(blank=True, null=True)),
                ('treatment_start_date', models.CharField(blank=True, max_length=32, null=True)),
                ('treatment_end_date', models.CharField(blank=True, max_length=32, null=True)),
                ('treatment_setting', models.CharField(blank=True, max_length=128, null=True)),
                ('treatment_intent', models.CharField(blank=True, max_length=128, null=True)),
                ('days_per_cycle', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('number_of_cycles', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('response_to_treatment_criteria_method', models.CharField(blank=True, max_length=255, null=True)),
                ('response_to_treatment', models.CharField(blank=True, max_length=255, null=True)),
                ('status_of_treatment', models.CharField(blank=True, max_length=255, null=True)),
                ('program_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.program')),
                ('submitter_donor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.donor')),
                ('submitter_primary_diagnosis_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.primarydiagnosis')),
            ],
            options={
                'ordering': ['submitter_treatment_id'],
            },
        ),
        migrations.CreateModel(
            name='Surgery',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('submitter_specimen_id', models.CharField(blank=True, max_length=64, null=True)),
                ('surgery_type', models.CharField(blank=True, max_length=255, null=True)),
                ('surgery_site', models.CharField(blank=True, max_length=255, null=True)),
                ('surgery_location', models.CharField(blank=True, max_length=128, null=True)),
                ('tumour_length', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('tumour_width', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('greatest_dimension_tumour', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('tumour_focality', models.CharField(blank=True, max_length=64, null=True)),
                ('residual_tumour_classification', models.CharField(blank=True, max_length=64, null=True)),
                ('margin_types_involved', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=128, null=True), blank=True, null=True, size=None)),
                ('margin_types_not_involved', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=128, null=True), blank=True, null=True, size=None)),
                ('margin_types_not_assessed', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=128, null=True), blank=True, null=True, size=None)),
                ('lymphovascular_invasion', models.CharField(blank=True, max_length=255, null=True)),
                ('perineural_invasion', models.CharField(blank=True, max_length=128, null=True)),
                ('program_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.program')),
                ('submitter_donor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.donor')),
                ('submitter_treatment_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.treatment')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Specimen',
            fields=[
                ('submitter_specimen_id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('pathological_tumour_staging_system', models.CharField(blank=True, max_length=255, null=True)),
                ('pathological_t_category', models.CharField(blank=True, max_length=64, null=True)),
                ('pathological_n_category', models.CharField(blank=True, max_length=64, null=True)),
                ('pathological_m_category', models.CharField(blank=True, max_length=64, null=True)),
                ('pathological_stage_group', models.CharField(blank=True, max_length=64, null=True)),
                ('specimen_collection_date', models.CharField(blank=True, max_length=32, null=True)),
                ('specimen_storage', models.CharField(blank=True, max_length=64, null=True)),
                ('specimen_processing', models.CharField(blank=True, max_length=128, null=True)),
                ('tumour_histological_type', models.CharField(blank=True, max_length=128, null=True)),
                ('specimen_anatomic_location', models.CharField(blank=True, max_length=32, null=True)),
                ('specimen_laterality', models.CharField(blank=True, max_length=64, null=True)),
                ('reference_pathology_confirmed_diagnosis', models.CharField(blank=True, max_length=32, null=True)),
                ('reference_pathology_confirmed_tumour_presence', models.CharField(blank=True, max_length=32, null=True)),
                ('tumour_grading_system', models.CharField(blank=True, max_length=128, null=True)),
                ('tumour_grade', models.CharField(blank=True, max_length=64, null=True)),
                ('percent_tumour_cells_range', models.CharField(blank=True, max_length=64, null=True)),
                ('percent_tumour_cells_measurement_method', models.CharField(blank=True, max_length=64, null=True)),
                ('program_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.program')),
                ('submitter_donor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.donor')),
                ('submitter_primary_diagnosis_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.primarydiagnosis')),
            ],
            options={
                'ordering': ['submitter_specimen_id'],
            },
        ),
        migrations.CreateModel(
            name='SampleRegistration',
            fields=[
                ('submitter_sample_id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('specimen_tissue_source', models.CharField(blank=True, max_length=255, null=True)),
                ('tumour_normal_designation', models.CharField(blank=True, max_length=32, null=True)),
                ('specimen_type', models.CharField(blank=True, max_length=255, null=True)),
                ('sample_type', models.CharField(blank=True, max_length=128, null=True)),
                ('program_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.program')),
                ('submitter_donor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.donor')),
                ('submitter_specimen_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.specimen')),
            ],
            options={
                'ordering': ['submitter_sample_id'],
            },
        ),
        migrations.CreateModel(
            name='Radiation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('radiation_therapy_modality', models.CharField(blank=True, max_length=255, null=True)),
                ('radiation_therapy_type', models.CharField(blank=True, max_length=64, null=True)),
                ('radiation_therapy_fractions', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('radiation_therapy_dosage', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('anatomical_site_irradiated', models.CharField(blank=True, max_length=255, null=True)),
                ('radiation_boost', models.BooleanField(blank=True, null=True)),
                ('reference_radiation_treatment_id', models.CharField(blank=True, max_length=64, null=True)),
                ('program_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.program')),
                ('submitter_donor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.donor')),
                ('submitter_treatment_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.treatment')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='primarydiagnosis',
            name='program_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.program'),
        ),
        migrations.AddField(
            model_name='primarydiagnosis',
            name='submitter_donor_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.donor'),
        ),
        migrations.CreateModel(
            name='Immunotherapy',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('drug_reference_database', models.CharField(blank=True, max_length=64, null=True)),
                ('immunotherapy_type', models.CharField(blank=True, max_length=255, null=True)),
                ('drug_name', models.CharField(blank=True, max_length=255, null=True)),
                ('drug_reference_identifier', models.CharField(blank=True, max_length=64, null=True)),
                ('immunotherapy_drug_dose_units', models.CharField(blank=True, max_length=64, null=True)),
                ('prescribed_cumulative_drug_dose', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('actual_cumulative_drug_dose', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('program_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.program')),
                ('submitter_donor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.donor')),
                ('submitter_treatment_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.treatment')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='HormoneTherapy',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('drug_reference_database', models.CharField(blank=True, max_length=64, null=True)),
                ('drug_name', models.CharField(blank=True, max_length=255, null=True)),
                ('drug_reference_identifier', models.CharField(blank=True, max_length=64, null=True)),
                ('hormone_drug_dose_units', models.CharField(blank=True, max_length=64, null=True)),
                ('prescribed_cumulative_drug_dose', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('actual_cumulative_drug_dose', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('program_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.program')),
                ('submitter_donor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.donor')),
                ('submitter_treatment_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.treatment')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='FollowUp',
            fields=[
                ('submitter_follow_up_id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('date_of_followup', models.CharField(blank=True, max_length=32, null=True)),
                ('disease_status_at_followup', models.CharField(blank=True, max_length=255, null=True)),
                ('relapse_type', models.CharField(blank=True, max_length=128, null=True)),
                ('date_of_relapse', models.CharField(blank=True, max_length=32, null=True)),
                ('method_of_progression_status', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=255, null=True), blank=True, null=True, size=None)),
                ('anatomic_site_progression_or_recurrence', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=255, null=True), blank=True, null=True, size=None)),
                ('recurrence_tumour_staging_system', models.CharField(blank=True, max_length=255, null=True)),
                ('recurrence_t_category', models.CharField(blank=True, max_length=32, null=True)),
                ('recurrence_n_category', models.CharField(blank=True, max_length=32, null=True)),
                ('recurrence_m_category', models.CharField(blank=True, max_length=32, null=True)),
                ('recurrence_stage_group', models.CharField(blank=True, max_length=64, null=True)),
                ('program_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.program')),
                ('submitter_donor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.donor')),
                ('submitter_primary_diagnosis_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mohpackets.primarydiagnosis')),
                ('submitter_treatment_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mohpackets.treatment')),
            ],
            options={
                'ordering': ['submitter_follow_up_id'],
            },
        ),
        migrations.CreateModel(
            name='Exposure',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('tobacco_smoking_status', models.CharField(blank=True, max_length=255, null=True)),
                ('tobacco_type', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=128, null=True), blank=True, null=True, size=None)),
                ('pack_years_smoked', models.FloatField(blank=True, null=True)),
                ('program_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.program')),
                ('submitter_donor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.donor')),
            ],
        ),
        migrations.AddField(
            model_name='donor',
            name='program_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.program'),
        ),
        migrations.CreateModel(
            name='Comorbidity',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('prior_malignancy', models.CharField(blank=True, max_length=32, null=True)),
                ('laterality_of_prior_malignancy', models.CharField(blank=True, max_length=64, null=True)),
                ('age_at_comorbidity_diagnosis', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('comorbidity_type_code', models.CharField(blank=True, max_length=64, null=True)),
                ('comorbidity_treatment_status', models.CharField(blank=True, max_length=32, null=True)),
                ('comorbidity_treatment', models.CharField(blank=True, max_length=255, null=True)),
                ('program_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.program')),
                ('submitter_donor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.donor')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Chemotherapy',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('drug_reference_database', models.CharField(blank=True, max_length=64, null=True)),
                ('drug_name', models.CharField(blank=True, max_length=255, null=True)),
                ('drug_reference_identifier', models.CharField(blank=True, max_length=64, null=True)),
                ('chemotherapy_drug_dose_units', models.CharField(blank=True, max_length=64, null=True)),
                ('prescribed_cumulative_drug_dose', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('actual_cumulative_drug_dose', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('program_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.program')),
                ('submitter_donor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.donor')),
                ('submitter_treatment_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.treatment')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Biomarker',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('submitter_specimen_id', models.CharField(blank=True, max_length=64, null=True)),
                ('submitter_primary_diagnosis_id', models.CharField(blank=True, max_length=64, null=True)),
                ('submitter_treatment_id', models.CharField(blank=True, max_length=64, null=True)),
                ('submitter_follow_up_id', models.CharField(blank=True, max_length=64, null=True)),
                ('test_date', models.CharField(blank=True, max_length=32, null=True)),
                ('psa_level', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('ca125', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('cea', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('er_status', models.CharField(blank=True, max_length=64, null=True)),
                ('er_percent_positive', models.FloatField(blank=True, null=True)),
                ('pr_status', models.CharField(blank=True, max_length=64, null=True)),
                ('pr_percent_positive', models.FloatField(blank=True, null=True)),
                ('her2_ihc_status', models.CharField(blank=True, max_length=64, null=True)),
                ('her2_ish_status', models.CharField(blank=True, max_length=64, null=True)),
                ('hpv_ihc_status', models.CharField(blank=True, max_length=64, null=True)),
                ('hpv_pcr_status', models.CharField(blank=True, max_length=64, null=True)),
                ('hpv_strain', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=32, null=True), blank=True, null=True, size=None)),
                ('program_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.program')),
                ('submitter_donor_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mohpackets.donor')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
