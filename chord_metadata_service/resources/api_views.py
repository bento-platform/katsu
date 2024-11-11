from rest_framework.settings import api_settings
from django_filters.rest_framework import DjangoFilterBackend

from chord_metadata_service.authz.viewset import BentoAuthzModelViewSet
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET
from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination

from .models import Resource
from .serializers import ResourceSerializer
from .filters import ResourceFilter


class ResourceViewSet(BentoAuthzModelViewSet):
    """
    get:
    Return a list of all existing resources

    post:
    Create a new resource

    """

    data_type = DATA_TYPE_PHENOPACKET

    queryset = Resource.objects.all().order_by("id")
    serializer_class = ResourceSerializer
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, PhenopacketsRenderer)
    pagination_class = LargeResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ResourceFilter

