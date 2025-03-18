from typing import Optional

from ninja import Schema

"""
Module with schema used for discovery response

Author: Son Chau
"""


class ProgramDiscoverySchema(Schema):
    program_id: str
    metadata: object


class DiscoveryDonorSchema(Schema):
    program_id: str
    donors_count: str


class PatientPerProgramSchema(Schema):
    program_id: str
    patients_count: str


class GenderCountSchema(Schema):
    gender: Optional[str]
    gender_count: str


class PrimarySiteCountSchema(Schema):
    primary_site_name: Optional[str]
    primary_site_count: str


class TreatmentTypeCountSchema(Schema):
    treatment_type_name: str
    treatment_type_count: str


class DiagnosisAgeCountSchema(Schema):
    age_at_diagnosis: str
    age_count: str
