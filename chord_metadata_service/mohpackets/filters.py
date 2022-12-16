import datetime
from django_filters import rest_framework as filters
import functools
from django.db.models import Q

from chord_metadata_service.mohpackets.models import (
    Program,
    Donor,
    Specimen,
    SampleRegistration,
    PrimaryDiagnosis,
    Treatment,
    Chemotherapy,
    HormoneTherapy,
    Radiation,
    Immunotherapy,
    Surgery,
    FollowUp,
    Biomarker,
    Comorbidity,
)

"""
    This module contains the FILTERS for the models in the mohpackets app.
    Filtering data changes queryset that is used to build a custom API response. 
    For example, we can filter the results by "male" or "female".
    
    We use the FilterSet class, which can automatically pick up fields from
    a model and allow simple equality-based filtering, and we can add custom 
    fields with more complex rules. For reference, see:
    https://django-filter.readthedocs.io/en/stable/ref/filterset.html
    
"""


class ProgramFilter(filters.FilterSet):
    class Meta:
        model = Program
        fields = "__all__"


class DonorFilter(filters.FilterSet):
    class Meta:
        model = Donor
        fields = "__all__"


class SpecimenFilter(filters.FilterSet):
    class Meta:
        model = Specimen
        fields = "__all__"


class SampleRegistrationFilter(filters.FilterSet):
    class Meta:
        model = SampleRegistration
        fields = "__all__"


class PrimaryDiagnosisFilter(filters.FilterSet):
    class Meta:
        model = PrimaryDiagnosis
        fields = "__all__"


class TreatmentFilter(filters.FilterSet):
    class Meta:
        model = Treatment
        fields = "__all__"


class ChemotherapyFilter(filters.FilterSet):
    class Meta:
        model = Chemotherapy
        fields = "__all__"


class HormoneTherapyFilter(filters.FilterSet):
    class Meta:
        model = HormoneTherapy
        fields = "__all__"


class RadiationFilter(filters.FilterSet):
    class Meta:
        model = Radiation
        fields = "__all__"


class ImmunotherapyFilter(filters.FilterSet):
    class Meta:
        model = Immunotherapy
        fields = "__all__"


class SurgeryFilter(filters.FilterSet):
    class Meta:
        model = Surgery
        fields = "__all__"


class FollowUpFilter(filters.FilterSet):
    class Meta:
        model = FollowUp
        fields = "__all__"


class BiomarkerFilter(filters.FilterSet):
    class Meta:
        model = Biomarker
        fields = "__all__"


class ComorbidityFilter(filters.FilterSet):
    class Meta:
        model = Comorbidity
        fields = "__all__"
