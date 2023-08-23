import datetime
import functools

from django.db.models import Q
from django_filters import rest_framework as filters

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
        fields = ["program_id"]


class DonorFilter(filters.FilterSet):
    # custom filters
    # NOTE: DonorFilter class is a special case that is allowed to be filtered by multiple ids
    # with case-insensitive matching since most of the queries happen here.
    # For example, writing either ID TREATMENT_1 or treatment_1 is acceptable.
    # Other class filters are not allowed to do this.

    primary_site = filters.CharFilter(lookup_expr="icontains")
    age = filters.NumberFilter(field_name="date_of_birth", method="filter_age")
    max_age = filters.NumberFilter(field_name="date_of_birth", method="filter_age__lt")
    min_age = filters.NumberFilter(field_name="date_of_birth", method="filter_age__gt")
    donors = filters.CharFilter(method="filter_donors")
    primary_diagnosis = filters.CharFilter(method="filter_primary_diagnosis")
    speciman = filters.CharFilter(method="filter_specimen")
    treatment = filters.CharFilter(method="filter_treatment")
    chemotherapy = filters.CharFilter(method="filter_chemotherapy")
    hormone_therapy = filters.CharFilter(method="filter_hormone_therapy")
    radiation = filters.CharFilter(method="filter_radiation")
    immunotherapy = filters.CharFilter(method="filter_immunotherapy")
    surgery = filters.CharFilter(method="filter_surgery")
    follow_up = filters.CharFilter(method="filter_follow_up")
    biomarker = filters.CharFilter(method="filter_biomarker")
    comorbidity = filters.CharFilter(method="filter_comorbidity")
    exposure = filters.CharFilter(method="filter_exposure")

    def filter_donors(self, queryset, name, value):
        """
        This function allows us to filter by multiple donor ids.
        Since we cannot use "iexact" together with "in" filter,
        we have to convert it to a list of Q objects like this:
        MyModel.objects.filter(Q(name__iexact='Alpha') | Q(name__iexact='bEtA') | ...)
        """
        donor_ids_list = [x.strip() for x in value.split(",")]
        q_list = map(lambda n: Q(pk__iexact=n), donor_ids_list)
        q_list = functools.reduce(lambda a, b: a | b, q_list)
        return queryset.filter(q_list)

    def filter_primary_diagnosis(self, queryset, name, value):
        return queryset.filter(primarydiagnosis__pk__iexact=value)

    def filter_specimen(self, queryset, name, value):
        return queryset.filter(specimen__pk__iexact=value)

    def filter_treatment(self, queryset, name, value):
        return queryset.filter(treatment__pk__iexact=value)

    def filter_chemotherapy(self, queryset, name, value):
        return queryset.filter(chemotherapy__pk__iexact=value)

    def filter_hormone_therapy(self, queryset, name, value):
        return queryset.filter(hormonetherapy__pk__iexact=value)

    def filter_radiation(self, queryset, name, value):
        return queryset.filter(radiation__pk__iexact=value)

    def filter_immunotherapy(self, queryset, name, value):
        return queryset.filter(immunotherapy__pk__iexact=value)

    def filter_surgery(self, queryset, name, value):
        return queryset.filter(surgery__pk__iexact=value)

    def filter_follow_up(self, queryset, name, value):
        return queryset.filter(followup__pk__iexact=value)

    def filter_biomarker(self, queryset, name, value):
        return queryset.filter(biomarker__pk__iexact=value)

    def filter_comorbidity(self, queryset, name, value):
        return queryset.filter(comorbidity__pk__iexact=value)

    def filter_exposure(self, queryset, name, value):
        return queryset.filter(exposure__pk__iexact=value)

    def filter_age(self, queryset, name, value):
        """
        Since date_of_birth is a CharField, we can't use the built-in filter.
        We do it by looking up if date_of_birth contains a particular year. eg 1971
        """
        year = datetime.datetime.now().year - int(value)
        return queryset.filter(date_of_birth__icontains=year)

    def filter_age__lt(self, queryset, name, value):
        """
        Since date_of_birth is a CharField, we can't use the built-in filter.
        We do it by looking up if date_of_birth contains any year in the range
        from the current year to the specified year. eg [1971,1972,1973,...]
        """
        year = datetime.datetime.now().year - int(value)
        years = [year for year in range(year, datetime.datetime.now().year)]
        # this is a fancy way to write
        # Q(name__contains=list[0]) | Q(name__contains=list[1]) | ... | Q(name__contains=list[-1])
        query = functools.reduce(
            lambda x, y: x | y, [Q(date_of_birth__icontains=year) for year in years]
        )

        return queryset.filter(query)

    def filter_age__gt(self, queryset, name, value):
        """
        Since date_of_birth is a CharField, we can't use the built-in filter.
        We do it by looking up if date_of_birth contains any year in the range
        from 1900 to the specified year. eg [1900,1901,1902,...]
        """
        year = datetime.datetime.now().year - int(value)
        years = [year for year in range(1900, year)]
        query = functools.reduce(
            lambda x, y: x | y, [Q(date_of_birth__icontains=year) for year in years]
        )

        return queryset.filter(query)

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
    treatment_type = filters.CharFilter(lookup_expr="icontains")

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
    margin_types_involved = filters.CharFilter(lookup_expr="icontains")
    margin_types_not_involved = filters.CharFilter(lookup_expr="icontains")
    margin_types_not_assessed = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Surgery
        fields = "__all__"


class FollowUpFilter(filters.FilterSet):
    method_of_progression_status = filters.CharFilter(lookup_expr="icontains")
    anatomic_site_progression_or_recurrence = filters.CharFilter(
        lookup_expr="icontains"
    )

    class Meta:
        model = FollowUp
        fields = "__all__"


class BiomarkerFilter(filters.FilterSet):
    hpv_strain = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Biomarker
        fields = "__all__"


class ComorbidityFilter(filters.FilterSet):
    class Meta:
        model = Comorbidity
        fields = "__all__"


class ExposureFilter(filters.FilterSet):
    tobacco_type = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Exposure
        fields = "__all__"
