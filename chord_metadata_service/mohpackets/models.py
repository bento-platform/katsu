import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

"""
    This module contains MOHCCN Clinical Data Model V3.

    Field constraints should be handle in the schema, not in the model.
    UUID and FK fields are added to the original Model Schema for internal use.

    Author: Son Chau
"""


class AutoDateTimeField(models.DateTimeField):
    """
    This function provides the timefield when the model is saved.
    Without this, the updated field will be empty and failed on update.
    """

    def pre_save(self, model_instance, add):
        return timezone.now()


class Program(models.Model):
    program_id = models.CharField(max_length=64, primary_key=True)
    metadata = models.JSONField(null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    updated = AutoDateTimeField(default=timezone.now)

    class Meta:
        ordering = ["program_id"]

    def __str__(self):
        return f"{self.program_id}"


class Donor(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    submitter_donor_id = models.CharField(max_length=64, null=False, blank=False)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    gender = models.CharField(max_length=32, null=True, blank=True)
    sex_at_birth = models.CharField(max_length=32, null=True, blank=True)
    is_deceased = models.CharField(max_length=32, blank=True, null=True)
    lost_to_followup_after_clinical_event_identifier = models.CharField(
        max_length=255, null=True, blank=True
    )
    lost_to_followup_reason = models.CharField(max_length=255, null=True, blank=True)
    date_alive_after_lost_to_followup = models.JSONField(null=True, blank=True)
    cause_of_death = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.JSONField(null=True, blank=True)
    date_of_death = models.JSONField(null=True, blank=True)
    date_resolution = models.CharField(max_length=32, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["program_id", "submitter_donor_id"], name="unique_donor"
            )
        ]
        ordering = ["submitter_donor_id"]

    def __str__(self):
        return f"{self.program_id}: {self.submitter_donor_id}"


class PrimaryDiagnosis(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    donor_uuid = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_primary_diagnosis_id = models.CharField(
        max_length=64, null=False, blank=False
    )
    submitter_donor_id = models.CharField(max_length=64, null=False, blank=False)
    primary_site = models.CharField(max_length=255, null=True, blank=True)
    date_of_diagnosis = models.JSONField(null=True, blank=True)
    cancer_type_code = models.CharField(max_length=64, null=True, blank=True)
    basis_of_diagnosis = models.CharField(max_length=128, null=True, blank=True)
    laterality = models.CharField(max_length=128, null=True, blank=True)
    clinical_tumour_staging_system = models.CharField(
        max_length=128, null=True, blank=True
    )
    clinical_t_category = models.CharField(max_length=64, null=True, blank=True)
    clinical_n_category = models.CharField(max_length=64, null=True, blank=True)
    clinical_m_category = models.CharField(max_length=64, null=True, blank=True)
    clinical_stage_group = models.CharField(max_length=64, null=True, blank=True)
    pathological_tumour_staging_system = models.CharField(
        max_length=255, null=True, blank=True
    )
    pathological_t_category = models.CharField(max_length=64, null=True, blank=True)
    pathological_n_category = models.CharField(max_length=64, null=True, blank=True)
    pathological_m_category = models.CharField(max_length=64, null=True, blank=True)
    pathological_stage_group = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["program_id", "submitter_primary_diagnosis_id"],
                name="unique_primary_diagnosis",
            )
        ]
        ordering = ["submitter_primary_diagnosis_id"]

    def __str__(self):
        return f"{self.program_id}: {self.submitter_primary_diagnosis_id}"


