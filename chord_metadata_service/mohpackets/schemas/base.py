from typing import List, Optional

from ninja import Field, Schema
from ninja.orm import create_schema

from chord_metadata_service.mohpackets.models import (
    Biomarker,
    Comorbidity,
    Donor,
    Exposure,
    FollowUp,
    PrimaryDiagnosis,
    Program,
    Radiation,
    SampleRegistration,
    Specimen,
    Surgery,
    SystemicTherapy,
    Treatment,
)
from chord_metadata_service.mohpackets.permissible_values import (
    COMORBIDITY_REGEX,
    ID_REGEX,
    MORPHOLOGY_REGEX,
    TOPOGRAPHY_REGEX,
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
    LostToFollowupReasonEnum,
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
    SurgeryReferenceDatabaseEnum,
    TCategoryEnum,
    TherapyTypeEnum,
    TobaccoTypeEnum,
    TreatmentIntentEnum,
    TreatmentResponseEnum,
    TreatmentResponseMethodEnum,
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

"""
Module containing base schemas for clinical data models.

All fields are derived from the model, excluding 'uuid'.
Basic validations, such as regex and permissible choices, are included.

Author: Son Chau
"""

########################################
#                                      #
#           BASE SCHEMA                #
#                                      #
########################################


class DateInterval(Schema):
    day_interval: Optional[int] = Field(
        None, description="number of days since first diagnosis"
    )
    month_interval: int = Field(
        ..., description="number of months since first diagnosis"
    )


BaseProgramSchema = create_schema(
    Program,
    name="BaseProgramSchema",
    custom_fields=[
        ("program_id", str, Field(pattern=ID_REGEX, max_length=64)),
    ],
)

BaseDonorSchema = create_schema(
    Donor,
    name="BaseDonorSchema",
    exclude=["uuid", "program_id"],
    custom_fields=[
        ("cause_of_death", Optional[CauseOfDeathEnum], None),
        ("is_deceased", Optional[uBooleanEnum], None),
        ("submitter_donor_id", str, Field(pattern=ID_REGEX, max_length=64)),
        ("date_of_birth", Optional[DateInterval], None),
        ("date_of_death", Optional[DateInterval], None),
        ("gender", Optional[GenderEnum], None),
        ("sex_at_birth", Optional[SexAtBirthEnum], None),
        ("lost_to_followup_reason", Optional[LostToFollowupReasonEnum], None),
        ("date_alive_after_lost_to_followup", Optional[DateInterval], None),
    ],
)

BasePrimaryDiagnosisSchema = create_schema(
    PrimaryDiagnosis,
    name="BasePrimaryDiagnosisSchema",
    exclude=["uuid", "donor_uuid", "submitter_donor_id", "program_id"],
    custom_fields=[
        (
            "submitter_primary_diagnosis_id",
            str,
            Field(pattern=ID_REGEX, max_length=64),
        ),
        ("date_of_diagnosis", Optional[DateInterval], None),
        ("basis_of_diagnosis", Optional[BasisOfDiagnosisEnum], None),
        ("clinical_tumour_staging_system", Optional[TumourStagingSystemEnum], None),
        ("clinical_t_category", Optional[TCategoryEnum], None),
        ("clinical_n_category", Optional[NCategoryEnum], None),
        ("clinical_m_category", Optional[MCategoryEnum], None),
        ("clinical_stage_group", Optional[StageGroupEnum], None),
        ("laterality", Optional[PrimaryDiagnosisLateralityEnum], None),
        ("primary_site", Optional[PrimarySiteEnum], None),
        ("pathological_tumour_staging_system", Optional[TumourStagingSystemEnum], None),
        ("pathological_t_category", Optional[TCategoryEnum], None),
        ("pathological_n_category", Optional[NCategoryEnum], None),
        ("pathological_m_category", Optional[MCategoryEnum], None),
        ("pathological_stage_group", Optional[StageGroupEnum], None),
    ],
)

BaseSpecimenSchema = create_schema(
    Specimen,
    name="BaseSpecimenSchema",
    exclude=[
        "uuid",
        "donor_uuid",
        "submitter_donor_id",
        "program_id",
        "submitter_primary_diagnosis_id",
        "primary_diagnosis_uuid",
    ],
    custom_fields=[
        ("submitter_specimen_id", str, Field(pattern=ID_REGEX, max_length=64)),
        ("specimen_storage", Optional[StorageEnum], None),
        (
            "tumour_histological_type",
            Optional[str],
            Field(None, max_length=128, pattern=MORPHOLOGY_REGEX),
        ),
        (
            "specimen_anatomic_location",
            Optional[str],
            Field(None, max_length=32, pattern=TOPOGRAPHY_REGEX),
        ),
        (
            "reference_pathology_confirmed_diagnosis",
            Optional[ConfirmedDiagnosisTumourEnum],
            None,
        ),
        (
            "reference_pathology_confirmed_tumour_presence",
            Optional[ConfirmedDiagnosisTumourEnum],
            None,
        ),
        ("tumour_grading_system", Optional[TumourGradingSystemEnum], None),
        ("tumour_grade", Optional[TumourGradeEnum], None),
        ("percent_tumour_cells_range", Optional[PercentCellsRangeEnum], None),
        (
            "percent_tumour_cells_measurement_method",
            Optional[CellsMeasureMethodEnum],
            None,
        ),
        ("specimen_processing", Optional[SpecimenProcessingEnum], None),
        ("specimen_laterality", Optional[SpecimenLateralityEnum], None),
    ],
)

BaseSampleRegistrationSchema = create_schema(
    SampleRegistration,
    name="BaseSampleRegistrationSchema",
    exclude=[
        "uuid",
        "donor_uuid",
        "submitter_donor_id",
        "program_id",
        "submitter_specimen_id",
        "specimen_uuid",
    ],
    custom_fields=[
        ("submitter_sample_id", str, Field(pattern=ID_REGEX, max_length=64)),
        ("specimen_tissue_source", Optional[SpecimenTissueSourceEnum], None),
        ("tumour_normal_designation", Optional[TumourDesginationEnum], None),
        ("specimen_type", Optional[SpecimenTypeEnum], None),
        ("sample_type", Optional[SampleTypeEnum], None),
    ],
)

BaseTreatmentSchema = create_schema(
    Treatment,
    name="BaseTreatmentSchema",
    exclude=[
        "uuid",
        "donor_uuid",
        "submitter_donor_id",
        "program_id",
        "submitter_primary_diagnosis_id",
        "primary_diagnosis_uuid",
    ],
    custom_fields=[
        (
            "submitter_treatment_id",
            str,
            Field(pattern=ID_REGEX, max_length=64),
        ),
        ("treatment_type", Optional[List[TreatmentTypeEnum]], None),
        ("is_primary_treatment", Optional[uBooleanEnum], None),
        ("treatment_start_date", Optional[DateInterval], None),
        ("treatment_end_date", Optional[DateInterval], None),
        ("treatment_intent", Optional[TreatmentIntentEnum], None),
        (
            "response_to_treatment_criteria_method",
            Optional[TreatmentResponseMethodEnum],
            None,
        ),
        ("response_to_treatment", Optional[TreatmentResponseEnum], None),
        ("status_of_treatment", Optional[TreatmentStatusEnum], None),
    ],
)

BaseSystemicTherapySchema = create_schema(
    SystemicTherapy,
    name="BaseSystemicTherapySchema",
    exclude=[
        "uuid",
        "donor_uuid",
        "submitter_donor_id",
        "program_id",
        "submitter_treatment_id",
        "treatment_uuid",
    ],
    custom_fields=[
        ("drug_dose_units", Optional[DosageUnitsEnum], None),
        ("drug_reference_database", Optional[DrugReferenceDbEnum], None),
    ],
)


BaseRadiationSchema = create_schema(
    Radiation,
    name="BaseRadiationSchema",
    exclude=[
        "uuid",
        "donor_uuid",
        "submitter_donor_id",
        "program_id",
        "submitter_treatment_id",
        "treatment_uuid",
    ],
    custom_fields=[
        ("radiation_therapy_modality", Optional[RadiationTherapyModalityEnum], None),
        ("radiation_therapy_type", Optional[TherapyTypeEnum], None),
        ("anatomical_site_irradiated", Optional[RadiationAnatomicalSiteEnum], None),
        ("radiation_boost", Optional[uBooleanEnum], None),
    ],
)


BaseSurgerySchema = create_schema(
    Surgery,
    name="BaseSurgerySchema",
    exclude=[
        "uuid",
        "donor_uuid",
        "submitter_donor_id",
        "program_id",
        "submitter_treatment_id",
        "treatment_uuid",
    ],
    custom_fields=[
        (
            "surgery_site",
            Optional[str],
            Field(None, pattern=TOPOGRAPHY_REGEX, max_length=255),
        ),
        ("surgery_location", Optional[SurgeryLocationEnum], None),
        ("tumour_focality", Optional[TumourFocalityEnum], None),
        ("residual_tumour_classification", Optional[TumourClassificationEnum], None),
        ("margin_types_involved", Optional[List[MarginTypesEnum]], None),
        ("margin_types_not_involved", Optional[List[MarginTypesEnum]], None),
        ("margin_types_not_assessed", Optional[List[MarginTypesEnum]], None),
        ("lymphovascular_invasion", Optional[LymphovascularInvasionEnum], None),
        ("perineural_invasion", Optional[PerineuralInvasionEnum], None),
        ("surgery_reference_database", Optional[SurgeryReferenceDatabaseEnum], None),
    ],
)

BaseFollowUpSchema = create_schema(
    FollowUp,
    name="BaseFollowUpSchema",
    exclude=[
        "uuid",
        "donor_uuid",
        "submitter_donor_id",
        "program_id",
        "submitter_treatment_id",
        "submitter_primary_diagnosis_id",
        "primary_diagnosis_uuid",
        "treatment_uuid",
    ],
    custom_fields=[
        (
            "submitter_follow_up_id",
            str,
            Field(pattern=ID_REGEX, max_length=64),
        ),
        ("disease_status_at_followup", Optional[DiseaseStatusFollowupEnum], None),
        ("relapse_type", Optional[RelapseTypeEnum], None),
        ("date_of_followup", Optional[DateInterval], None),
        ("date_of_relapse", Optional[DateInterval], None),
        (
            "method_of_progression_status",
            Optional[List[ProgressionStatusMethodEnum]],
            None,
        ),
        ("anatomic_site_progression_or_recurrence", Optional[List[str]], None),
    ],
)

BaseBiomarkerSchema = create_schema(
    Biomarker,
    name="BaseBiomarkerSchema",
    exclude=["uuid", "donor_uuid", "submitter_donor_id", "program_id"],
    custom_fields=[
        ("er_status", Optional[ErPrHpvStatusEnum], None),
        ("pr_status", Optional[ErPrHpvStatusEnum], None),
        ("her2_ihc_status", Optional[Her2StatusEnum], None),
        ("her2_ish_status", Optional[Her2StatusEnum], None),
        ("hpv_ihc_status", Optional[ErPrHpvStatusEnum], None),
        ("hpv_pcr_status", Optional[ErPrHpvStatusEnum], None),
        ("hpv_strain", Optional[List[HpvStrainEnum]], None),
        ("test_date", Optional[DateInterval], None),
    ],
)

BaseComorbiditySchema = create_schema(
    Comorbidity,
    name="BaseComorbiditySchema",
    exclude=["uuid", "donor_uuid", "submitter_donor_id", "program_id"],
    custom_fields=[
        ("prior_malignancy", Optional[uBooleanEnum], None),
        ("laterality_of_prior_malignancy", Optional[MalignancyLateralityEnum], None),
        (
            "comorbidity_type_code",
            Optional[str],
            Field(None, pattern=COMORBIDITY_REGEX, max_length=64),
        ),
        ("comorbidity_treatment_status", Optional[uBooleanEnum], None),
        ("comorbidity_treatment", Optional[str], Field(None, max_length=255)),
    ],
)

BaseExposureSchema = create_schema(
    Exposure,
    name="BaseExposureSchema",
    exclude=["uuid", "donor_uuid", "submitter_donor_id", "program_id"],
    custom_fields=[
        ("tobacco_smoking_status", Optional[SmokingStatusEnum], None),
        ("tobacco_type", Optional[List[TobaccoTypeEnum]], None),
    ],
)
