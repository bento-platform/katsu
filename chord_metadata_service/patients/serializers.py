from chord_metadata_service.phenopackets.serializers import BiosampleSerializer, SimplePhenopacketSerializer
from chord_metadata_service.restapi.serializers import GenericSerializer
from .models import Individual

__all__ = [
    "IndividualSerializer",
]


class IndividualSerializer(GenericSerializer):
    biosamples = BiosampleSerializer(read_only=True, many=True, exclude_when_nested=['individual'])
    phenopackets = SimplePhenopacketSerializer(read_only=True, many=True, exclude_when_nested=['subject'])

    class Meta:
        model = Individual
        fields = "__all__"
