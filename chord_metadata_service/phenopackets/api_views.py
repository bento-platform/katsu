from collections import Counter
from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend

from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer, FHIRRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination
from chord_metadata_service.restapi.utils import parse_individual_age
from chord_metadata_service.chord.permissions import OverrideOrSuperUserOnly
from chord_metadata_service.phenopackets.schemas import PHENOPACKET_SCHEMA
from . import models as m, serializers as s, filters as f


class PhenopacketsModelViewSet(viewsets.ModelViewSet):
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, PhenopacketsRenderer)
    pagination_class = LargeResultsSetPagination

    # Cache page for the requested url for 2 hours
    @method_decorator(cache_page(60 * 60 * 2))
    def dispatch(self, *args, **kwargs):
        return super(PhenopacketsModelViewSet, self).dispatch(*args, **kwargs)


class ExtendedPhenopacketsModelViewSet(PhenopacketsModelViewSet):
    renderer_classes = (*PhenopacketsModelViewSet.renderer_classes, FHIRRenderer)


class PhenotypicFeatureViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing phenotypic features

    post:
    Create a new phenotypic feature

    """
    queryset = m.PhenotypicFeature.objects.all().order_by("id")
    serializer_class = s.PhenotypicFeatureSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.PhenotypicFeatureFilter


class ProcedureViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing procedures

    post:
    Create a new procedure

    """
    queryset = m.Procedure.objects.all().order_by("id")
    serializer_class = s.ProcedureSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.ProcedureFilter


class HtsFileViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing HTS files

    post:
    Create a new HTS file

    """
    queryset = m.HtsFile.objects.all().order_by("uri")
    serializer_class = s.HtsFileSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.HtsFileFilter


class GeneViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing genes

    post:
    Create a new gene

    """
    queryset = m.Gene.objects.all().order_by("id")
    serializer_class = s.GeneSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.GeneFilter


class VariantViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing variants

    post:
    Create a new variant

    """
    queryset = m.Variant.objects.all().order_by("id")
    serializer_class = s.VariantSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.VariantFilter


class DiseaseViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing diseases

    post:
    Create a new disease

    """
    queryset = m.Disease.objects.all().order_by("id")
    serializer_class = s.DiseaseSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.DiseaseFilter


META_DATA_PREFETCH = (
    "resources",
)


class MetaDataViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing metadata records

    post:
    Create a new metadata record

    """
    queryset = m.MetaData.objects.all().prefetch_related(*META_DATA_PREFETCH).order_by("id")
    serializer_class = s.MetaDataSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.MetaDataFilter


BIOSAMPLE_PREFETCH = (
    "hts_files",
    "phenotypic_features",
    "procedure",
    "variants",
    "experiment_set",
)

BIOSAMPLE_SELECT_REL = (
    "procedure",
)


class BiosampleViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing biosamples

    post:
    Create a new biosample
    """
    queryset = m.Biosample.objects.all()\
        .prefetch_related(*BIOSAMPLE_PREFETCH)\
        .select_related(*BIOSAMPLE_SELECT_REL)\
        .order_by("id")
    serializer_class = s.BiosampleSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.BiosampleFilter


PHENOPACKET_PREFETCH = (
    *(f"biosamples__{p}" for p in BIOSAMPLE_PREFETCH),
    "diseases",
    "genes",
    "hts_files",
    *(f"meta_data__{p}" for p in META_DATA_PREFETCH),
    "phenotypic_features",
    "subject",
    "variants",
)

PHENOPACKET_SELECT_REL = (
    "subject",
    "meta_data",
)


