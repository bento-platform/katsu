from django.db import models
from django.utils import timezone

"""
    This module contains the MODELS for the Marathon of Hope app.
    --------------------------------
    MOHCCN Clinical Data Model V1: Data Standards Sub-Committee (DSC)
    Model Schema (Excel): https://docs.google.com/spreadsheets/d/1pChl2DQiynU0OdueDHW7saJiLliv31GutgNbW8XSfUk/edit#gid=0 # noqa: E501
    Model Schema (PDF): https://www.marathonofhopecancercentres.ca/docs/default-source/policies-and-guidelines/mohccn-clinical-data-model_v1_endorsed6oct-2022.pdf?Status=Master&sfvrsn=7f6bd159_7 # noqa: E501
    ER Diagram: https://www.marathonofhopecancercentres.ca/docs/default-source/policies-and-guidelines/mohccn_data_standard_er_diagram_endorsed6oct22.pdf?Status=Master&sfvrsn=dd57a75e_5 # noqa: E501
    Schema last updated: September 2022
    --------------------------------
    NOTES:
    - Permissible values are not enforced in the model.
        They are checked in the serializer and ingest process.

    - It is important to have a __str__ method to return just the ID as
        the validator regex relies on this for primary key validation.
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
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    created = models.DateTimeField(default=timezone.now)
    updated = AutoDateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.program_id}"


class Donor(models.Model):
    submitter_donor_id = models.CharField(max_length=64, primary_key=True)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    is_deceased = models.BooleanField()
    cause_of_death = models.CharField(max_length=255)
    date_of_birth = models.CharField(max_length=32, null=False, blank=False)
    date_of_death = models.CharField(max_length=32)
    primary_site = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return f"{self.submitter_donor_id}"


class PrimaryDiagnosis(models.Model):
    submitter_primary_diagnosis_id = models.CharField(max_length=64, primary_key=True)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    date_of_diagnosis = models.CharField(max_length=32, null=False, blank=False)
    cancer_type_code = models.CharField(max_length=64, null=False, blank=False)
    basis_of_diagnosis = models.CharField(max_length=128, null=False, blank=False)
    lymph_nodes_examined_status = models.CharField(
        max_length=128, null=False, blank=False
    )
    lymph_nodes_examined_method = models.CharField(max_length=64)
    number_lymph_nodes_positive = models.IntegerField(blank=True, null=True)
    clinical_tumour_staging_system = models.CharField(max_length=128)
    clinical_t_category = models.CharField(max_length=64)
    clinical_n_category = models.CharField(max_length=64)
    clinical_m_category = models.CharField(max_length=64)
    clinical_stage_group = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.submitter_primary_diagnosis_id}"


class Specimen(models.Model):
    submitter_specimen_id = models.CharField(max_length=64, primary_key=True)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_primary_diagnosis_id = models.ForeignKey(
        PrimaryDiagnosis, on_delete=models.CASCADE, null=False, blank=False
    )
    pathological_tumour_staging_system = models.CharField(max_length=255)
    pathological_t_category = models.CharField(max_length=64)
    pathological_n_category = models.CharField(max_length=64)
    pathological_m_category = models.CharField(max_length=64)
    pathological_stage_group = models.CharField(max_length=64)
    specimen_collection_date = models.CharField(max_length=32, null=False, blank=False)
    specimen_storage = models.CharField(max_length=64, null=False, blank=False)
    tumour_histological_type = models.CharField(max_length=128)
    specimen_anatomic_location = models.CharField(max_length=32)
    reference_pathology_confirmed_diagnosis = models.CharField(max_length=32)
    reference_pathology_confirmed_tumour_presence = models.CharField(max_length=32)
    tumour_grading_system = models.CharField(max_length=128)
    tumour_grade = models.CharField(max_length=64)
    percent_tumour_cells_range = models.CharField(max_length=64)
    percent_tumour_cells_measurement_method = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.submitter_specimen_id}"


class SampleRegistration(models.Model):
    submitter_sample_id = models.CharField(max_length=64, primary_key=True)
    program_id = models.CharField(max_length=64, null=False, blank=False)
    submitter_donor_id = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_specimen_id = models.ForeignKey(
        Specimen, on_delete=models.CASCADE, null=False, blank=False
    )
    gender = models.CharField(max_length=32, null=False, blank=False)
    sex_at_birth = models.CharField(max_length=32, null=False, blank=False)
    specimen_tissue_source = models.CharField(max_length=255, null=False, blank=False)
    tumour_normal_designation = models.CharField(max_length=32, null=False, blank=False)
    specimen_type = models.CharField(max_length=255, null=False, blank=False)
    sample_type = models.CharField(max_length=128, null=False, blank=False)

    def __str__(self):
        return f"{self.submitter_sample_id}"


class Treatment(models.Model):
    submitter_treatment_id = models.CharField(max_length=64, primary_key=True)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_primary_diagnosis_id = models.ForeignKey(
        PrimaryDiagnosis, on_delete=models.CASCADE, null=False, blank=False
    )
    treatment_type = models.CharField(max_length=255, null=False, blank=False)
    is_primary_treatment = models.CharField(max_length=32, null=False, blank=False)
    treatment_start_date = models.CharField(max_length=32, null=False, blank=False)
    treatment_end_date = models.CharField(max_length=32, null=False, blank=False)
    treatment_setting = models.CharField(max_length=128, null=False, blank=False)
    treatment_intent = models.CharField(max_length=128, null=False, blank=False)
    days_per_cycle = models.IntegerField(blank=True, null=True)
    number_of_cycles = models.IntegerField(blank=True, null=True)
    response_to_treatment_criteria_method = models.CharField(
        max_length=255, null=False, blank=False
    )
    response_to_treatment = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return f"{self.submitter_treatment_id}"


class Chemotherapy(models.Model):
    id = models.AutoField(primary_key=True)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_treatment_id = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    drug_name = models.CharField(max_length=255, null=False, blank=False)
    drug_rxnormcui = models.CharField(max_length=64, null=False, blank=False)
    chemotherapy_dosage_units = models.CharField(max_length=64, null=False, blank=False)
    cumulative_drug_dosage_prescribed = models.IntegerField(blank=True, null=True)
    cumulative_drug_dosage_actual = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}"


class HormoneTherapy(models.Model):
    id = models.AutoField(primary_key=True)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_treatment_id = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    drug_name = models.CharField(max_length=255, null=False, blank=False)
    drug_rxnormcui = models.CharField(max_length=64, null=False, blank=False)
    hormone_drug_dosage_units = models.CharField(max_length=64, null=False, blank=False)
    cumulative_drug_dosage_prescribed = models.IntegerField(blank=True, null=True)
    cumulative_drug_dosage_actual = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}"


class Radiation(models.Model):
    id = models.AutoField(primary_key=True)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_treatment_id = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    radiation_therapy_modality = models.CharField(
        max_length=255, null=False, blank=False
    )
    radiation_therapy_type = models.CharField(max_length=64, null=False, blank=False)
    radiation_therapy_fractions = models.IntegerField()
    radiation_therapy_dosage = models.IntegerField()
    anatomical_site_irradiated = models.CharField(
        max_length=255, null=False, blank=False
    )
    radiation_boost = models.BooleanField(null=True)
    reference_radiation_treatment_id = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.id}"


class Immunotherapy(models.Model):
    id = models.AutoField(primary_key=True)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_treatment_id = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    immunotherapy_type = models.CharField(max_length=255, null=False, blank=False)
    drug_name = models.CharField(max_length=255, null=False, blank=False)
    drug_rxnormcui = models.CharField(max_length=64, null=False, blank=False)

    def __str__(self):
        return f"{self.id}"


class Surgery(models.Model):
    id = models.AutoField(primary_key=True)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_specimen_id = models.ForeignKey(
        Specimen, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_treatment_id = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    surgery_type = models.CharField(max_length=255, null=False, blank=False)
    surgery_site = models.CharField(max_length=255)
    surgery_location = models.CharField(max_length=128)
    tumour_length = models.IntegerField(null=True, blank=True)
    tumour_width = models.IntegerField(null=True, blank=True)
    greatest_dimension_tumour = models.IntegerField(null=True, blank=True)
    tumour_focality = models.CharField(max_length=64)
    residual_tumour_classification = models.CharField(max_length=64)
    margin_types_involved = models.CharField(max_length=128)
    margin_types_not_involved = models.CharField(max_length=128)
    margin_types_not_assessed = models.CharField(max_length=128)
    lymphovascular_invasion = models.CharField(max_length=255)
    perineural_invasion = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.id}"


class FollowUp(models.Model):
    submitter_follow_up_id = models.CharField(max_length=64, primary_key=True)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_primary_diagnosis_id = models.ForeignKey(
        PrimaryDiagnosis, on_delete=models.SET_NULL, blank=True, null=True
    )
    submitter_treatment_id = models.ForeignKey(
        Treatment, on_delete=models.SET_NULL, blank=True, null=True
    )
    date_of_followup = models.CharField(max_length=32, null=False, blank=False)
    lost_to_followup = models.BooleanField(null=True)
    lost_to_followup_reason = models.CharField(max_length=255)
    disease_status_at_followup = models.CharField(
        max_length=255, null=False, blank=False
    )
    relapse_type = models.CharField(max_length=128)
    date_of_relapse = models.CharField(max_length=32)
    method_of_progression_status = models.CharField(max_length=255)
    anatomic_site_progression_or_recurrence = models.CharField(max_length=255)
    recurrence_tumour_staging_system = models.CharField(max_length=255)
    recurrence_t_category = models.CharField(max_length=32)
    recurrence_n_category = models.CharField(max_length=32)
    recurrence_m_category = models.CharField(max_length=32)
    recurrence_stage_group = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.submitter_follow_up_id}"


class Biomarker(models.Model):
    id = models.AutoField(primary_key=True)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_specimen_id = models.ForeignKey(
        Specimen, on_delete=models.SET_NULL, blank=True, null=True
    )
    submitter_primary_diagnosis_id = models.ForeignKey(
        PrimaryDiagnosis, on_delete=models.SET_NULL, blank=True, null=True
    )
    submitter_treatment_id = models.ForeignKey(
        Treatment, on_delete=models.SET_NULL, blank=True, null=True
    )
    submitter_follow_up_id = models.ForeignKey(
        FollowUp, on_delete=models.SET_NULL, blank=True, null=True
    )
    test_interval = models.IntegerField(null=True, blank=True)
    psa_level = models.IntegerField(null=True, blank=True)
    ca125 = models.IntegerField(null=True, blank=True)
    cea = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.id}"


class Comorbidity(models.Model):
    id = models.AutoField(primary_key=True)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    prior_malignancy = models.CharField(max_length=32)
    laterality_of_prior_malignancy = models.CharField(max_length=64)
    age_at_comorbidity_diagnosis = models.IntegerField(null=True, blank=True)
    comorbidity_type_code = models.CharField(max_length=64)
    comorbidity_treatment_status = models.CharField(max_length=32)
    comorbidity_treatment = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.id}"
