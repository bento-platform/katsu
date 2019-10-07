from rest_framework import viewsets, pagination
from .serializers import *
from .models import *
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from chord_metadata_service.metadata.service_info import SERVICE_INFO


class LargeResultsSetPagination(pagination.PageNumberPagination):
	page_size = 25
	page_size_query_param = 'page_size'
	max_page_size = 10000


class OntologyViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing ontologies

	post:
	Create a new ontology

	"""
	queryset = Ontology.objects.all()
	serializer_class = OntologySerializer
	pagination_class = LargeResultsSetPagination


class VariantViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing variants

	post:
	Create a new variant

	"""
	queryset = Variant.objects.all()
	serializer_class = VariantSerializer
	pagination_class = LargeResultsSetPagination
	# TODO filtering
	# filter_backends = (DjangoFilterBackend,)
	# filter_class = VariantFilter


class PhenotypicFeatureViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing phenotypic features

	post:
	Create a new phenotypic feature

	"""
	queryset = PhenotypicFeature.objects.all()
	serializer_class = PhenotypicFeatureSerializer
	pagination_class = LargeResultsSetPagination


class ProcedureViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing procedures

	post:
	Create a new procedure

	"""
	queryset = Procedure.objects.all()
	serializer_class = ProcedureSerializer
	pagination_class = LargeResultsSetPagination


class HtsFileViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing HTS files

	post:
	Create a new HTS file

	"""
	queryset = HtsFile.objects.all()
	serializer_class = HtsFileSerializer
	pagination_class = LargeResultsSetPagination


class GeneViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing genes

	post:
	Create a new gene

	"""
	queryset = Gene.objects.all()
	serializer_class = GeneSerializer
	pagination_class = LargeResultsSetPagination


class DiseaseViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing diseases

	post:
	Create a new disease

	"""
	queryset = Disease.objects.all()
	serializer_class = DiseaseSerializer
	pagination_class = LargeResultsSetPagination


class ResourceViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing resources

	post:
	Create a new resource

	"""
	queryset = Resource.objects.all()
	serializer_class = ResourceSerializer
	pagination_class = LargeResultsSetPagination


class UpdateViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing updates

	post:
	Create a new update

	"""
	queryset = Update.objects.all()
	serializer_class = UpdateSerializer
	pagination_class = LargeResultsSetPagination


class ExternalReferenceViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing external references

	post:
	Create a new external reference

	"""
	queryset = ExternalReference.objects.all()
	serializer_class = ExternalReferenceSerializer
	pagination_class = LargeResultsSetPagination


class MetaDataViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing metadata records

	post:
	Create a new metadata record

	"""
	queryset = MetaData.objects.all()
	serializer_class = MetaDataSerializer
	pagination_class = LargeResultsSetPagination


class IndividualViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing individuals

	post:
	Create a new individual

	"""
	queryset = Individual.objects.all()
	serializer_class = IndividualSerializer
	pagination_class = LargeResultsSetPagination


class BiosampleViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing biosamples

	post:
	Create a new biosample
	"""
	queryset = Biosample.objects.all()
	serializer_class = BiosampleSerializer
	pagination_class = LargeResultsSetPagination


class PhenopacketViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing phenopackets

	post:
	Create a new phenopacket

	"""
	queryset = Phenopacket.objects.all()
	serializer_class = PhenopacketSerializer
	pagination_class = LargeResultsSetPagination


class GenomicInterpretationViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing genomic interpretations

	post:
	Create a new genomic interpretation

	"""
	queryset = GenomicInterpretation.objects.all()
	serializer_class = GenomicInterpretationSerializer
	pagination_class = LargeResultsSetPagination


class DiagnosisViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing diagnoses

	post:
	Create a new diagnosis

	"""
	queryset = Diagnosis.objects.all()
	serializer_class = DiagnosisSerializer
	pagination_class = LargeResultsSetPagination


class InterpretationViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing interpretations

	post:
	Create a new interpretation

	"""
	queryset = Interpretation.objects.all()
	serializer_class = InterpretationSerializer
	pagination_class = LargeResultsSetPagination


class ProjectViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing projects

	post:
	Create a new project
	"""

	queryset = Project.objects.all().order_by("project_id")
	serializer_class = ProjectSerializer
	pagination_class = LargeResultsSetPagination

	# noinspection PyUnusedLocal
	@action(detail=True, methods=["GET"])
	def datasets(self, _request, pk):
		project = self.get_object()
		datasets = Dataset.objects.filter(project=project)

		page = self.paginate_queryset(datasets)
		if page is not None:
			serializer = DatasetSerializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = DatasetSerializer(datasets, many=True)
		return Response(serializer.data)


class DatasetViewSet(viewsets.ModelViewSet):
	"""
	get:
	Return a list of all existing datasets

	post:
	Create a new dataset
	"""

	queryset = Dataset.objects.all().order_by("dataset_id")
	serializer_class = DatasetSerializer
	pagination_class = LargeResultsSetPagination


@api_view()
def service_info(request):
	"""
	get:
	Return service info
	"""

	return Response(SERVICE_INFO)
