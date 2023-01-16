import django_filters
from django.db.models import Q
from django.db.models import TextField
from django.db.models.functions import Cast
from django.contrib.postgres.search import SearchVector
from .models import Individual


class IndividualFilter(django_filters.rest_framework.FilterSet):
    id = django_filters.AllValuesMultipleFilter()
    alternate_ids = django_filters.CharFilter(lookup_expr="icontains")
    sex = django_filters.CharFilter(lookup_expr="iexact")
    karyotypic_sex = django_filters.CharFilter(lookup_expr="iexact")
    ethnicity = django_filters.CharFilter(lookup_expr="icontains")
    race = django_filters.CharFilter(lookup_expr="icontains")
    disease = django_filters.CharFilter(
        method="filter_disease", field_name="phenopackets__diseases", label="Disease"
    )
    # e.g. select all patients who have a symptom "dry cough"
    found_phenotypic_feature = django_filters.CharFilter(
        method="filter_found_phenotypic_feature",
        field_name="phenopackets__phenotypic_features",
        label="Found phenotypic feature",
    )

    extra_properties = django_filters.CharFilter(
        method="filter_extra_properties", label="Extra properties"
    )
    # full-text search at api/individuals?search=
    search = django_filters.CharFilter(method="filter_search", label="Search")

    # e.g. date_of_birth_after=1987-01-01&date_of_birth_before=1990-12-31
    date_of_birth = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Individual
        fields = [
            "id",
            "alternate_ids",
            "active",
            "deceased",
            "phenopackets__biosamples",
            "phenopackets",
        ]

    def filter_found_phenotypic_feature(self, qs, name, value):
        """
        Filters only found (present in a patient) Phenotypic features by id or label
        """
        qs = qs.filter(
            Q(phenopackets__phenotypic_features__pftype__id__icontains=value)
            | Q(phenopackets__phenotypic_features__pftype__label__icontains=value),
            phenopackets__phenotypic_features__negated=False,
        ).distinct()
        return qs

    def filter_disease(self, qs, name, value):
        qs = qs.filter(
            Q(phenopackets__diseases__term__id__icontains=value)
            | Q(phenopackets__diseases__term__label__icontains=value)
        ).distinct()
        return qs

    def filter_extra_properties(self, qs, name, value):
        return qs.filter(extra_properties__icontains=value)

    def filter_search(self, qs, name, value):
        # creates index in db
        qs = (
            qs.annotate(
                search=SearchVector(
                    "id",
                    "alternate_ids",
                    "date_of_birth",
                    Cast("age", TextField()),
                    "sex",
                    "karyotypic_sex",
                    Cast("taxonomy", TextField()),
                    Cast("comorbid_condition", TextField()),
                    Cast("ecog_performance_status", TextField()),
                    Cast("karnofsky", TextField()),
                    "ethnicity",
                    "race",
                    Cast("extra_properties", TextField()),
                    # Phenotypic feature fields
                    "phenopackets__phenotypic_features__description",
                    Cast("phenopackets__phenotypic_features__pftype", TextField()),
                    Cast("phenopackets__phenotypic_features__severity", TextField()),
                    Cast("phenopackets__phenotypic_features__modifier", TextField()),
                    Cast("phenopackets__phenotypic_features__onset", TextField()),
                    Cast("phenopackets__phenotypic_features__evidence", TextField()),
                    Cast(
                        "phenopackets__phenotypic_features__extra_properties",
                        TextField(),
                    ),
                    # Biosample fields
                    "phenopackets__biosamples__id",
                    "phenopackets__biosamples__description",
                    Cast("phenopackets__biosamples__sampled_tissue", TextField()),
                    Cast("phenopackets__biosamples__taxonomy", TextField()),
                    Cast(
                        "phenopackets__biosamples__individual_age_at_collection",
                        TextField(),
                    ),
                    Cast(
                        "phenopackets__biosamples__histological_diagnosis", TextField()
                    ),
                    Cast("phenopackets__biosamples__tumor_progression", TextField()),
                    Cast("phenopackets__biosamples__tumor_grade", TextField()),
                    Cast("phenopackets__biosamples__diagnostic_markers", TextField()),
                    # Biosample Procedure fields
                    Cast("phenopackets__biosamples__procedure__code", TextField()),
                    Cast("phenopackets__biosamples__procedure__body_site", TextField()),
                    Cast(
                        "phenopackets__biosamples__procedure__extra_properties",
                        TextField(),
                    ),
                    Cast("phenopackets__biosamples__extra_properties", TextField()),
                    # Biosample Variant fields
                    "phenopackets__biosamples__variants__allele_type",
                    Cast("phenopackets__biosamples__variants__allele", TextField()),
                    Cast("phenopackets__biosamples__variants__zygosity", TextField()),
                    Cast(
                        "phenopackets__biosamples__variants__extra_properties",
                        TextField(),
                    ),
                    # Biosample HTS file fields
                    "phenopackets__biosamples__hts_files__uri",
                    "phenopackets__biosamples__hts_files__description",
                    "phenopackets__biosamples__hts_files__hts_format",
                    "phenopackets__biosamples__hts_files__genome_assembly",
                    Cast(
                        "phenopackets__biosamples__hts_files__individual_to_sample_identifiers",
                        TextField(),
                    ),
                    Cast(
                        "phenopackets__biosamples__hts_files__extra_properties",
                        TextField(),
                    ),
                    # Gene fields
                    "phenopackets__genes__id",
                    "phenopackets__genes__alternate_ids",
                    "phenopackets__genes__symbol",
                    Cast("phenopackets__genes__extra_properties", TextField()),
                    # Variant fields
                    "phenopackets__variants__allele_type",
                    Cast("phenopackets__variants__allele", TextField()),
                    Cast("phenopackets__variants__zygosity", TextField()),
                    Cast("phenopackets__variants__extra_properties", TextField()),
                    # Disease field
                    Cast("phenopackets__diseases__term", TextField()),
                    Cast("phenopackets__diseases__onset", TextField()),
                    Cast("phenopackets__diseases__disease_stage", TextField()),
                    Cast("phenopackets__diseases__tnm_finding", TextField()),
                    Cast("phenopackets__diseases__extra_properties", TextField()),
                    # HTS file fields
                    "phenopackets__hts_files__uri",
                    "phenopackets__hts_files__description",
                    "phenopackets__hts_files__hts_format",
                    "phenopackets__hts_files__genome_assembly",
                    Cast(
                        "phenopackets__hts_files__individual_to_sample_identifiers",
                        TextField(),
                    ),
                    Cast("phenopackets__hts_files__extra_properties", TextField()),
                    # Experiment fields
                    "phenopackets__biosamples__experiment__study_type",
                    "phenopackets__biosamples__experiment__experiment_type",
                    Cast(
                        "phenopackets__biosamples__experiment__experiment_ontology",
                        TextField(),
                    ),
                    "phenopackets__biosamples__experiment__molecule",
                    Cast(
                        "phenopackets__biosamples__experiment__molecule_ontology",
                        TextField(),
                    ),
                    "phenopackets__biosamples__experiment__library_strategy",
                    "phenopackets__biosamples__experiment__library_source",
                    "phenopackets__biosamples__experiment__library_selection",
                    "phenopackets__biosamples__experiment__library_layout",
                    "phenopackets__biosamples__experiment__extraction_protocol",
                    "phenopackets__biosamples__experiment__reference_registry_id",
                    Cast(
                        "phenopackets__biosamples__experiment__extra_properties",
                        TextField(),
                    ),
                    # Experiments: Experiment Results fields
                    "phenopackets__biosamples__experiment__experiment_results__description",
                    "phenopackets__biosamples__experiment__experiment_results__filename",
                    "phenopackets__biosamples__experiment__experiment_results__file_format",
                    "phenopackets__biosamples__experiment__experiment_results__data_output_type",
                    "phenopackets__biosamples__experiment__experiment_results__usage",
                    "phenopackets__biosamples__experiment__experiment_results__creation_date",
                    "phenopackets__biosamples__experiment__experiment_results__created_by",
                    Cast(
                        "phenopackets__biosamples__experiment__experiment_results__extra_properties",
                        TextField(),
                    ),
                    # Experiments: Instrument fields
                    "phenopackets__biosamples__experiment__instrument__platform",
                    "phenopackets__biosamples__experiment__instrument__description",
                    "phenopackets__biosamples__experiment__instrument__model",
                    Cast(
                        "phenopackets__biosamples__experiment__instrument__extra_properties",
                        TextField(),
                    ),
                )
            )
            .filter(search=value)
            .distinct("id")
        )
        return qs
