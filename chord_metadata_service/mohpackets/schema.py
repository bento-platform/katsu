from enum import Enum, IntEnum
from typing import Dict, List, Optional, Type

from ninja import Field, FilterSchema, ModelSchema, NinjaAPI, Query, Schema
from pydantic import BaseModel, constr

from chord_metadata_service.mohpackets.models import (
    Biomarker,
    Chemotherapy,
    Comorbidity,
    Donor,
    Exposure,
    FollowUp,
    HormoneTherapy,
    Immunotherapy,
    PrimaryDiagnosis,
    Program,
    Radiation,
    SampleRegistration,
    Specimen,
    Surgery,
    Treatment,
)
from chord_metadata_service.mohpackets.permissible_values import (
    COMORBIDITY_REGEX_PATTERNS,
    DATE_REGEX_PATTERNS,
    ID_REGEX_PATTERNS,
    MORPHOLOGY_REGEX_PATTERNS,
    TOPOGRAPHY_REGEX_PATTERNS,
    BasisOfDiagnosisEnum,
    CauseOfDeathEnum,
    CellsMeasureMethodEnum,
    ConfirmedDiagnosisTumourEnum,
    DiseaseStatusFollowupEnum,
    DosageUnitsEnum,
    DrugReferenceDbEnum,
    ErPrHpvStatusEnum,
    GenderEnum,
    Her2StatusEnum,
    HpvStrainEnum,
    ImmunotherapyTypeEnum,
    LostToFollowupReasonEnum,
    LymphNodeMethodEnum,
    LymphNodeStatusEnum,
    LymphovascularInvasionEnum,
    MalignancyLateralityEnum,
    MarginTypesEnum,
    MCategoryEnum,
    NCategoryEnum,
    PercentCellsRangeEnum,
    PerineuralInvasionEnum,
    PrimaryDiagnosisLateralityEnum,
    PrimarySiteEnum,
    ProgressionStatusMethodEnum,
    RadiationAnatomicalSiteEnum,
    RadiationTherapyModalityEnum,
    RelapseTypeEnum,
    SampleTypeEnum,
    SexAtBirthEnum,
    SmokingStatusEnum,
    SpecimenLateralityEnum,
    SpecimenProcessingEnum,
    SpecimenTissueSourceEnum,
    SpecimenTypeEnum,
    StageGroupEnum,
    StorageEnum,
    SurgeryLocationEnum,
    SurgeryTypeEnum,
    TCategoryEnum,
    TherapyTypeEnum,
    TobaccoTypeEnum,
    TreatmentIntentEnum,
    TreatmentResponseEnum,
    TreatmentResponseMethodEnum,
    TreatmentSettingEnum,
    TreatmentStatusEnum,
    TreatmentTypeEnum,
    TumourClassificationEnum,
    TumourDesginationEnum,
    TumourFocalityEnum,
    TumourGradeEnum,
    TumourGradingSystemEnum,
    TumourStagingSystemEnum,
    uBooleanEnum,
)


########################################
#                                      #
#           DISCOVERY SCHEMA           #
#                                      #
########################################
class ProgramDiscoverySchema(Schema):
    program_id: str


class DiscoverySchema(Schema):
    discovery_donor: Dict[str, int]


########################################
#                                      #
#           MODEL SCHEMA               #
#                                      #
########################################


class ProgramModelSchema(ModelSchema):
    class Config:
        model = Program
        model_fields = "__all__"


class ExposureModelSchema(ModelSchema):
    tobacco_smoking_status: Optional[SmokingStatusEnum] = None
    tobacco_type: Optional[List[TobaccoTypeEnum]] = None

    class Config:
        model = Exposure
        model_exclude = ["uuid", "donor_uuid"]


