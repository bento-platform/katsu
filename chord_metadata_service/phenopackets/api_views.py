from rest_framework import viewsets, pagination
from .serializers import *
from .models import *
from rest_framework.settings import api_settings
from chord_metadata_service.restapi.api_renderers import *


class LargeResultsSetPagination(pagination.PageNumberPagination):
	page_size = 25
	page_size_query_param = 'page_size'
	max_page_size = 10000


class PhenopacketsModelViewSet(viewsets.ModelViewSet):
	renderer_classes = tuple(
		api_settings.DEFAULT_RENDERER_CLASSES) + (PhenopacketsRenderer,)
	pagination_class = LargeResultsSetPagination


class PhenotypicFeatureViewSet(PhenopacketsModelViewSet):
	"""
	get:
	Return a list of all existing phenotypic features

	post:
	Create a new phenotypic feature

	"""
	queryset = PhenotypicFeature.objects.all().order_by("id")
	serializer_class = PhenotypicFeatureSerializer
	renderer_classes = tuple(PhenopacketsModelViewSet.renderer_classes) + (
		FHIRRenderer,)


class ProcedureViewSet(PhenopacketsModelViewSet):
	"""
	get:
	Return a list of all existing procedures

	post:
	Create a new procedure

	"""
	queryset = Procedure.objects.all().order_by("id")
	serializer_class = ProcedureSerializer
	renderer_classes = tuple(PhenopacketsModelViewSet.renderer_classes) + (
		FHIRRenderer,)


class HtsFileViewSet(PhenopacketsModelViewSet):
	"""
	get:
	Return a list of all existing HTS files

	post:
	Create a new HTS file

	"""
	queryset = HtsFile.objects.all().order_by("uri")
	serializer_class = HtsFileSerializer
	renderer_classes = tuple(PhenopacketsModelViewSet.renderer_classes) + (
		FHIRRenderer,)


class GeneViewSet(PhenopacketsModelViewSet):
	"""
	get:
	Return a list of all existing genes

	post:
	Create a new gene

	"""
	queryset = Gene.objects.all().order_by("id")
	serializer_class = GeneSerializer
	renderer_classes = tuple(PhenopacketsModelViewSet.renderer_classes) + (
		FHIRRenderer,)


class VariantViewSet(PhenopacketsModelViewSet):
	"""
	get:
	Return a list of all existing variants

	post:
	Create a new variant

	"""
	queryset = Variant.objects.all().order_by("id")
	serializer_class = VariantSerializer
	renderer_classes = tuple(PhenopacketsModelViewSet.renderer_classes) + (
		FHIRRenderer,)


class DiseaseViewSet(PhenopacketsModelViewSet):
	"""
	get:
	Return a list of all existing diseases

	post:
	Create a new disease

	"""
	queryset = Disease.objects.all().order_by("id")
	serializer_class = DiseaseSerializer
	renderer_classes = tuple(PhenopacketsModelViewSet.renderer_classes) + (
		FHIRRenderer,)


class ResourceViewSet(PhenopacketsModelViewSet):
	"""
	get:
	Return a list of all existing resources

	post:
	Create a new resource

	"""
	queryset = Resource.objects.all().order_by("id")
	serializer_class = ResourceSerializer


class MetaDataViewSet(PhenopacketsModelViewSet):
	"""
	get:
	Return a list of all existing metadata records

	post:
	Create a new metadata record

	"""
	queryset = MetaData.objects.all().order_by("id")
	serializer_class = MetaDataSerializer


class BiosampleViewSet(PhenopacketsModelViewSet):
	"""
	get:
	Return a list of all existing biosamples

	post:
	Create a new biosample
	"""
	queryset = Biosample.objects.all().order_by("id")
	serializer_class = BiosampleSerializer
	renderer_classes = tuple(PhenopacketsModelViewSet.renderer_classes) + (
		FHIRRenderer,)


class PhenopacketViewSet(PhenopacketsModelViewSet):
	"""
	get:
	Return a list of all existing phenopackets

	post:
	Create a new phenopacket

	"""
	queryset = Phenopacket.objects.all().order_by("id")
	serializer_class = PhenopacketSerializer


class GenomicInterpretationViewSet(PhenopacketsModelViewSet):
	"""
	get:
	Return a list of all existing genomic interpretations

	post:
	Create a new genomic interpretation

	"""
	queryset = GenomicInterpretation.objects.all().order_by("id")
	serializer_class = GenomicInterpretationSerializer


class DiagnosisViewSet(PhenopacketsModelViewSet):
	"""
	get:
	Return a list of all existing diagnoses

	post:
	Create a new diagnosis

	"""
	queryset = Diagnosis.objects.all().order_by("id")
	serializer_class = DiagnosisSerializer


class InterpretationViewSet(PhenopacketsModelViewSet):
	"""
	get:
	Return a list of all existing interpretations

	post:
	Create a new interpretation

	"""
	queryset = Interpretation.objects.all().order_by("id")
	serializer_class = InterpretationSerializer
