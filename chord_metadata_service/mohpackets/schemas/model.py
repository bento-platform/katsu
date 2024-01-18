from typing import Optional

from ninja import Field

from chord_metadata_service.mohpackets.schemas.base import (
    BaseBiomarkerSchema,
    BaseChemotherapySchema,
    BaseComorbiditySchema,
    BaseDonorSchema,
    BaseExposureSchema,
    BaseFollowUpSchema,
    BaseHormoneTherapySchema,
    BaseImmunotherapySchema,
    BasePrimaryDiagnosisSchema,
    BaseProgramSchema,
    BaseRadiationSchema,
    BaseSampleRegistrationSchema,
    BaseSpecimenSchema,
    BaseSurgerySchema,
    BaseTreatmentSchema,
)


"""
Schemas for clinical models, inherted from base schemas.

Added "foreign keys" to link between models

Author: Son Chau
"""

########################################
#                                      #
#           MODEL SCHEMA               #
#                                      #
########################################


class ProgramModelSchema(BaseProgramSchema):
    pass


class DonorModelSchema(BaseDonorSchema):
    program_id: str = Field(..., alias="program_id_id")


class PrimaryDiagnosisModelSchema(BasePrimaryDiagnosisSchema):
    program_id: str = Field(..., alias="program_id_id")
    submitter_donor_id: str


class SpecimenModelSchema(BaseSpecimenSchema):
    program_id: str = Field(..., alias="program_id_id")
    submitter_donor_id: str
    submitter_primary_diagnosis_id: str


class SampleRegistrationModelSchema(BaseSampleRegistrationSchema):
    program_id: str = Field(..., alias="program_id_id")
    submitter_donor_id: str
    submitter_specimen_id: str


class TreatmentModelSchema(BaseTreatmentSchema):
    program_id: str = Field(..., alias="program_id_id")
    submitter_donor_id: str
    submitter_primary_diagnosis_id: str


class SurgeryModelSchema(BaseSurgerySchema):
    program_id: str = Field(..., alias="program_id_id")
    submitter_donor_id: str
    submitter_treatment_id: str


class ImmunotherapyModelSchema(BaseImmunotherapySchema):
    program_id: str = Field(..., alias="program_id_id")
    submitter_donor_id: str
    submitter_treatment_id: str


class RadiationModelSchema(BaseRadiationSchema):
    program_id: str = Field(..., alias="program_id_id")
    submitter_donor_id: str
    submitter_treatment_id: str


class HormoneTherapyModelSchema(BaseHormoneTherapySchema):
    program_id: str = Field(..., alias="program_id_id")
    submitter_donor_id: str
    submitter_treatment_id: str


class ChemotherapyModelSchema(BaseChemotherapySchema):
    program_id: str = Field(..., alias="program_id_id")
    submitter_donor_id: str
    submitter_treatment_id: str


class FollowUpModelSchema(BaseFollowUpSchema):
    program_id: str = Field(..., alias="program_id_id")
    submitter_donor_id: str
    submitter_primary_diagnosis_id: Optional[str] = None
    submitter_treatment_id: Optional[str] = None


class BiomarkerModelSchema(BaseBiomarkerSchema):
    program_id: str = Field(..., alias="program_id_id")
    submitter_donor_id: str


class ExposureModelSchema(BaseExposureSchema):
    program_id: str = Field(..., alias="program_id_id")
    submitter_donor_id: str


class ComorbidityModelSchema(BaseComorbiditySchema):
    program_id: str = Field(..., alias="program_id_id")
    submitter_donor_id: str
