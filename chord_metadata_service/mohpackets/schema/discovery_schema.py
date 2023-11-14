from typing import Dict, List

from ninja import Schema

"""
*** DISCOVERY SCHEMA ****

Contains schemas for discovery APIs, 
used to convert Python objects or Django model instances into JSON strings.
"""


class ProgramDiscoverySchema(Schema):
    cohort_list: List[str]


class DiscoverySchema(Schema):
    donors_by_cohort: Dict[str, int]
