from rest_framework.decorators import api_view
from rest_framework.response import Response
from chord_metadata_service.metadata.service_info import SERVICE_INFO

@api_view()
def service_info(request):
	"""
	get:
	Return service info
	"""

	return Response(SERVICE_INFO)