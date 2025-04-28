from chord_metadata_service.phenopackets.serializers import (
    BiosampleSerializer, SimpleBiosampleSerializer, SimplePhenopacketSerializer
)
from chord_metadata_service.restapi.serializers import GenericSerializer
from .models import Individual

__all__ = [
    "IndividualSerializer",
    "IndividualSerializerForCSV",
]


class IndividualSerializer(GenericSerializer):
    biosamples = BiosampleSerializer(read_only=True, many=True)
    phenopackets = SimplePhenopacketSerializer(read_only=True, many=True)

    class Meta:
        model = Individual
        fields = "__all__"


class IndividualSerializerForCSV(GenericSerializer):
    biosamples = SimpleBiosampleSerializer(read_only=True, many=True)
    phenopackets = SimplePhenopacketSerializer(read_only=True, many=True)

    class Meta:
        model = Individual
        fields = [
            "id",
            "sex",
            "karyotypic_sex",
            "date_of_birth",
            "taxonomy",
            "time_at_last_encounter",
            "created",
            "updated",
            # ---
            "biosamples",
            "phenopackets",
        ]
