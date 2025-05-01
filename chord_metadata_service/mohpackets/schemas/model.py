from typing import List, Optional

from ninja import Field

from chord_metadata_service.mohpackets.schemas.base import (
    BaseBiomarkerSchema,
    BaseComorbiditySchema,
    BaseDonorSchema,
    BaseExposureSchema,
    BaseFollowUpSchema,
    BasePrimaryDiagnosisSchema,
    BaseProgramSchema,
    BaseRadiationSchema,
    BaseSampleRegistrationSchema,
    BaseSpecimenSchema,
    BaseSurgerySchema,
    BaseSystemicTherapySchema,
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


class QueryDonorSchema(BaseDonorSchema):
    program_id: str = Field(..., alias="program_id_id")
    primary_site: Optional[List[str]] = None
    treatment_type: Optional[List[str]] = None
    submitter_sample_ids: Optional[List[str]] = None


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


class RadiationModelSchema(BaseRadiationSchema):
    program_id: str = Field(..., alias="program_id_id")
    submitter_donor_id: str
    submitter_treatment_id: str


class SystemicTherapyModelSchema(BaseSystemicTherapySchema):
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