class ComorbidityModelSchema(ModelSchema):
    prior_malignancy: Optional[uBooleanEnum] = None
    laterality_of_prior_malignancy: Optional[MalignancyLateralityEnum] = None
    comorbidity_type_code: Optional[str] = Field(
        None, pattern=COMORBIDITY_REGEX_PATTERNS, max_length=64
    )
    comorbidity_treatment_status: Optional[uBooleanEnum] = None
    comorbidity_treatment: Optional[str] = Field(None, max_length=255)

    class Config:
        model = Comorbidity
        model_exclude = ["uuid", "donor_uuid"]


class BiomarkerModelSchema(ModelSchema):
    er_status: Optional[ErPrHpvStatusEnum] = None
    pr_status: Optional[ErPrHpvStatusEnum] = None
    her2_ihc_status: Optional[Her2StatusEnum] = None
    her2_ish_status: Optional[Her2StatusEnum] = None
    hpv_ihc_status: Optional[ErPrHpvStatusEnum] = None
    hpv_pcr_status: Optional[ErPrHpvStatusEnum] = None
    hpv_strain: Optional[List[HpvStrainEnum]] = None

    class Config:
        model = Biomarker
        model_exclude = ["uuid", "donor_uuid"]


class FollowUpModelSchema(ModelSchema):
    disease_status_at_followup: Optional[DiseaseStatusFollowupEnum] = None
    relapse_type: Optional[RelapseTypeEnum] = None
    date_of_relapse: Optional[str] = Field(
        None, pattern=DATE_REGEX_PATTERNS, max_length=32
    )
    method_of_progression_status: Optional[List[ProgressionStatusMethodEnum]] = None
    anatomic_site_progression_or_recurrence: Optional[List[str]] = None
    recurrence_tumour_staging_system: Optional[TumourStagingSystemEnum] = None
    recurrence_t_category: Optional[TCategoryEnum] = None
    recurrence_n_category: Optional[NCategoryEnum] = None
    recurrence_m_category: Optional[MCategoryEnum] = None
    recurrence_stage_group: Optional[StageGroupEnum] = None

    class Config:
        model = FollowUp
        model_exclude = ["uuid", "donor_uuid"]


class SurgeryModelSchema(ModelSchema):
    surgery_type: Optional[SurgeryTypeEnum] = None
    surgery_site: Optional[str] = Field(
        None, pattern=TOPOGRAPHY_REGEX_PATTERNS, max_length=255
    )
    surgery_location: Optional[SurgeryLocationEnum] = None
    tumour_focality: Optional[TumourFocalityEnum] = None
    residual_tumour_classification: Optional[TumourClassificationEnum] = None
    margin_types_involved: Optional[List[MarginTypesEnum]] = None
    margin_types_not_involved: Optional[List[MarginTypesEnum]] = None
    margin_types_not_assessed: Optional[List[MarginTypesEnum]] = None
    lymphovascular_invasion: Optional[LymphovascularInvasionEnum] = None
    perineural_invasion: Optional[PerineuralInvasionEnum] = None

    class Config:
        model = Surgery
        model_exclude = ["uuid", "donor_uuid"]


class ImmunotherapyModelSchema(ModelSchema):
    immunotherapy_type: Optional[ImmunotherapyTypeEnum] = None
    drug_reference_database: Optional[DrugReferenceDbEnum] = None
    immunotherapy_drug_dose_units: Optional[DosageUnitsEnum] = None

    class Config:
        model = Immunotherapy
        model_exclude = ["uuid", "donor_uuid"]


class RadiationModelSchema(ModelSchema):
    radiation_therapy_modality: Optional[RadiationTherapyModalityEnum] = None
    radiation_therapy_type: Optional[TherapyTypeEnum] = None
    anatomical_site_irradiated: Optional[RadiationAnatomicalSiteEnum] = None

    class Config:
        model = Radiation
        model_exclude = ["uuid", "donor_uuid"]


class HormoneTherapyModelSchema(ModelSchema):
    hormone_drug_dose_units: Optional[DosageUnitsEnum] = None
    drug_reference_database: Optional[DrugReferenceDbEnum] = None

    class Config:
        model = HormoneTherapy
        model_exclude = ["uuid", "donor_uuid"]


