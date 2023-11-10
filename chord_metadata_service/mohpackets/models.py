import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

""" 
    Marathon of Hope MODELS module containing MOHCCN Clinical Data Model V2.
    
    Model Schema: https://www.marathonofhopecancercentres.ca/docs/default-source/policies-and-guidelines/moh-clinical-data-model-v2---feb-202381759e70b6034dcfa0b7bde4174e9822.xlsx?Status=Master&sfvrsn=2932cab_7 # noqa: E501
    ER Diagram: https://www.marathonofhopecancercentres.ca/docs/default-source/policies-and-guidelines/mohccn_data_standard_er_diagram_endorsed6oct22.pdf?Status=Master&sfvrsn=dd57a75e_5 # noqa: E501

    Note: UUID and FK fields are added to the original Model Schema. 
    For the list of changes, see "Notes on the changes from the Entity Model (ER)" 
    on Confluence page.
    
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
    is_deceased = models.BooleanField(blank=True, null=True)
    lost_to_followup_after_clinical_event_identifier = models.CharField(
        max_length=255, null=True, blank=True
    )
    lost_to_followup_reason = models.CharField(max_length=255, null=True, blank=True)
    date_alive_after_lost_to_followup = models.CharField(
        max_length=32, null=True, blank=True
    )
    cause_of_death = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.CharField(max_length=32, null=True, blank=True)
    date_of_death = models.CharField(max_length=32, null=True, blank=True)
    primary_site = ArrayField(
        models.CharField(max_length=255, null=True, blank=True), null=True, blank=True
    )

    class Meta:
        unique_together = ["program_id", "submitter_donor_id"]
        ordering = ["submitter_donor_id"]

    def __str__(self):
        return f"{self.submitter_donor_id}"


class PrimaryDiagnosis(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    donor_uuid = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=True, blank=True
    )
    submitter_primary_diagnosis_id = models.CharField(
        max_length=64, null=True, blank=True
    )
    submitter_donor_id = models.CharField(max_length=64, null=True, blank=True)
    date_of_diagnosis = models.CharField(max_length=32, null=True, blank=True)
    cancer_type_code = models.CharField(max_length=64, null=True, blank=True)
    basis_of_diagnosis = models.CharField(max_length=128, null=True, blank=True)
    laterality = models.CharField(max_length=128, null=True, blank=True)
    lymph_nodes_examined_status = models.CharField(
        max_length=128, null=True, blank=True
    )
    lymph_nodes_examined_method = models.CharField(max_length=64, null=True, blank=True)
    number_lymph_nodes_positive = models.PositiveSmallIntegerField(
        null=True, blank=True
    )
    clinical_tumour_staging_system = models.CharField(
        max_length=128, null=True, blank=True
    )
    clinical_t_category = models.CharField(max_length=64, null=True, blank=True)
    clinical_n_category = models.CharField(max_length=64, null=True, blank=True)
    clinical_m_category = models.CharField(max_length=64, null=True, blank=True)
    clinical_stage_group = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        unique_together = ["program_id", "submitter_primary_diagnosis_id"]
        ordering = ["submitter_primary_diagnosis_id"]

    def __str__(self):
        return f"{self.submitter_primary_diagnosis_id}"


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
    pathological_tumour_staging_system = models.CharField(
        max_length=255, null=True, blank=True
    )
    pathological_t_category = models.CharField(max_length=64, null=True, blank=True)
    pathological_n_category = models.CharField(max_length=64, null=True, blank=True)
    pathological_m_category = models.CharField(max_length=64, null=True, blank=True)
    pathological_stage_group = models.CharField(max_length=64, null=True, blank=True)
    specimen_collection_date = models.CharField(max_length=32, null=True, blank=True)
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
        unique_together = ["program_id", "submitter_specimen_id"]
        ordering = ["submitter_specimen_id"]

    def __str__(self):
        return f"{self.submitter_specimen_id}"


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
        unique_together = ["program_id", "submitter_sample_id"]
        ordering = ["submitter_sample_id"]

    def __str__(self):
        return f"{self.submitter_sample_id}"


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
    line_of_treatment = models.IntegerField(null=True, blank=True)
    treatment_start_date = models.CharField(max_length=32, null=True, blank=True)
    treatment_end_date = models.CharField(max_length=32, null=True, blank=True)
    treatment_setting = models.CharField(max_length=128, null=True, blank=True)
    treatment_intent = models.CharField(max_length=128, null=True, blank=True)
    days_per_cycle = models.PositiveSmallIntegerField(null=True, blank=True)
    number_of_cycles = models.PositiveSmallIntegerField(null=True, blank=True)
    response_to_treatment_criteria_method = models.CharField(
        max_length=255, null=True, blank=True
    )
    response_to_treatment = models.CharField(max_length=255, null=True, blank=True)
    status_of_treatment = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ["program_id", "submitter_treatment_id"]
        ordering = ["submitter_treatment_id"]

    def __str__(self):
        return f"{self.submitter_treatment_id}"


class Chemotherapy(models.Model):
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
    drug_reference_database = models.CharField(max_length=64, null=True, blank=True)
    drug_name = models.CharField(max_length=255, null=True, blank=True)
    drug_reference_identifier = models.CharField(max_length=64, null=True, blank=True)
    chemotherapy_drug_dose_units = models.CharField(
        max_length=64, null=True, blank=True
    )
    prescribed_cumulative_drug_dose = models.PositiveSmallIntegerField(
        blank=True, null=True
    )
    actual_cumulative_drug_dose = models.PositiveSmallIntegerField(
        blank=True, null=True
    )

    class Meta:
        ordering = ["uuid"]

    def __str__(self):
        return f"{self.submitter_treatment_id}"


class HormoneTherapy(models.Model):
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
    drug_reference_database = models.CharField(max_length=64, null=True, blank=True)
    drug_name = models.CharField(max_length=255, null=True, blank=True)
    drug_reference_identifier = models.CharField(max_length=64, null=True, blank=True)
    hormone_drug_dose_units = models.CharField(max_length=64, null=True, blank=True)
    prescribed_cumulative_drug_dose = models.PositiveSmallIntegerField(
        blank=True, null=True
    )
    actual_cumulative_drug_dose = models.PositiveSmallIntegerField(
        blank=True, null=True
    )

    class Meta:
        ordering = ["uuid"]

    def __str__(self):
        return f"{self.submitter_treatment_id}"


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
    radiation_therapy_fractions = models.PositiveSmallIntegerField(
        null=True, blank=True
    )
    radiation_therapy_dosage = models.PositiveSmallIntegerField(null=True, blank=True)
    anatomical_site_irradiated = models.CharField(max_length=255, null=True, blank=True)
    radiation_boost = models.BooleanField(blank=True, null=True)
    reference_radiation_treatment_id = models.CharField(
        max_length=64, null=True, blank=True
    )

    class Meta:
        ordering = ["uuid"]

    def __str__(self):
        return f"{self.submitter_treatment_id}"


class Immunotherapy(models.Model):
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
    drug_reference_database = models.CharField(max_length=64, null=True, blank=True)
    immunotherapy_type = models.CharField(max_length=255, null=True, blank=True)
    drug_name = models.CharField(max_length=255, null=True, blank=True)
    drug_reference_identifier = models.CharField(max_length=64, null=True, blank=True)
    immunotherapy_drug_dose_units = models.CharField(
        max_length=64, null=True, blank=True
    )
    prescribed_cumulative_drug_dose = models.PositiveSmallIntegerField(
        blank=True, null=True
    )
    actual_cumulative_drug_dose = models.PositiveSmallIntegerField(
        blank=True, null=True
    )

    class Meta:
        ordering = ["uuid"]

    def __str__(self):
        return f"{self.submitter_treatment_id}"


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
    submitter_specimen_id = models.CharField(max_length=64, null=True, blank=True)
    surgery_type = models.CharField(max_length=255, null=True, blank=True)
    surgery_site = models.CharField(max_length=255, null=True, blank=True)
    surgery_location = models.CharField(max_length=128, null=True, blank=True)
    tumour_length = models.PositiveSmallIntegerField(null=True, blank=True)
    tumour_width = models.PositiveSmallIntegerField(null=True, blank=True)
    greatest_dimension_tumour = models.PositiveSmallIntegerField(null=True, blank=True)
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

    class Meta:
        ordering = ["uuid"]

    def __str__(self):
        return f"{self.submitter_treatment_id}"


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
        max_length=64, null=False, blank=False
    )
    submitter_treatment_id = models.CharField(max_length=64, null=False, blank=False)
    date_of_followup = models.CharField(max_length=32, null=True, blank=True)
    disease_status_at_followup = models.CharField(max_length=255, null=True, blank=True)
    relapse_type = models.CharField(max_length=128, null=True, blank=True)
    date_of_relapse = models.CharField(max_length=32, null=True, blank=True)
    method_of_progression_status = ArrayField(
        models.CharField(max_length=255, null=True, blank=True), null=True, blank=True
    )
    anatomic_site_progression_or_recurrence = ArrayField(
        models.CharField(max_length=255, null=True, blank=True), null=True, blank=True
    )
    recurrence_tumour_staging_system = models.CharField(
        max_length=255, null=True, blank=True
    )
    recurrence_t_category = models.CharField(max_length=32, null=True, blank=True)
    recurrence_n_category = models.CharField(max_length=32, null=True, blank=True)
    recurrence_m_category = models.CharField(max_length=32, null=True, blank=True)
    recurrence_stage_group = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        unique_together = ["program_id", "submitter_follow_up_id"]
        ordering = ["submitter_follow_up_id"]

    def __str__(self):
        return f"{self.submitter_follow_up_id}"


class Biomarker(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    donor_uuid = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.CharField(max_length=64, null=False, blank=False)
    submitter_specimen_id = models.CharField(max_length=64, null=True, blank=True)
    submitter_primary_diagnosis_id = models.CharField(
        max_length=64, null=True, blank=True
    )
    submitter_treatment_id = models.CharField(max_length=64, null=True, blank=True)
    submitter_follow_up_id = models.CharField(max_length=64, null=True, blank=True)
    test_date = models.CharField(max_length=32, null=True, blank=True)
    psa_level = models.PositiveSmallIntegerField(null=True, blank=True)
    ca125 = models.PositiveSmallIntegerField(null=True, blank=True)
    cea = models.PositiveSmallIntegerField(null=True, blank=True)
    er_status = models.CharField(max_length=64, null=True, blank=True)
    er_percent_positive = models.FloatField(null=True, blank=True)
    pr_status = models.CharField(max_length=64, null=True, blank=True)
    pr_percent_positive = models.FloatField(null=True, blank=True)
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
        return f"{self.submitter_donor_id}"


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
    age_at_comorbidity_diagnosis = models.PositiveSmallIntegerField(
        null=True, blank=True
    )
    comorbidity_type_code = models.CharField(max_length=64, null=True, blank=True)
    comorbidity_treatment_status = models.CharField(
        max_length=32, null=True, blank=True
    )
    comorbidity_treatment = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ["uuid"]

    def __str__(self):
        return f"{self.donor_uuid}"


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

    class Meta:
        ordering = ["uuid"]

    def __str__(self):
        return f"{self.donor_uuid}"
