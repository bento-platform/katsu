from chord_metadata_service.phenopackets.serializers import BiosampleSerializer, SimplePhenopacketSerializer
from chord_metadata_service.restapi.serializers import GenericSerializer
from .models import Individual, VitalStatus

__all__ = [
    "VitalStatusSerializer",
    "IndividualSerializer",
]


class VitalStatusSerializer(GenericSerializer):
    class Meta:
        model = VitalStatus
        fields = "__all__"


class IndividualSerializer(GenericSerializer):
    biosamples = BiosampleSerializer(read_only=True, many=True)
    phenopackets = SimplePhenopacketSerializer(read_only=True, many=True)
    vital_status = VitalStatusSerializer(read_only=True)

    class Meta:
        model = Individual
        exclude = ("fts_extra",)
