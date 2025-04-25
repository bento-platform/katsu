from typing import List, Optional

from ninja import Field, FilterSchema

"""
Module with schema used for filtering

Author: Son Chau
"""


########################################
#                                      #
#           FILTER SCHEMA              #
#                                      #
########################################
class ProgramFilterSchema(FilterSchema):
    program_id: Optional[str] = Field(None)


class DonorFilterSchema(FilterSchema):
    submitter_donor_id: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    gender: Optional[str] = Field(None, q="gender__icontains")
    sex_at_birth: Optional[str] = Field(None)
    is_deceased: Optional[str] = Field(None)
    lost_to_followup_after_clinical_event_identifier: Optional[str] = Field(None)
    lost_to_followup_reason: Optional[str] = Field(None)
    cause_of_death: Optional[str] = Field(None)


class PrimaryDiagnosisFilterSchema(FilterSchema):
    submitter_primary_diagnosis_id: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    cancer_type_code: Optional[str] = Field(None)
    basis_of_diagnosis: Optional[str] = Field(None)
    laterality: Optional[str] = Field(None)
    clinical_tumour_staging_system: Optional[str] = Field(None)
    clinical_t_category: Optional[str] = Field(None)
    clinical_n_category: Optional[str] = Field(None)
    clinical_m_category: Optional[str] = Field(None)
    clinical_stage_group: Optional[str] = Field(None)
    primary_site: Optional[str] = Field(None)
    pathological_tumour_staging_system: Optional[str] = Field(None)
    pathological_t_category: Optional[str] = Field(None)
    pathological_n_category: Optional[str] = Field(None)
    pathological_m_category: Optional[str] = Field(None)
    pathological_stage_group: Optional[str] = Field(None)


class SpecimenFilterSchema(FilterSchema):
    submitter_specimen_id: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_primary_diagnosis_id: Optional[str] = Field(None)
    submitter_treatment_id: Optional[str] = Field(None)
    specimen_storage: Optional[str] = Field(None)
    specimen_processing: Optional[str] = Field(None)
    tumour_histological_type: Optional[str] = Field(None)
    specimen_anatomic_location: Optional[str] = Field(None)
    specimen_laterality: Optional[str] = Field(None)
    reference_pathology_confirmed_diagnosis: Optional[str] = Field(None)
    reference_pathology_confirmed_tumour_presence: Optional[str] = Field(None)
    tumour_grading_system: Optional[str] = Field(None)
    tumour_grade: Optional[str] = Field(None)
    percent_tumour_cells_range: Optional[str] = Field(None)
    percent_tumour_cells_measurement_method: Optional[str] = Field(None)


class SampleRegistrationFilterSchema(FilterSchema):
    submitter_sample_id: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_specimen_id: Optional[str] = Field(None)
    specimen_tissue_source: Optional[str] = Field(None)
    tumour_normal_designation: Optional[str] = Field(None)
    specimen_type: Optional[str] = Field(None)
    sample_type: Optional[str] = Field(None)


class TreatmentFilterSchema(FilterSchema):
    submitter_treatment_id: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_primary_diagnosis_id: Optional[str] = Field(None)
    treatment_type: List[str] = Field(None, q="treatment_type__overlap")
    is_primary_treatment: Optional[str] = Field(None)
    treatment_intent: Optional[str] = Field(None)
    response_to_treatment_criteria_method: Optional[str] = Field(None)
    response_to_treatment: Optional[str] = Field(None)
    status_of_treatment: Optional[str] = Field(None)


class SystemicTherapyFilterSchema(FilterSchema):
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_treatment_id: Optional[str] = Field(None)
    drug_reference_database: Optional[str] = Field(None)
    drug_name: Optional[str] = Field(None)
    drug_reference_identifier: Optional[str] = Field(None)
    drug_dose_units: Optional[str] = Field(None)
    prescribed_cumulative_drug_dose: Optional[int] = Field(None)
    actual_cumulative_drug_dose: Optional[int] = Field(None)
    days_per_cycle: Optional[int] = Field(None)
    number_of_cycles: Optional[int] = Field(None)
    systemic_therapy_type: Optional[str] = Field(None)


class RadiationFilterSchema(FilterSchema):
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_treatment_id: Optional[str] = Field(None)
    radiation_therapy_modality: Optional[str] = Field(None)
    radiation_therapy_type: Optional[str] = Field(None)
    radiation_therapy_fractions: Optional[int] = Field(None)
    radiation_therapy_dosage: Optional[int] = Field(None)
    anatomical_site_irradiated: Optional[str] = Field(None)
    radiation_boost: Optional[str] = Field(None)
    reference_radiation_treatment_id: Optional[str] = Field(None)