class ChemotherapyModelSchema(ModelSchema):
    chemotherapy_drug_dose_units: Optional[DosageUnitsEnum] = None
    drug_reference_database: Optional[DrugReferenceDbEnum] = None

    class Config:
        model = Chemotherapy
        model_exclude = ["uuid", "donor_uuid"]


class TreatmentModelSchema(ModelSchema):
    submitter_treatment_id: str = Field(pattern=ID_REGEX_PATTERNS, max_length=64)
    treatment_type: Optional[List[TreatmentTypeEnum]] = None
    is_primary_treatment: Optional[uBooleanEnum] = None
    treatment_start_date: Optional[str] = Field(
        None, pattern=DATE_REGEX_PATTERNS, max_length=32
    )
    treatment_end_date: Optional[str] = Field(
        None, pattern=DATE_REGEX_PATTERNS, max_length=32
    )
    treatment_setting: Optional[TreatmentSettingEnum] = None
    treatment_intent: Optional[TreatmentIntentEnum] = None
    response_to_treatment_criteria_method: Optional[TreatmentResponseMethodEnum] = None
    response_to_treatment: Optional[TreatmentResponseEnum] = None
    status_of_treatment: Optional[TreatmentStatusEnum] = None

    class Config:
        model = Treatment
        model_exclude = ["uuid", "donor_uuid"]


class PrimaryDiagnosisModelSchema(ModelSchema):
    submitter_primary_diagnosis_id: str = Field(
        pattern=ID_REGEX_PATTERNS, max_length=64
    )
    date_of_diagnosis: Optional[str] = Field(
        None, pattern=DATE_REGEX_PATTERNS, max_length=32
    )

    basis_of_diagnosis: Optional[BasisOfDiagnosisEnum] = None
    lymph_nodes_examined_status: Optional[LymphNodeStatusEnum] = None
    lymph_nodes_examined_method: Optional[LymphNodeMethodEnum] = None
    clinical_tumour_staging_system: Optional[TumourStagingSystemEnum] = None
    clinical_t_category: Optional[TCategoryEnum] = None
    clinical_n_category: Optional[NCategoryEnum] = None
    clinical_m_category: Optional[MCategoryEnum] = None
    clinical_stage_group: Optional[StageGroupEnum] = None
    laterality: Optional[PrimaryDiagnosisLateralityEnum] = None

    class Config:
        model = PrimaryDiagnosis
        model_exclude = ["uuid", "donor_uuid"]


class SampleRegistrationModelSchema(ModelSchema):
    submitter_sample_id: str = Field(pattern=ID_REGEX_PATTERNS, max_length=64)
    specimen_tissue_source: Optional[SpecimenTissueSourceEnum] = None
    tumour_normal_designation: Optional[TumourDesginationEnum] = None
    specimen_type: Optional[SpecimenTypeEnum] = None
    sample_type: Optional[SampleTypeEnum] = None

    class Config:
        model = SampleRegistration
        model_exclude = ["uuid", "donor_uuid"]


