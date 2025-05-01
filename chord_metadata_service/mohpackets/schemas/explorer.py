from typing import List, Optional

from ninja import Field, Schema

from chord_metadata_service.mohpackets.permissible_values import ID_REGEX

"""
Module with schema used for explorer response

Author: Son Chau
"""


class DonorExplorerSchema(Schema):
    program_id: str = Field(pattern=ID_REGEX, max_length=64)
    submitter_donor_id: str = Field(pattern=ID_REGEX, max_length=64)
    submitter_sample_ids: Optional[List[str]]
    primary_site: Optional[List[str]] = None
    treatment_type: Optional[List[str]] = None
    age_at_diagnosis: Optional[str] = None