class SurgeryFilterSchema(FilterSchema):
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_treatment_id: Optional[str] = Field(None)
    surgery_type: Optional[str] = Field(None)
    surgery_site: Optional[str] = Field(None)
    surgery_location: Optional[str] = Field(None)
    tumour_length: Optional[int] = Field(None)
    tumour_width: Optional[int] = Field(None)
    greatest_dimension_tumour: Optional[int] = Field(None)
    tumour_focality: Optional[str] = Field(None)
    residual_tumour_classification: Optional[str] = Field(None)
    margin_types_involved: List[str] = Field(None, q="margin_types_involved__overlap")
    margin_types_not_involved: List[str] = Field(
        None, q="margin_types_not_involved__overlap"
    )
    margin_types_not_assessed: List[str] = Field(
        None, q="margin_types_not_assessed__overlap"
    )
    lymphovascular_invasion: Optional[str] = Field(None)
    perineural_invasion: Optional[str] = Field(None)
    surgery_reference_database: Optional[str] = Field(None)
    surgery_reference_identifier: Optional[str] = Field(None)


class FollowUpFilterSchema(FilterSchema):
    submitter_follow_up_id: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_primary_diagnosis_id: Optional[str] = Field(None)
    submitter_treatment_id: Optional[str] = Field(None)
    disease_status_at_followup: Optional[str] = Field(None)
    relapse_type: Optional[str] = Field(None)
    method_of_progression_status: List[str] = Field(
        None, q="method_of_progression_status__overlap"
    )
    anatomic_site_progression_or_recurrence: List[str] = Field(
        None, q="anatomic_site_progression_or_recurrence__overlap"
    )


class BiomarkerFilterSchema(FilterSchema):
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_specimen_id: Optional[str] = Field(None)
    submitter_primary_diagnosis_id: Optional[str] = Field(None)
    submitter_treatment_id: Optional[str] = Field(None)
    submitter_follow_up_id: Optional[str] = Field(None)
    psa_level: Optional[int] = Field(None)
    ca125: Optional[int] = Field(None)
    cea: Optional[int] = Field(None)
    er_status: Optional[str] = Field(None)
    er_percent_positive: Optional[float] = Field(None)
    pr_status: Optional[str] = Field(None)
    pr_percent_positive: Optional[float] = Field(None)
    her2_ihc_status: Optional[str] = Field(None)
    her2_ish_status: Optional[str] = Field(None)
    hpv_ihc_status: Optional[str] = Field(None)
    hpv_pcr_status: Optional[str] = Field(None)
    hpv_strain: List[str] = Field(None, q="hpv_strain__overlap")


class ComorbidityFilterSchema(FilterSchema):
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    prior_malignancy: Optional[str] = Field(None)
    laterality_of_prior_malignancy: Optional[str] = Field(None)
    age_at_comorbidity_diagnosis: Optional[int] = Field(None)
    comorbidity_type_code: Optional[str] = Field(None)
    comorbidity_treatment_status: Optional[str] = Field(None)
    comorbidity_treatment: Optional[str] = Field(None)


class ExposureFilterSchema(FilterSchema):
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    tobacco_smoking_status: Optional[str] = Field(None)
    tobacco_type: List[str] = Field(None, q="tobacco_type__overlap")
    pack_years_smoked: Optional[float] = Field(None)


class DonorWithClinicalDataFilterSchema(FilterSchema):
    submitter_donor_id: str
    program_id: str


class DonorExplorerFilterSchema(FilterSchema):
    treatment_type: List[str] = Field(None, q="treatment_type__overlap")
    primary_site: List[str] = Field(None)
    systemic_therapy_drug_name: List[str] = Field(None)
    exclude_programs: List[str] = Field(None)

class DownloadFilterSchema(FilterSchema):
    treatment_type: List[str] = Field(None, q="treatment_type__overlap")
    primary_site: List[str] = Field(None)
    systemic_therapy_drug_name: List[str] = Field(None)
    program_id: List[str] = Field(None)
    biosample_id: List[str] = Field(None)
    summary_only: bool = Field(
        False,
        description="If true, only summary data will be returned. "
        "If false, detailed data will be returned.",
    )