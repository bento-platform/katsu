import django_filters
from django.db.models import Q
from django.db.models import TextField, BooleanField
from django.db.models.functions import Cast
from django.contrib.postgres.search import SearchVector
from .models import Individual

GENOMIC_INTERPRETATION_QUERY = "phenopackets__interpretations__diagnosis__genomic_interpretations"
GENE_DESCRIPTOR_QUERY = f"{GENOMIC_INTERPRETATION_QUERY}__gene_descriptor"
VARIANT_INTERPRETATION_QUERY = f"{GENOMIC_INTERPRETATION_QUERY}__variant_interpretation"
VARIATION_DESCRIPTOR_QUERY = f"{VARIANT_INTERPRETATION_QUERY}__variation_descriptor"


class IndividualFilter(django_filters.rest_framework.FilterSet):
    id = django_filters.AllValuesMultipleFilter()
    alternate_ids = django_filters.CharFilter(lookup_expr="icontains")
    sex = django_filters.CharFilter(lookup_expr="iexact")
    karyotypic_sex = django_filters.CharFilter(lookup_expr="iexact")
    disease = django_filters.CharFilter(
        method="filter_disease", field_name="phenopackets__diseases",
        label="Disease")
    # e.g. select all patients who have a symptom "dry cough"
    found_phenotypic_feature = django_filters.CharFilter(
        method="filter_found_phenotypic_feature", field_name="phenopackets__phenotypic_features",
        label="Found phenotypic feature"
    )

    extra_properties = django_filters.CharFilter(method="filter_extra_properties", label="Extra properties")
    # full-text search at api/individuals?search=
    search = django_filters.CharFilter(method="filter_search", label="Search")

    # e.g. date_of_birth_after=1987-01-01&date_of_birth_before=1990-12-31
    date_of_birth = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Individual
        fields = ["id", "alternate_ids", "active", "deceased",
                  "phenopackets__biosamples", "phenopackets"]

    def filter_found_phenotypic_feature(self, qs, name, value):
        """
        Filters only found (present in a patient) Phenotypic features by id or label
        """
        qs = qs.filter(
            Q(phenopackets__phenotypic_features__pftype__id__icontains=value) |
            Q(phenopackets__phenotypic_features__pftype__label__icontains=value),
            phenopackets__phenotypic_features__excluded=False
        ).distinct()
        return qs

    def filter_disease(self, qs, name, value):
        qs = qs.filter(
            Q(phenopackets__diseases__term__id__icontains=value) |
            Q(phenopackets__diseases__term__label__icontains=value)
        ).distinct()
        return qs

    def filter_extra_properties(self, qs, name, value):
        return qs.filter(extra_properties__icontains=value)

    def filter_search(self, qs, name, value):
        # creates index in db
        qs = qs.annotate(
            search=SearchVector("id", "alternate_ids", "date_of_birth",
                                Cast("time_at_last_encounter", TextField()),
                                Cast("time_at_last_encounter__age", TextField()),
                                Cast("time_at_last_encounter__age_range", TextField()),
                                Cast("vital_status__status", TextField()),
                                Cast("vital_status__time_of_death", TextField()),
                                Cast("vital_status__cause_of_death", TextField()),
                                Cast("vital_status__survival_time_in_days", TextField()),
                                "sex", "karyotypic_sex",
                                Cast("taxonomy", TextField()),
                                Cast("extra_properties", TextField()),

                                # Phenotypic feature fields
                                "phenopackets__phenotypic_features__description",
                                Cast("phenopackets__phenotypic_features__pftype", TextField()),
                                Cast("phenopackets__phenotypic_features__severity", TextField()),
                                Cast("phenopackets__phenotypic_features__modifiers", TextField()),
                                Cast("phenopackets__phenotypic_features__onset", TextField()),
                                Cast("phenopackets__phenotypic_features__evidence", TextField()),
                                Cast("phenopackets__phenotypic_features__extra_properties", TextField()),

                                # Biosample fields
                                "phenopackets__biosamples__id",
                                "phenopackets__biosamples__description",
                                Cast("phenopackets__biosamples__sampled_tissue", TextField()),
                                Cast("phenopackets__biosamples__taxonomy", TextField()),
                                Cast("phenopackets__biosamples__time_of_collection", TextField()),
                                Cast("phenopackets__biosamples__histological_diagnosis", TextField()),
                                Cast("phenopackets__biosamples__tumor_progression", TextField()),
                                Cast("phenopackets__biosamples__tumor_grade", TextField()),
                                Cast("phenopackets__biosamples__diagnostic_markers", TextField()),
                                # Biosample Procedure fields
                                Cast("phenopackets__biosamples__procedure__code", TextField()),
                                Cast("phenopackets__biosamples__procedure__body_site", TextField()),
                                Cast("phenopackets__biosamples__procedure__extra_properties", TextField()),
                                Cast("phenopackets__biosamples__extra_properties", TextField()),

                                # Interpretation field
                                "phenopackets__interpretations__progress_status",
                                "phenopackets__interpretations__summary",
                                Cast("phenopackets__interpretations__extra_properties", TextField()),

                                # Interpretation.Diagnosis
                                Cast("phenopackets__interpretations__diagnosis__disease", TextField()),
                                Cast("phenopackets__interpretations__diagnosis__extra_properties", TextField()),

                                # Interpretation.Diagnosis.GenomicInterpretation
                                f"{GENOMIC_INTERPRETATION_QUERY}__subject__id",
                                f"{GENOMIC_INTERPRETATION_QUERY}__biosample__id",
                                f"{GENOMIC_INTERPRETATION_QUERY}__interpretation_status",
                                Cast(f"{GENOMIC_INTERPRETATION_QUERY}__extra_properties", TextField()),

                                # Interpretation.Diagnosis.GenomicInterpretation.VariantInterpretation fields
                                f"{VARIANT_INTERPRETATION_QUERY}__acmg_pathogenicity_classification",
                                f"{VARIANT_INTERPRETATION_QUERY}__therapeutic_actionability",

                                # VariantInterpretation.VariationDescriptor
                                f"{VARIATION_DESCRIPTOR_QUERY}__id",
                                f"{VARIATION_DESCRIPTOR_QUERY}__label",
                                f"{VARIATION_DESCRIPTOR_QUERY}__description",
                                f"{VARIATION_DESCRIPTOR_QUERY}__molecule_context",
                                f"{VARIATION_DESCRIPTOR_QUERY}__vrs_ref_allele_seq",
                                Cast(f"{VARIATION_DESCRIPTOR_QUERY}__variation", TextField()),
                                Cast(f"{VARIATION_DESCRIPTOR_QUERY}__expressions", TextField()),
                                Cast(f"{VARIATION_DESCRIPTOR_QUERY}__vcf_record", TextField()),
                                Cast(f"{VARIATION_DESCRIPTOR_QUERY}__xrefs", TextField()),
                                Cast(f"{VARIATION_DESCRIPTOR_QUERY}__alternate_labels", TextField()),
                                Cast(f"{VARIATION_DESCRIPTOR_QUERY}__extensions", TextField()),
                                Cast(f"{VARIATION_DESCRIPTOR_QUERY}__structural_type", TextField()),
                                Cast(f"{VARIATION_DESCRIPTOR_QUERY}__allelic_state", TextField()),

                                # Interpretation.Diagnosis.GenomicInterpretation.GeneDescriptor fields
                                f"{GENE_DESCRIPTOR_QUERY}__value_id",
                                f"{GENE_DESCRIPTOR_QUERY}__symbol",
                                f"{GENE_DESCRIPTOR_QUERY}__description",
                                Cast(f"{GENE_DESCRIPTOR_QUERY}__alternate_ids", TextField()),
                                Cast(f"{GENE_DESCRIPTOR_QUERY}__xrefs", TextField()),
                                Cast(f"{GENE_DESCRIPTOR_QUERY}__alternate_symbols", TextField()),
                                Cast(f"{GENE_DESCRIPTOR_QUERY}__extra_properties", TextField()),

                                # Disease field
                                Cast("phenopackets__diseases__term", TextField()),
                                Cast("phenopackets__diseases__excluded", BooleanField()),
                                Cast("phenopackets__diseases__onset", TextField()),
                                Cast("phenopackets__diseases__resolution", TextField()),
                                Cast("phenopackets__diseases__disease_stage", TextField()),
                                Cast("phenopackets__diseases__clinical_tnm_finding", TextField()),
                                Cast("phenopackets__diseases__primary_site", TextField()),
                                Cast("phenopackets__diseases__laterality", TextField()),
                                Cast("phenopackets__diseases__extra_properties", TextField()),

                                # Experiment fields
                                "phenopackets__biosamples__experiment__study_type",
                                "phenopackets__biosamples__experiment__experiment_type",
                                Cast("phenopackets__biosamples__experiment__experiment_ontology", TextField()),
                                "phenopackets__biosamples__experiment__molecule",
                                Cast("phenopackets__biosamples__experiment__molecule_ontology", TextField()),
                                "phenopackets__biosamples__experiment__library_strategy",
                                "phenopackets__biosamples__experiment__library_source",
                                "phenopackets__biosamples__experiment__library_selection",
                                "phenopackets__biosamples__experiment__library_layout",
                                "phenopackets__biosamples__experiment__extraction_protocol",
                                "phenopackets__biosamples__experiment__reference_registry_id",
                                Cast("phenopackets__biosamples__experiment__extra_properties", TextField()),
                                # Experiments: Experiment Results fields
                                "phenopackets__biosamples__experiment__experiment_results__description",
                                "phenopackets__biosamples__experiment__experiment_results__filename",
                                "phenopackets__biosamples__experiment__experiment_results__file_format",
                                "phenopackets__biosamples__experiment__experiment_results__genome_assembly_id",
                                "phenopackets__biosamples__experiment__experiment_results__data_output_type",
                                "phenopackets__biosamples__experiment__experiment_results__usage",
                                "phenopackets__biosamples__experiment__experiment_results__creation_date",
                                "phenopackets__biosamples__experiment__experiment_results__created_by",
                                Cast(
                                    "phenopackets__biosamples__experiment__experiment_results__extra_properties",
                                    TextField()
                                ),
                                # Experiments: Instrument fields
                                "phenopackets__biosamples__experiment__instrument__platform",
                                "phenopackets__biosamples__experiment__instrument__description",
                                "phenopackets__biosamples__experiment__instrument__model",
                                Cast(
                                    "phenopackets__biosamples__experiment__instrument__extra_properties",
                                    TextField()
                                ),
                                )
        ).filter(search=value).distinct("id")
        return qs
