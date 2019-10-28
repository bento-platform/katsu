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
