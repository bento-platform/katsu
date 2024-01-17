from typing import Optional

from ninja import Field, ModelSchema
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
from chord_metadata_service.mohpackets.permissible_values import GenderEnum

"""
Module with schema used for ingesting

All fields are derived from the model, with the fix for FK and uuid

Author: Son Chau
"""


########################################
#                                      #
#           INGEST SCHEMA              #
#                                      #
########################################


class ProgramIngestSchema(ModelSchema):
    class Meta:
        model = Program
        fields = "__all__"


class DonorIngestSchema(ModelSchema):
    program_id_id: str = Field(..., alias="program_id")
    uuid: Optional[str] = None
    gender: Optional[GenderEnum] = None

    class Config:
        model = Donor
        model_exclude = ["uuid", "program_id"]
        use_enum_values = True


class PrimaryDiagnosisIngestSchema(ModelSchema):
    program_id_id: str = Field(..., alias="program_id")
    uuid: Optional[str] = None

    class Config:
        model = PrimaryDiagnosis
        model_exclude = [
            "uuid",
            "program_id",
            "donor_uuid",
        ]


class BiomarkerIngestSchema(ModelSchema):
    program_id_id: str = Field(..., alias="program_id")
    uuid: Optional[str] = None

    class Config:
        model = Biomarker
        model_exclude = [
            "uuid",
            "program_id",
            "donor_uuid",
        ]


class ChemotherapyIngestSchema(ModelSchema):
    program_id_id: str = Field(..., alias="program_id")
    uuid: Optional[str] = None

    class Config:
        model = Chemotherapy
        model_exclude = [
            "uuid",
            "program_id",
            "donor_uuid",
            "treatment_uuid",
        ]


class ComorbidityIngestSchema(ModelSchema):
    program_id_id: str = Field(..., alias="program_id")
    uuid: Optional[str] = None

    class Config:
        model = Comorbidity
        model_exclude = [
            "uuid",
            "program_id",
            "donor_uuid",
        ]


class ExposureIngestSchema(ModelSchema):
    program_id_id: str = Field(..., alias="program_id")
    uuid: Optional[str] = None

    class Config:
        model = Exposure
        model_exclude = [
            "uuid",
            "program_id",
            "donor_uuid",
        ]


class FollowUpIngestSchema(ModelSchema):
    program_id_id: str = Field(..., alias="program_id")
    uuid: Optional[str] = None

    class Config:
        model = FollowUp
        model_exclude = [
            "uuid",
            "program_id",
            "donor_uuid",
        ]


class HormoneTherapyIngestSchema(ModelSchema):
    program_id_id: str = Field(..., alias="program_id")
    uuid: Optional[str] = None

    class Config:
        model = HormoneTherapy
        model_exclude = [
            "uuid",
            "program_id",
            "donor_uuid",
            "treatment_uuid",
        ]


class ImmunotherapyIngestSchema(ModelSchema):
    program_id_id: str = Field(..., alias="program_id")
    uuid: Optional[str] = None

    class Config:
        model = Immunotherapy
        model_exclude = [
            "uuid",
            "program_id",
            "donor_uuid",
            "treatment_uuid",
        ]


class RadiationIngestSchema(ModelSchema):
    program_id_id: str = Field(..., alias="program_id")
    uuid: Optional[str] = None

    class Config:
        model = Radiation
        model_exclude = [
            "uuid",
            "program_id",
            "donor_uuid",
            "treatment_uuid",
        ]


class SampleRegistrationIngestSchema(ModelSchema):
    program_id_id: str = Field(..., alias="program_id")
    uuid: Optional[str] = None

    class Config:
        model = SampleRegistration
        model_exclude = [
            "uuid",
            "program_id",
            "donor_uuid",
            "specimen_uuid",
        ]


class SpecimenIngestSchema(ModelSchema):
    program_id_id: str = Field(..., alias="program_id")
    uuid: Optional[str] = None

    class Config:
        model = Specimen
        model_exclude = [
            "uuid",
            "program_id",
            "donor_uuid",
            "primary_diagnosis_uuid",
        ]


class SurgeryIngestSchema(ModelSchema):
    program_id_id: str = Field(..., alias="program_id")
    uuid: Optional[str] = None

    class Config:
        model = Surgery
        model_exclude = [
            "uuid",
            "program_id",
            "donor_uuid",
            "treatment_uuid",
        ]


class TreatmentIngestSchema(ModelSchema):
    program_id_id: str = Field(..., alias="program_id")
    uuid: Optional[str] = None

    class Config:
        model = Treatment
        model_exclude = [
            "uuid",
            "program_id",
            "donor_uuid",
            "primary_diagnosis_uuid",
        ]