class PhenopacketViewSet(ExtendedPhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing phenopackets

    post:
    Create a new phenopacket

    """
    queryset = m.Phenopacket.objects.all()\
        .prefetch_related(*PHENOPACKET_PREFETCH)\
        .select_related(*PHENOPACKET_SELECT_REL)\
        .order_by("id")
    serializer_class = s.PhenopacketSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.PhenopacketFilter


class GenomicInterpretationViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing genomic interpretations

    post:
    Create a new genomic interpretation

    """
    queryset = m.GenomicInterpretation.objects.all().order_by("id")
    serializer_class = s.GenomicInterpretationSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.GenomicInterpretationFilter


class DiagnosisViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing diagnoses

    post:
    Create a new diagnosis

    """
    queryset = m.Diagnosis.objects.all().order_by("id")
    serializer_class = s.DiagnosisSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.DiagnosisFilter


class InterpretationViewSet(PhenopacketsModelViewSet):
    """
    get:
    Return a list of all existing interpretations

    post:
    Create a new interpretation

    """
    queryset = m.Interpretation.objects.all().order_by("id")
    serializer_class = s.InterpretationSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = f.InterpretationFilter


@api_view(["GET"])
@permission_classes([AllowAny])
def get_chord_phenopacket_schema(_request):
    """
    get:
    Chord phenopacket schema that can be shared with data providers.
    """
    return Response(PHENOPACKET_SCHEMA)


# Cache page for the requested url for 2 hours
@cache_page(60 * 60 * 2)
@api_view(["GET"])
@permission_classes([OverrideOrSuperUserOnly])
def phenopackets_overview(_request):
    """
    get:
    Overview of all Phenopackets in the database
    """
    phenopackets = m.Phenopacket.objects.all().prefetch_related(*PHENOPACKET_PREFETCH).select_related(
        *PHENOPACKET_SELECT_REL)

    diseases_counter = Counter()
    phenotypic_features_counter = Counter()

    biosamples_set = set()
    individuals_set = set()

    biosamples_taxonomy = Counter()
    biosamples_sampled_tissue = Counter()

    experiments_set = set()
    experiments_study_type = Counter()
    experiments_experiment_type = Counter()
    experiments_molecule = Counter()
    experiments_library_strategy = Counter()
    experiments_library_source = Counter()
    experiments_library_selection = Counter()
    experiments_library_layout = Counter()
    experiments_extraction_protocol = Counter()

    experiments_experiment_results_set = set()
    experiments_experiment_results_file_format = Counter()
    experiments_experiment_results_data_output_type = Counter()
    experiments_experiment_results_usage = Counter()

    experiments_instrument_set = set()
    experiments_instrument_platform = Counter()
    experiments_instrument_model = Counter()

    individuals_sex = Counter()
    individuals_k_sex = Counter()
    individuals_taxonomy = Counter()
    individuals_age = Counter()
    individuals_ethnicity = Counter()
    individuals_extra_prop = {}
    extra_prop_counter_dict = {}

    def count_individual(ind):

        individuals_set.add(ind.id)
        individuals_sex.update((ind.sex,))
        individuals_k_sex.update((ind.karyotypic_sex,))
        # ethnicity is char field, check it's not empty
        if ind.ethnicity != "":
            individuals_ethnicity.update((ind.ethnicity,))

        # Generic Counter on all available extra properties
        if ind.extra_properties:
            for key in ind.extra_properties:
                # Declare new Counter() if it's not delcared
                if key not in extra_prop_counter_dict:
                    extra_prop_counter_dict[key] = Counter()

                extra_prop_counter_dict[key].update((ind.extra_properties[key],))
                individuals_extra_prop[key] = dict(extra_prop_counter_dict[key])

        if ind.age is not None:
            individuals_age.update((parse_individual_age(ind.age),))
        if ind.taxonomy is not None:
            individuals_taxonomy.update((ind.taxonomy["label"],))

    for p in phenopackets:
        for b in p.biosamples.all():
            biosamples_set.add(b.id)
            biosamples_sampled_tissue.update((b.sampled_tissue["label"],))

            if b.taxonomy is not None:
                biosamples_taxonomy.update((b.taxonomy["label"],))

            for exp in b.experiment_set.all():
                experiments_set.add(exp.id)

                if exp.study_type is not None:
                    experiments_study_type.update((exp.study_type,))

                if exp.experiment_type is not None:
                    experiments_experiment_type.update((exp.experiment_type,))

                if exp.molecule is not None:
                    experiments_molecule.update((exp.molecule,))

                if exp.library_strategy is not None:
                    experiments_library_strategy.update((exp.library_strategy,))

                if exp.library_source is not None:
                    experiments_library_source.update((exp.library_source,))

                if exp.library_selection is not None:
                    experiments_library_selection.update((exp.library_selection,))

                if exp.library_layout is not None:
                    experiments_library_layout.update((exp.library_layout,))

                if exp.extraction_protocol is not None:
                    experiments_extraction_protocol.update((exp.extraction_protocol,))

                # query_set.many_to_many.all()
                if exp.experiment_results.all() is not None:
                    for result in exp.experiment_results.all():
                        experiments_experiment_results_set.add(result.id)
                        experiments_experiment_results_file_format.update((result.file_format,))
                        experiments_experiment_results_data_output_type.update((result.data_output_type,))
                        experiments_experiment_results_usage.update((result.usage,))

                if exp.instrument is not None:
                    experiments_instrument_set.add(exp.instrument.id)
                    experiments_instrument_platform.update((exp.instrument.platform,))
                    experiments_instrument_model.update((exp.instrument.model,))


            # TODO decide what to do with nested Phenotypic features and Subject in Biosample
            # This might serve future use cases that Biosample as a have main focus of study
            # for pf in b.phenotypic_features.all():
            #     phenotypic_features_counter.update((pf.pftype["label"],))

        # according to Phenopackets standard
        # phenotypic features also can be linked to a Biosample
        # but we count them here because all our use cases current have them linked to Phenopacket not biosample
        for d in p.diseases.all():
            diseases_counter.update((d.term["label"],))

        for pf in p.phenotypic_features.all():
            phenotypic_features_counter.update((pf.pftype["label"],))

        # Currently, phenopacket subject is required so we can assume it's not None
        count_individual(p.subject)

    return Response({
        "phenopackets": phenopackets.count(),
        "data_type_specific": {
            "biosamples": {
                "count": len(biosamples_set),
                "taxonomy": dict(biosamples_taxonomy),
                "sampled_tissue": dict(biosamples_sampled_tissue),
            },
            "diseases": {
                # count is a number of unique disease terms (not all diseases in the database)
                "count": len(diseases_counter.keys()),
                "term": dict(diseases_counter)
            },
            "individuals": {
                "count": len(individuals_set),
                "sex": {k: individuals_sex[k] for k in (s[0] for s in m.Individual.SEX)},
                "karyotypic_sex": {k: individuals_k_sex[k] for k in (s[0] for s in m.Individual.KARYOTYPIC_SEX)},
                "taxonomy": dict(individuals_taxonomy),
                "age": dict(individuals_age),
                "ethnicity": dict(individuals_ethnicity),
                "extra_properties": dict(individuals_extra_prop),
            },
            "phenotypic_features": {
                # count is a number of unique phenotypic feature types (not all pfs in the database)
                "count": len(phenotypic_features_counter.keys()),
                "type": dict(phenotypic_features_counter)
            },
            "experiments": {
                "count": len(experiments_set),
                "study_type": dict(experiments_study_type),
                "experiment_type": dict(experiments_experiment_type),
                "molecule": dict(experiments_molecule),
                "library_strategy": dict(experiments_library_strategy),
                "library_source": dict(experiments_library_source),
                "library_selection": dict(experiments_library_selection),
                "library_layout": dict(experiments_library_layout),
                "extraction_protocol": dict(experiments_extraction_protocol),
            },
            "experiment_results": {
                "count": len(experiments_experiment_results_set),
                "file_format": dict(experiments_experiment_results_file_format),
                "data_output_type": dict(experiments_experiment_results_data_output_type),
                "usage": dict(experiments_experiment_results_usage)
            },
            "instruments": {
                "count": len(experiments_instrument_set),
                "platform": dict(experiments_instrument_platform),
                "model": dict(experiments_instrument_model)
            },
        }
    })
