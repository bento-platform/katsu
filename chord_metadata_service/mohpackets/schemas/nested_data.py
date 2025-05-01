from typing import List

from ninja import Field

from chord_metadata_service.mohpackets.schemas.base import (
    BaseBiomarkerSchema,
    BaseComorbiditySchema,
    BaseDonorSchema,
    BaseExposureSchema,
    BaseFollowUpSchema,
    BasePrimaryDiagnosisSchema,
    BaseRadiationSchema,
    BaseSampleRegistrationSchema,
    BaseSpecimenSchema,
    BaseSurgerySchema,
    BaseSystemicTherapySchema,
    BaseTreatmentSchema,
)

"""
Schemas for nested donor with clinical models, inherted from base schemas.

Donor would include other models, exclude the FKs.

Author: Son Chau
"""

#####################################################
#                                                   #
#           DONOR WITH CLINICAL SCHEMA              #
#                                                   #
#####################################################


class NestedExposureSchema(BaseExposureSchema):
    pass


class NestedComorbiditySchema(BaseComorbiditySchema):
    pass


class NestedSystemicTherapySchema(BaseSystemicTherapySchema):
    pass


class NestedRadiationSchema(BaseRadiationSchema):
    pass


class NestedSurgerySchema(BaseSurgerySchema):
    pass


class NestedFollowUpSchema(BaseFollowUpSchema):
    pass


class NestedBiomarkerSchema(BaseBiomarkerSchema):
    pass


class NestedSampleRegistrationSchema(BaseSampleRegistrationSchema):
    pass


class NestedTreatmentSchema(BaseTreatmentSchema):
    systemic_therapies: List[NestedSystemicTherapySchema] = Field(
        None, alias="systemictherapy_set"
    )
    radiations: List[NestedRadiationSchema] = Field(None, alias="radiation_set")
    surgeries: List[NestedSurgerySchema] = Field(None, alias="surgery_set")
    followups: List[NestedFollowUpSchema] = Field(None, alias="followup_set")


class NestedSpecimenSchema(BaseSpecimenSchema):
    sample_registrations: List[NestedSampleRegistrationSchema] = Field(
        None, alias="sampleregistration_set"
    )


class NestedPrimaryDiagnosisSchema(BasePrimaryDiagnosisSchema):
    specimens: List[NestedSpecimenSchema] = Field(None, alias="specimen_set")
    treatments: List[NestedTreatmentSchema] = Field(None, alias="treatment_set")
    followups: List[NestedFollowUpSchema] = Field(None, alias="followup_set")


class DonorWithClinicalDataSchema(BaseDonorSchema):
    program_id: str = Field(..., alias="program_id_id")
    primary_diagnoses: List[NestedPrimaryDiagnosisSchema] = Field(
        None, alias="primarydiagnosis_set"
    )
    followups: List[NestedFollowUpSchema] = Field(None, alias="followup_set")
    biomarkers: List[NestedBiomarkerSchema] = Field(None, alias="biomarker_set")
    exposures: List[NestedExposureSchema] = Field(None, alias="exposure_set")
    comorbidities: List[NestedComorbiditySchema] = Field(None, alias="comorbidity_set")
