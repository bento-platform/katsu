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
    REGEX_PATTERNS,
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
    TobaccoTypeEnum,
    TreatmentIntentEnum,
    TreatmentResponseEnum,
    TreatmentResponseMethodEnum,
    TreatmentSettingEnum,
    TreatmentStatusEnum,
    TreatmentTypeEnum,
    TumourClassificationEnum,
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
class ExposureSchema(ModelSchema):
    class Config:
        model = Exposure
        model_fields = "__all__"


class ComorbiditySchema(ModelSchema):
    class Config:
        model = Comorbidity
        model_fields = "__all__"


class SampleRegistrationSchema(ModelSchema):
    class Config:
        model = SampleRegistration
        model_fields = "__all__"


class SpecimenSchema(ModelSchema):
    samplesregistrations: List[SampleRegistrationSchema] = Field(
        ..., alias="sampleregistration_set"
    )

    class Config:
        model = Specimen
        model_fields = "__all__"


class ChemotherapySchema(ModelSchema):
    class Config:
        model = Chemotherapy
        model_fields = "__all__"


class ImmunotherapySchema(ModelSchema):
    class Config:
        model = Immunotherapy
        model_fields = "__all__"


class HormoneTherapySchema(ModelSchema):
    class Config:
        model = HormoneTherapy
        model_fields = "__all__"


class RadiationSchema(ModelSchema):
    class Config:
        model = Radiation
        model_fields = "__all__"


class SurgerySchema(ModelSchema):
    class Config:
        model = Surgery
        model_fields = "__all__"


class FollowUpSchema(Schema):
    class Config:
        model = FollowUp
        model_fields = "__all__"


class TreatmentSchema(ModelSchema):
    chemotherapies: List[ChemotherapySchema] = Field(..., alias="chemotherapy_set")
    immunotherapies: List[ImmunotherapySchema] = Field(..., alias="immunotherapy_set")
    hormonetherapies: List[HormoneTherapySchema] = Field(
        ..., alias="hormonetherapy_set"
    )
    radiations: List[RadiationSchema] = Field(..., alias="radiation_set")
    surgeries: List[SurgerySchema] = Field(..., alias="surgery_set")
    followups: List[FollowUpSchema] = Field(..., alias="followup_set")

    class Config:
        model = Treatment
        model_fields = "__all__"


class PrimaryDiagnosisSchema(ModelSchema):
    specimens: List[SpecimenSchema] = Field(..., alias="specimen_set")
    treatments: List[TreatmentSchema] = Field(..., alias="treatment_set")
    followups: List[FollowUpSchema] = Field(..., alias="followup_set")

    class Config:
        model = PrimaryDiagnosis
        model_fields = "__all__"


class BiomarkerSchema(ModelSchema):
    class Config:
        model = Biomarker
        model_fields = "__all__"


class DonorSchema(ModelSchema):
    cause_of_death: Optional[CauseOfDeathEnum] = None
    submitter_donor_id: str = Field(pattern=REGEX_PATTERNS["ID"], max_length=64)
    date_of_birth: Optional[str] = Field(
        None, pattern=REGEX_PATTERNS["DATE"], max_length=32
    )
    date_of_death: Optional[str] = Field(
        None, pattern=REGEX_PATTERNS["DATE"], max_length=32
    )
    primary_site: Optional[List[PrimarySiteEnum]] = None

    class Config:
        model = Donor
        model_exclude = ["uuid"]


#####################################################
#                                                   #
#           DONOR WITH CLINICAL SCHEMA              #
#                                                   #
#####################################################


class DonorWithClinicalDataSchema(ModelSchema):
    comorbidities: List[ComorbiditySchema] = Field(..., alias="comorbidity_set")
    exposures: List[ExposureSchema] = Field(..., alias="exposure_set")
    biomarkers: List[BiomarkerSchema] = Field(..., alias="biomarker_set")
    primarydiagnosis: List[PrimaryDiagnosisSchema] = Field(
        ..., alias="primarydiagnosis_set"
    )
    followups: List[FollowUpSchema] = Field(..., alias="followup_set")

    class Config:
        model = Donor
        model_fields = "__all__"


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