class Specimen(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    donor_uuid = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    primary_diagnosis_uuid = models.ForeignKey(
        PrimaryDiagnosis, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_specimen_id = models.CharField(max_length=64, null=False, blank=False)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.CharField(max_length=64, null=False, blank=False)
    submitter_primary_diagnosis_id = models.CharField(
        max_length=64, null=False, blank=False
    )
    submitter_treatment_id = models.CharField(
        max_length=64, null=True, blank=True
    )  # ref field, not a true id
    specimen_collection_date = models.JSONField(null=True, blank=True)
    specimen_storage = models.CharField(max_length=64, null=True, blank=True)
    specimen_processing = models.CharField(max_length=128, null=True, blank=True)
    tumour_histological_type = models.CharField(max_length=128, null=True, blank=True)
    specimen_anatomic_location = models.CharField(max_length=32, null=True, blank=True)
    specimen_laterality = models.CharField(max_length=64, null=True, blank=True)
    reference_pathology_confirmed_diagnosis = models.CharField(
        max_length=32, null=True, blank=True
    )
    reference_pathology_confirmed_tumour_presence = models.CharField(
        max_length=32, null=True, blank=True
    )
    tumour_grading_system = models.CharField(max_length=128, null=True, blank=True)
    tumour_grade = models.CharField(max_length=64, null=True, blank=True)
    percent_tumour_cells_range = models.CharField(max_length=64, null=True, blank=True)
    percent_tumour_cells_measurement_method = models.CharField(
        max_length=64, null=True, blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["program_id", "submitter_specimen_id"], name="unique_specimen"
            )
        ]
        ordering = ["submitter_specimen_id"]

    def __str__(self):
        return f"{self.program_id}: {self.submitter_specimen_id}"


class SampleRegistration(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    donor_uuid = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    specimen_uuid = models.ForeignKey(
        Specimen, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_sample_id = models.CharField(max_length=64, null=False, blank=False)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.CharField(max_length=64, null=False, blank=False)
    submitter_specimen_id = models.CharField(max_length=64, null=False, blank=False)
    specimen_tissue_source = models.CharField(max_length=255, null=True, blank=True)
    tumour_normal_designation = models.CharField(max_length=32, null=True, blank=True)
    specimen_type = models.CharField(max_length=255, null=True, blank=True)
    sample_type = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["program_id", "submitter_sample_id"],
                name="unique_sample_registration",
            )
        ]
        ordering = ["submitter_sample_id"]

    def __str__(self):
        return f"{self.program_id}: {self.submitter_sample_id}"


class Treatment(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    donor_uuid = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    primary_diagnosis_uuid = models.ForeignKey(
        PrimaryDiagnosis, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_treatment_id = models.CharField(max_length=64, null=False, blank=False)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.CharField(max_length=64, null=False, blank=False)
    submitter_primary_diagnosis_id = models.CharField(
        max_length=64, null=False, blank=False
    )
    treatment_type = ArrayField(models.CharField(max_length=255), null=True, blank=True)
    is_primary_treatment = models.CharField(max_length=32, null=True, blank=True)
    treatment_start_date = models.JSONField(null=True, blank=True)
    treatment_end_date = models.JSONField(null=True, blank=True)
    treatment_intent = models.CharField(max_length=128, null=True, blank=True)
    response_to_treatment_criteria_method = models.CharField(
        max_length=255, null=True, blank=True
    )
    response_to_treatment = models.CharField(max_length=255, null=True, blank=True)
    status_of_treatment = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["program_id", "submitter_treatment_id"], name="unique_treatment"
            )
        ]
        ordering = ["submitter_treatment_id"]

    def __str__(self):
        return f"{self.program_id}: {self.submitter_treatment_id}"


class SystemicTherapy(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    donor_uuid = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    treatment_uuid = models.ForeignKey(
        Treatment, on_delete=models.CASCADE, null=False, blank=False
    )
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.CharField(max_length=64, null=False, blank=False)
    submitter_treatment_id = models.CharField(max_length=64, null=False, blank=False)
    systemic_therapy_type = models.CharField(max_length=32, null=True, blank=True)
    days_per_cycle = models.IntegerField(null=True, blank=True)
    days_per_cycle_not_available = models.BooleanField(default=False)
    number_of_cycles = models.IntegerField(null=True, blank=True)
    number_of_cycles_not_available = models.BooleanField(default=False)
    start_date = models.JSONField(null=True, blank=True)
    end_date = models.JSONField(null=True, blank=True)
    drug_reference_database = models.CharField(max_length=64, null=True, blank=True)
    drug_name = models.CharField(max_length=255, null=True, blank=True)
    drug_reference_identifier = models.CharField(max_length=64, null=True, blank=True)
    drug_dose_units = models.CharField(max_length=64, null=True, blank=True)
    prescribed_cumulative_drug_dose = models.FloatField(blank=True, null=True)
    prescribed_cumulative_drug_dose_not_available = models.BooleanField(default=False)
    actual_cumulative_drug_dose = models.FloatField(blank=True, null=True)
    actual_cumulative_drug_dose_not_available = models.BooleanField(default=False)

    class Meta:
        ordering = ["uuid"]

    def __str__(self):
        return f"{self.program_id}: {self.submitter_treatment_id}"


class Radiation(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    donor_uuid = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    treatment_uuid = models.ForeignKey(
        Treatment, on_delete=models.CASCADE, null=False, blank=False
    )
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.CharField(max_length=64, null=False, blank=False)
    submitter_treatment_id = models.CharField(max_length=64, null=False, blank=False)
    radiation_therapy_modality = models.CharField(max_length=255, null=True, blank=True)
    radiation_therapy_type = models.CharField(max_length=64, null=True, blank=True)
    radiation_therapy_fractions = models.IntegerField(null=True, blank=True)
    radiation_therapy_fractions_not_available = models.BooleanField(default=False)
    radiation_therapy_dosage = models.IntegerField(null=True, blank=True)
    radiation_therapy_dosage_not_available = models.BooleanField(default=False)
    anatomical_site_irradiated = models.CharField(max_length=255, null=True, blank=True)
    radiation_boost = models.CharField(max_length=32, blank=True, null=True)
    reference_radiation_treatment_id = models.CharField(
        max_length=64, null=True, blank=True
    )

    class Meta:
        ordering = ["uuid"]

    def __str__(self):
        return f"{self.program_id}: {self.submitter_treatment_id}"


class Surgery(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    donor_uuid = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    treatment_uuid = models.ForeignKey(
        Treatment, on_delete=models.CASCADE, null=False, blank=False
    )
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.CharField(max_length=64, null=False, blank=False)
    submitter_treatment_id = models.CharField(max_length=64, null=False, blank=False)
    surgery_type = models.CharField(max_length=255, null=True, blank=True)
    surgery_site = models.CharField(max_length=255, null=True, blank=True)
    surgery_location = models.CharField(max_length=128, null=True, blank=True)
    tumour_length = models.IntegerField(null=True, blank=True)
    tumour_length_not_available = models.BooleanField(default=False)
    tumour_width = models.IntegerField(null=True, blank=True)
    tumour_width_not_available = models.BooleanField(default=False)
    greatest_dimension_tumour = models.IntegerField(null=True, blank=True)
    greatest_dimension_tumour_not_available = models.BooleanField(default=False)
    tumour_focality = models.CharField(max_length=64, null=True, blank=True)
    residual_tumour_classification = models.CharField(
        max_length=64, null=True, blank=True
    )
    margin_types_involved = ArrayField(
        models.CharField(max_length=128, null=True, blank=True), null=True, blank=True
    )
    margin_types_not_involved = ArrayField(
        models.CharField(max_length=128, null=True, blank=True), null=True, blank=True
    )
    margin_types_not_assessed = ArrayField(
        models.CharField(max_length=128, null=True, blank=True), null=True, blank=True
    )
    lymphovascular_invasion = models.CharField(max_length=255, null=True, blank=True)
    perineural_invasion = models.CharField(max_length=128, null=True, blank=True)
    surgery_reference_database = models.CharField(max_length=64, null=True, blank=True)
    surgery_reference_identifier = models.CharField(
        max_length=64, null=True, blank=True
    )

    class Meta:
        ordering = ["uuid"]

    def __str__(self):
        return f"{self.program_id}: {self.submitter_treatment_id}"


class FollowUp(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    donor_uuid = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    treatment_uuid = models.ForeignKey(
        Treatment, on_delete=models.CASCADE, null=True, blank=True
    )
    primary_diagnosis_uuid = models.ForeignKey(
        PrimaryDiagnosis, on_delete=models.CASCADE, null=True, blank=True
    )
    submitter_follow_up_id = models.CharField(max_length=64, null=False, blank=False)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.CharField(max_length=64, null=False, blank=False)
    submitter_primary_diagnosis_id = models.CharField(
        max_length=64, null=True, blank=True
    )  # optional id
    submitter_treatment_id = models.CharField(
        max_length=64, null=True, blank=True
    )  # optional id
    date_of_followup = models.JSONField(null=True, blank=True)
    disease_status_at_followup = models.CharField(max_length=255, null=True, blank=True)
    relapse_type = models.CharField(max_length=128, null=True, blank=True)
    date_of_relapse = models.JSONField(null=True, blank=True)
    method_of_progression_status = ArrayField(
        models.CharField(max_length=255, null=True, blank=True), null=True, blank=True
    )
    anatomic_site_progression_or_recurrence = ArrayField(
        models.CharField(max_length=255, null=True, blank=True), null=True, blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["program_id", "submitter_follow_up_id"], name="unique_follow_up"
            )
        ]
        ordering = ["submitter_follow_up_id"]

    def __str__(self):
        return f"{self.program_id}: {self.submitter_follow_up_id}"


class Biomarker(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    donor_uuid = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.CharField(max_length=64, null=False, blank=False)
    submitter_specimen_id = models.CharField(
        max_length=64, null=True, blank=True
    )  # ref field, not true id
    submitter_primary_diagnosis_id = models.CharField(
        max_length=64, null=True, blank=True
    )  # ref field, not true id
    submitter_treatment_id = models.CharField(
        max_length=64, null=True, blank=True
    )  # ref field, not true id
    submitter_follow_up_id = models.CharField(
        max_length=64, null=True, blank=True
    )  # ref field, not true id
    test_date = models.JSONField(null=True, blank=True)
    psa_level = models.IntegerField(null=True, blank=True)
    psa_level_not_available = models.BooleanField(default=False)
    ca125 = models.IntegerField(null=True, blank=True)
    ca125_not_available = models.BooleanField(default=False)
    cea = models.IntegerField(null=True, blank=True)
    cea_not_available = models.BooleanField(default=False)
    er_status = models.CharField(max_length=64, null=True, blank=True)
    er_percent_positive = models.FloatField(null=True, blank=True)
    er_percent_positive_not_available = models.BooleanField(default=False)
    pr_status = models.CharField(max_length=64, null=True, blank=True)
    pr_percent_positive = models.FloatField(null=True, blank=True)
    pr_percent_positive_not_available = models.BooleanField(default=False)
    her2_ihc_status = models.CharField(max_length=64, null=True, blank=True)
    her2_ish_status = models.CharField(max_length=64, null=True, blank=True)
    hpv_ihc_status = models.CharField(max_length=64, null=True, blank=True)
    hpv_pcr_status = models.CharField(max_length=64, null=True, blank=True)
    hpv_strain = ArrayField(
        models.CharField(max_length=32, null=True, blank=True), null=True, blank=True
    )

    class Meta:
        ordering = ["uuid"]

    def __str__(self):
        return f"{self.program_id}: {self.submitter_donor_id}"


class Comorbidity(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    donor_uuid = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.CharField(max_length=64, null=False, blank=False)
    prior_malignancy = models.CharField(max_length=32, null=True, blank=True)
    laterality_of_prior_malignancy = models.CharField(
        max_length=64, null=True, blank=True
    )
    age_at_comorbidity_diagnosis = models.IntegerField(null=True, blank=True)
    age_at_comorbidity_diagnosis_not_available = models.BooleanField(default=False)
    comorbidity_type_code = models.CharField(max_length=64, null=True, blank=True)
    comorbidity_treatment_status = models.CharField(
        max_length=32, null=True, blank=True
    )
    comorbidity_treatment = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ["uuid"]

    def __str__(self):
        return f"{self.program_id}: {self.submitter_donor_id}"


class Exposure(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    donor_uuid = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.CharField(max_length=64, null=False, blank=False)
    tobacco_smoking_status = models.CharField(max_length=255, null=True, blank=True)
    tobacco_type = ArrayField(
        models.CharField(max_length=128, null=True, blank=True), null=True, blank=True
    )
    pack_years_smoked = models.FloatField(null=True, blank=True)
    pack_years_smoked_not_available = models.BooleanField(default=False)

    class Meta:
        ordering = ["uuid"]

    def __str__(self):
        return f"{self.program_id}: {self.submitter_donor_id}"
