from typing import List, Optional

from ninja import Field, ModelSchema, NinjaAPI, Schema

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


class DonorSchema(ModelSchema):
    class Config:
        model = Donor
        model_fields = "__all__"