class SpecimenModelSchema(ModelSchema):
    submitter_specimen_id: str = Field(pattern=ID_REGEX_PATTERNS, max_length=64)
    pathological_tumour_staging_system: Optional[TumourStagingSystemEnum] = None
    pathological_t_category: Optional[TCategoryEnum] = None
    pathological_n_category: Optional[NCategoryEnum] = None
    pathological_m_category: Optional[MCategoryEnum] = None
    pathological_stage_group: Optional[StageGroupEnum] = None
    specimen_collection_date: Optional[str] = Field(
        None, pattern=DATE_REGEX_PATTERNS, max_length=32
    )
    specimen_storage: Optional[StorageEnum] = None
    tumour_histological_type: Optional[str] = Field(
        None, max_length=128, pattern=MORPHOLOGY_REGEX_PATTERNS
    )
    specimen_anatomic_location: Optional[str] = Field(
        None, max_length=32, pattern=TOPOGRAPHY_REGEX_PATTERNS
    )
    reference_pathology_confirmed_diagnosis: Optional[
        ConfirmedDiagnosisTumourEnum
    ] = None
    reference_pathology_confirmed_tumour_presence: Optional[
        ConfirmedDiagnosisTumourEnum
    ] = None
    tumour_grading_system: Optional[TumourGradingSystemEnum] = None
    tumour_grade: Optional[TumourGradeEnum] = None
    percent_tumour_cells_range: Optional[PercentCellsRangeEnum] = None
    percent_tumour_cells_measurement_method: Optional[CellsMeasureMethodEnum] = None
    specimen_processing: Optional[SpecimenProcessingEnum] = None
    specimen_laterality: Optional[SpecimenLateralityEnum] = None

    class Config:
        model = Specimen
        model_exclude = ["uuid", "donor_uuid"]


class DonorModelSchema(ModelSchema):
    cause_of_death: Optional[CauseOfDeathEnum] = None
    submitter_donor_id: str = Field(pattern=ID_REGEX_PATTERNS, max_length=64)
    date_of_birth: Optional[str] = Field(
        None, pattern=DATE_REGEX_PATTERNS, max_length=32
    )
    date_of_death: Optional[str] = Field(
        None, pattern=DATE_REGEX_PATTERNS, max_length=32
    )
    primary_site: Optional[List[PrimarySiteEnum]] = None
    gender: Optional[GenderEnum] = None
    sex_at_birth: Optional[SexAtBirthEnum] = None
    lost_to_followup_reason: Optional[LostToFollowupReasonEnum] = None
    date_alive_after_lost_to_followup: Optional[str] = Field(
        None, pattern=DATE_REGEX_PATTERNS, max_length=32
    )

    class Config:
        model = Donor
        model_exclude = ["uuid"]


#####################################################
#                                                   #
#           DONOR WITH CLINICAL SCHEMA              #
#                                                   #
#####################################################
class NestedExposureSchema(ModelSchema):
    class Config:
        model = Exposure
        model_exclude = [
            "uuid",
            "donor_uuid",
            "submitter_donor_id",
            "program_id",
        ]


class NestedComorbiditySchema(ModelSchema):
    class Config:
        model = Comorbidity
        model_exclude = [
            "uuid",
            "donor_uuid",
            "submitter_donor_id",
            "program_id",
        ]


class NestedChemotherapySchema(ModelSchema):
    class Config:
        model = Chemotherapy
        model_exclude = [
            "uuid",
            "donor_uuid",
            "submitter_donor_id",
            "program_id",
            "submitter_treatment_id",
            "treatment_uuid",
        ]


class NestedImmunotherapySchema(ModelSchema):
    class Config:
        model = Immunotherapy
        model_exclude = [
            "uuid",
            "donor_uuid",
            "submitter_donor_id",
            "program_id",
            "submitter_treatment_id",
            "treatment_uuid",
        ]


class NestedHormoneTherapySchema(ModelSchema):
    class Config:
        model = HormoneTherapy
        model_exclude = [
            "uuid",
            "donor_uuid",
            "submitter_donor_id",
            "program_id",
            "submitter_treatment_id",
            "treatment_uuid",
        ]


class NestedRadiationSchema(ModelSchema):
    class Config:
        model = Radiation
        model_exclude = [
            "uuid",
            "donor_uuid",
            "submitter_donor_id",
            "program_id",
            "submitter_treatment_id",
            "treatment_uuid",
        ]


class NestedSurgerySchema(ModelSchema):
    class Config:
        model = Surgery
        model_exclude = [
            "uuid",
            "donor_uuid",
            "submitter_donor_id",
            "program_id",
            "submitter_treatment_id",
            "treatment_uuid",
        ]


