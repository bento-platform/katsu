from typing import List, Optional, Dict
from ninja import Schema
from chord_metadata_service.mohpackets.schemas.model import (
    BiomarkerModelSchema,
    ComorbidityModelSchema,
    DonorModelSchema,
    ExposureModelSchema,
    FollowUpModelSchema,
    PrimaryDiagnosisModelSchema,
    RadiationModelSchema,
    SampleRegistrationModelSchema,
    SpecimenModelSchema,
    SurgeryModelSchema,
    SystemicTherapyModelSchema,
    TreatmentModelSchema,
)

class AllModelsSchema(Schema):
    donors: List[DonorModelSchema]
    primary_diagnoses: List[PrimaryDiagnosisModelSchema]
    specimens: List[SpecimenModelSchema]
    sample_registrations: List[SampleRegistrationModelSchema]
    treatments: List[TreatmentModelSchema]
    systemic_therapies: List[SystemicTherapyModelSchema]
    radiations: List[RadiationModelSchema]
    surgeries: List[SurgeryModelSchema]
    follow_ups: List[FollowUpModelSchema]
    biomarkers: List[BiomarkerModelSchema]
    comorbidities: List[ComorbidityModelSchema]
    exposures: List[ExposureModelSchema]


class SummaryMessageSchema(Schema):
    message: str
    record_counts: Dict[str, int]


class DownloadResponseSchema(Schema):
    summary: SummaryMessageSchema
    data: Optional[AllModelsSchema] = None
