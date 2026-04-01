from typing import Optional

from ninja import Field
from pydantic import ConfigDict

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
Module with schema used for ingesting

All fields are derived from the model but FK and uuid

Author: Son Chau
"""


########################################
#                                      #
#           INGEST SCHEMA              #
#                                      #
########################################


class ProgramIngestSchema(BaseProgramSchema):
    pass


class DonorIngestSchema(BaseDonorSchema):
    model_config = ConfigDict(use_enum_values=True)
    program_id_id: str = Field(..., alias="program_id")
    uuid: Optional[str] = None


class PrimaryDiagnosisIngestSchema(BasePrimaryDiagnosisSchema):
    model_config = ConfigDict(use_enum_values=True)
    program_id_id: str = Field(..., alias="program_id")
    submitter_donor_id: str
    uuid: Optional[str] = None


class BiomarkerIngestSchema(BaseBiomarkerSchema):
    model_config = ConfigDict(use_enum_values=True)
    program_id_id: str = Field(..., alias="program_id")
    submitter_donor_id: str
    uuid: Optional[str] = None


class SystemicTherapyIngestSchema(BaseSystemicTherapySchema):
    model_config = ConfigDict(use_enum_values=True)
    program_id_id: str = Field(..., alias="program_id")
    submitter_donor_id: str
    submitter_treatment_id: str
    uuid: Optional[str] = None


class ComorbidityIngestSchema(BaseComorbiditySchema):
    model_config = ConfigDict(use_enum_values=True)
    program_id_id: str = Field(..., alias="program_id")
    submitter_donor_id: str
    uuid: Optional[str] = None


class ExposureIngestSchema(BaseExposureSchema):
    model_config = ConfigDict(use_enum_values=True)
    program_id_id: str = Field(..., alias="program_id")
    submitter_donor_id: str
    uuid: Optional[str] = None


class FollowUpIngestSchema(BaseFollowUpSchema):
    model_config = ConfigDict(use_enum_values=True)
    program_id_id: str = Field(..., alias="program_id")
    submitter_donor_id: str
    submitter_primary_diagnosis_id: Optional[str] = None
    submitter_treatment_id: Optional[str] = None
    uuid: Optional[str] = None


class RadiationIngestSchema(BaseRadiationSchema):
    model_config = ConfigDict(use_enum_values=True)
    program_id_id: str = Field(..., alias="program_id")
    submitter_donor_id: str
    submitter_treatment_id: str
    uuid: Optional[str] = None


class SampleRegistrationIngestSchema(BaseSampleRegistrationSchema):
    model_config = ConfigDict(use_enum_values=True)
    program_id_id: str = Field(..., alias="program_id")
    submitter_donor_id: str
    submitter_specimen_id: str
    uuid: Optional[str] = None


class SpecimenIngestSchema(BaseSpecimenSchema):
    model_config = ConfigDict(use_enum_values=True)
    program_id_id: str = Field(..., alias="program_id")
    submitter_donor_id: str
    submitter_primary_diagnosis_id: str
    uuid: Optional[str] = None


class SurgeryIngestSchema(BaseSurgerySchema):
    model_config = ConfigDict(use_enum_values=True)
    program_id_id: str = Field(..., alias="program_id")
    submitter_donor_id: str
    submitter_treatment_id: str
    uuid: Optional[str] = None


class TreatmentIngestSchema(BaseTreatmentSchema):
    model_config = ConfigDict(use_enum_values=True)
    program_id_id: str = Field(..., alias="program_id")
    submitter_donor_id: str
    submitter_primary_diagnosis_id: str
    uuid: Optional[str] = None