class NestedFollowUpSchema(Schema):
    class Config:
        model = FollowUp
        model_exclude = [
            "uuid",
            "donor_uuid",
            "submitter_donor_id",
            "program_id",
            "submitter_treatment_id",
            "submitter_primary_diagnosis_id",
            "primary_diagnosis_uuid",
            "treatment_uuid",
        ]


class NestedBiomarkerSchema(ModelSchema):
    class Config:
        model = Biomarker
        model_exclude = [
            "uuid",
            "donor_uuid",
            "submitter_donor_id",
            "program_id",
        ]


class NestedSampleRegistrationSchema(ModelSchema):
    class Config:
        model = SampleRegistration
        model_exclude = [
            "uuid",
            "donor_uuid",
            "submitter_donor_id",
            "program_id",
            "submitter_specimen_id",
            "specimen_uuid",
        ]


class NestedTreatmentSchema(ModelSchema):
    chemotherapies: List[NestedChemotherapySchema] = Field(
        ..., alias="chemotherapy_set"
    )
    immunotherapies: List[NestedImmunotherapySchema] = Field(
        ..., alias="immunotherapy_set"
    )
    hormonetherapies: List[NestedHormoneTherapySchema] = Field(
        ..., alias="hormonetherapy_set"
    )
    radiations: List[NestedRadiationSchema] = Field(..., alias="radiation_set")
    surgeries: List[NestedSurgerySchema] = Field(..., alias="surgery_set")
    followups: List[NestedFollowUpSchema] = Field(..., alias="followup_set")

    class Config:
        model = Treatment
        model_exclude = [
            "uuid",
            "donor_uuid",
            "submitter_donor_id",
            "program_id",
            "submitter_primary_diagnosis_id",
            "primary_diagnosis_uuid",
        ]


class NestedSpecimenSchema(ModelSchema):
    samplesregistrations: List[NestedSampleRegistrationSchema] = Field(
        ..., alias="sampleregistration_set"
    )

    class Config:
        model = Specimen
        model_exclude = [
            "uuid",
            "donor_uuid",
            "submitter_donor_id",
            "program_id",
            "submitter_primary_diagnosis_id",
            "primary_diagnosis_uuid",
        ]


class NestedPrimaryDiagnosisSchema(ModelSchema):
    specimens: List[NestedSpecimenSchema] = Field(..., alias="specimen_set")
    treatments: List[NestedTreatmentSchema] = Field(..., alias="treatment_set")
    followups: List[NestedFollowUpSchema] = Field(..., alias="followup_set")

    class Config:
        model = PrimaryDiagnosis
        model_exclude = ["uuid", "donor_uuid", "submitter_donor_id", "program_id"]


class DonorWithClinicalDataSchema(ModelSchema):
    comorbidities: List[NestedComorbiditySchema] = Field(..., alias="comorbidity_set")
    exposures: List[NestedExposureSchema] = Field(..., alias="exposure_set")
    biomarkers: List[NestedBiomarkerSchema] = Field(..., alias="biomarker_set")
    primarydiagnosis: List[NestedPrimaryDiagnosisSchema] = Field(
        ..., alias="primarydiagnosis_set"
    )
    followups: List[NestedFollowUpSchema] = Field(..., alias="followup_set")

    class Config:
        model = Donor
        model_exclude = ["uuid"]


########################################
#                                      #
#           INGEST SCHEMA              #
#                                      #
########################################
class DonorIngestSchema(ModelSchema):
    program_id_id: str = Field(..., alias="program_id")

    class Config:
        model = Donor
        model_exclude = ["uuid", "program_id"]


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
    is_deceased: Optional[bool] = Field(None)
    lost_to_followup_after_clinical_event_identifier: Optional[str] = Field(None)
    lost_to_followup_reason: Optional[str] = Field(None)
    date_alive_after_lost_to_followup: Optional[str] = Field(None)
    cause_of_death: Optional[str] = Field(None)
    date_of_birth: Optional[str] = Field(None)
    date_of_death: Optional[str] = Field(None)
    primary_site: List[str] = Field(None, q="primary_site__overlap")


