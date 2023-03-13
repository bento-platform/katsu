from drf_spectacular.utils import extend_schema, extend_schema_serializer
from rest_framework import mixins, serializers, viewsets
from rest_framework.response import Response

from chord_metadata_service.mohpackets.api_base import (
    BaseBiomarkerViewSet,
    BaseChemotherapyViewSet,
    BaseComorbidityViewSet,
    BaseDonorViewSet,
    BaseFollowUpViewSet,
    BaseHormoneTherapyViewSet,
    BaseImmunotherapyViewSet,
    BasePrimaryDiagnosisViewSet,
    BaseRadiationViewSet,
    BaseSampleRegistrationViewSet,
    BaseSpecimenViewSet,
    BaseSurgeryViewSet,
    BaseTreatmentViewSet,
)

"""
    This module inheriting from the base views and adding the discovery mixin,
    which returns the number of donors only.
    
    The discovery feature can help users without authorization explore the
    available data without exposing the details.
"""


##########################################
#                                        #
#           HELPER FUNCTIONS             #
#                                        #
##########################################


@extend_schema_serializer(many=False)
class DiscoverySerializer(serializers.Serializer):
    """
    This serializer is used to return the discovery_count.
    It also override the list serializer to a single object
    """

    discovery_count = serializers.IntegerField()


class DiscoveryMixin:
    @extend_schema(responses=DiscoverySerializer(many=False))
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        count = queryset.values_list("submitter_donor_id").distinct().count()
        return Response({"discovery_count": count})


###############################################
#                                             #
#           DISCOVERY API VIEWS               #
#                                             #
###############################################


class DiscoveryDonorViewSet(DiscoveryMixin, BaseDonorViewSet):
    pass


class DiscoverySpecimenViewSet(DiscoveryMixin, BaseSpecimenViewSet):
    pass


class DiscoverySampleRegistrationViewSet(DiscoveryMixin, BaseSampleRegistrationViewSet):
    pass


class DiscoveryPrimaryDiagnosisViewSet(DiscoveryMixin, BasePrimaryDiagnosisViewSet):
    pass


class DiscoveryTreatmentViewSet(DiscoveryMixin, BaseTreatmentViewSet):
    pass


class DiscoveryChemotherapyViewSet(DiscoveryMixin, BaseChemotherapyViewSet):
    pass


class DiscoveryHormoneTherapyViewSet(DiscoveryMixin, BaseHormoneTherapyViewSet):
    pass


class DiscoveryRadiationViewSet(DiscoveryMixin, BaseRadiationViewSet):
    pass


class DiscoveryImmunotherapyViewSet(DiscoveryMixin, BaseImmunotherapyViewSet):
    pass


class DiscoverySurgeryViewSet(DiscoveryMixin, BaseSurgeryViewSet):
    pass


class DiscoveryFollowUpViewSet(DiscoveryMixin, BaseFollowUpViewSet):
    pass


class DiscoveryBiomarkerViewSet(DiscoveryMixin, BaseBiomarkerViewSet):
    pass


class DiscoveryComorbidityViewSet(DiscoveryMixin, BaseComorbidityViewSet):
    pass
