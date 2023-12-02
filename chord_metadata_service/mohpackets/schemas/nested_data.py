from typing import List

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
    Radiation,
    SampleRegistration,
    Specimen,
    Surgery,
    Treatment,
)


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


class NestedFollowUpSchema(ModelSchema):
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
        None, alias="chemotherapy_set"
    )
    immunotherapies: List[NestedImmunotherapySchema] = Field(
        None, alias="immunotherapy_set"
    )
    hormone_therapies: List[NestedHormoneTherapySchema] = Field(
        None, alias="hormonetherapy_set"
    )
    radiations: List[NestedRadiationSchema] = Field(None, alias="radiation_set")
    surgeries: List[NestedSurgerySchema] = Field(None, alias="surgery_set")
    followups: List[NestedFollowUpSchema] = Field(None, alias="followup_set")

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
    sample_registrations: List[NestedSampleRegistrationSchema] = Field(
        None, alias="sampleregistration_set"
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
    specimens: List[NestedSpecimenSchema] = Field(None, alias="specimen_set")
    treatments: List[NestedTreatmentSchema] = Field(None, alias="treatment_set")
    followups: List[NestedFollowUpSchema] = Field(None, alias="followup_set")

    class Config:
        model = PrimaryDiagnosis
        model_exclude = ["uuid", "donor_uuid", "submitter_donor_id", "program_id"]


class DonorWithClinicalDataSchema(ModelSchema):
    primary_diagnoses: List[NestedPrimaryDiagnosisSchema] = Field(
        None, alias="primarydiagnosis_set"
    )
    followups: List[NestedFollowUpSchema] = Field(None, alias="followup_set")
    biomarkers: List[NestedBiomarkerSchema] = Field(None, alias="biomarker_set")
    exposures: List[NestedExposureSchema] = Field(None, alias="exposure_set")
    comorbidities: List[NestedComorbiditySchema] = Field(None, alias="comorbidity_set")

    class Config:
        model = Donor
        model_exclude = ["uuid"]