class PrimaryDiagnosisFilterSchema(FilterSchema):
    submitter_primary_diagnosis_id: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    donor_uuid: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    date_of_diagnosis: Optional[str] = Field(None)
    cancer_type_code: Optional[str] = Field(None)
    basis_of_diagnosis: Optional[str] = Field(None)
    laterality: Optional[str] = Field(None)
    lymph_nodes_examined_status: Optional[str] = Field(None)
    lymph_nodes_examined_method: Optional[str] = Field(None)
    number_lymph_nodes_positive: Optional[int] = Field(None)
    clinical_tumour_staging_system: Optional[str] = Field(None)
    clinical_t_category: Optional[str] = Field(None)
    clinical_n_category: Optional[str] = Field(None)
    clinical_m_category: Optional[str] = Field(None)
    clinical_stage_group: Optional[str] = Field(None)


class SpecimenFilterSchema(FilterSchema):
    submitter_specimen_id: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_primary_diagnosis_id: Optional[str] = Field(None)
    pathological_tumour_staging_system: Optional[str] = Field(None)
    pathological_t_category: Optional[str] = Field(None)
    pathological_n_category: Optional[str] = Field(None)
    pathological_m_category: Optional[str] = Field(None)
    pathological_stage_group: Optional[str] = Field(None)
    specimen_collection_date: Optional[str] = Field(None)
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
    donor_uuid: Optional[str] = Field(None)
    specimen_uuid: Optional[str] = Field(None)
    submitter_sample_id: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_specimen_id: Optional[str] = Field(None)
    specimen_tissue_source: Optional[str] = Field(None)
    tumour_normal_designation: Optional[str] = Field(None)
    specimen_type: Optional[str] = Field(None)
    sample_type: Optional[str] = Field(None)


class TreatmentFilterSchema(FilterSchema):
    donor_uuid: Optional[str] = Field(None)
    primary_diagnosis_uuid: Optional[str] = Field(None)
    submitter_treatment_id: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_primary_diagnosis_id: Optional[str] = Field(None)
    treatment_type: List[str] = Field(None, q="treatment_type__overlap")
    is_primary_treatment: Optional[str] = Field(None)
    line_of_treatment: Optional[int] = Field(None)
    treatment_start_date: Optional[str] = Field(None)
    treatment_end_date: Optional[str] = Field(None)
    treatment_setting: Optional[str] = Field(None)
    treatment_intent: Optional[str] = Field(None)
    days_per_cycle: Optional[int] = Field(None)
    number_of_cycles: Optional[int] = Field(None)
    response_to_treatment_criteria_method: Optional[str] = Field(None)
    response_to_treatment: Optional[str] = Field(None)
    status_of_treatment: Optional[str] = Field(None)


class ChemotherapyFilterSchema(FilterSchema):
    donor_uuid: Optional[str] = Field(None)
    treatment_uuid: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_treatment_id: Optional[str] = Field(None)
    drug_reference_database: Optional[str] = Field(None)
    drug_name: Optional[str] = Field(None)
    drug_reference_identifier: Optional[str] = Field(None)
    chemotherapy_drug_dose_units: Optional[str] = Field(None)
    prescribed_cumulative_drug_dose: Optional[int] = Field(None)
    actual_cumulative_drug_dose: Optional[int] = Field(None)


class HormoneTherapyFilterSchema(FilterSchema):
    donor_uuid: Optional[str] = Field(None)
    treatment_uuid: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_treatment_id: Optional[str] = Field(None)
    drug_reference_database: Optional[str] = Field(None)
    drug_name: Optional[str] = Field(None)
    drug_reference_identifier: Optional[str] = Field(None)
    hormone_drug_dose_units: Optional[str] = Field(None)
    prescribed_cumulative_drug_dose: Optional[int] = Field(None)
    actual_cumulative_drug_dose: Optional[int] = Field(None)


class RadiationFilterSchema(FilterSchema):
    donor_uuid: Optional[str] = Field(None)
    treatment_uuid: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_treatment_id: Optional[str] = Field(None)
    radiation_therapy_modality: Optional[str] = Field(None)
    radiation_therapy_type: Optional[str] = Field(None)
    radiation_therapy_fractions: Optional[int] = Field(None)
    radiation_therapy_dosage: Optional[int] = Field(None)
    anatomical_site_irradiated: Optional[str] = Field(None)
    radiation_boost: Optional[bool] = Field(None)
    reference_radiation_treatment_id: Optional[str] = Field(None)


class ImmunotherapyFilterSchema(FilterSchema):
    donor_uuid: Optional[str] = Field(None)
    treatment_uuid: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_treatment_id: Optional[str] = Field(None)
    drug_reference_database: Optional[str] = Field(None)
    immunotherapy_type: Optional[str] = Field(None)
    drug_name: Optional[str] = Field(None)
    drug_reference_identifier: Optional[str] = Field(None)
    immunotherapy_drug_dose_units: Optional[str] = Field(None)
    prescribed_cumulative_drug_dose: Optional[int] = Field(None)
    actual_cumulative_drug_dose: Optional[int] = Field(None)


class SurgeryFilterSchema(FilterSchema):
    donor_uuid: Optional[str] = Field(None)
    treatment_uuid: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_treatment_id: Optional[str] = Field(None)
    submitter_specimen_id: Optional[str] = Field(None)
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


class FollowUpFilterSchema(FilterSchema):
    donor_uuid: Optional[str] = Field(None)
    treatment_uuid: Optional[str] = Field(None)
    primary_diagnosis_uuid: Optional[str] = Field(None)
    submitter_follow_up_id: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_primary_diagnosis_id: Optional[str] = Field(None)
    submitter_treatment_id: Optional[str] = Field(None)
    date_of_followup: Optional[str] = Field(None)
    disease_status_at_followup: Optional[str] = Field(None)
    relapse_type: Optional[str] = Field(None)
    date_of_relapse: Optional[str] = Field(None)
    method_of_progression_status: List[str] = Field(
        None, q="method_of_progression_status__overlap"
    )
    anatomic_site_progression_or_recurrence: List[str] = Field(
        None, q="anatomic_site_progression_or_recurrence__overlap"
    )
    recurrence_tumour_staging_system: Optional[str] = Field(None)
    recurrence_t_category: Optional[str] = Field(None)
    recurrence_n_category: Optional[str] = Field(None)
    recurrence_m_category: Optional[str] = Field(None)
    recurrence_stage_group: Optional[str] = Field(None)


class BiomarkerFilterSchema(FilterSchema):
    donor_uuid: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    submitter_specimen_id: Optional[str] = Field(None)
    submitter_primary_diagnosis_id: Optional[str] = Field(None)
    submitter_treatment_id: Optional[str] = Field(None)
    submitter_follow_up_id: Optional[str] = Field(None)
    test_date: Optional[str] = Field(None)
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
    donor_uuid: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    prior_malignancy: Optional[str] = Field(None)
    laterality_of_prior_malignancy: Optional[str] = Field(None)
    age_at_comorbidity_diagnosis: Optional[int] = Field(None)
    comorbidity_type_code: Optional[str] = Field(None)
    comorbidity_treatment_status: Optional[str] = Field(None)
    comorbidity_treatment: Optional[str] = Field(None)


class ExposureFilterSchema(FilterSchema):
    donor_uuid: Optional[str] = Field(None)
    program_id: Optional[str] = Field(None)
    submitter_donor_id: Optional[str] = Field(None)
    tobacco_smoking_status: Optional[str] = Field(None)
    tobacco_type: List[str] = Field(None, q="tobacco_type__overlap")
    pack_years_smoked: Optional[float] = Field(None)
