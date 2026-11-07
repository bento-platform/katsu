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
    vital_status = VitalStatusSerializer(read_only=True, exclude_when_nested=["id", "created", "updated"])

    class Meta:
        model = Individual
        exclude = ("fts_extra",)

    def create(self, validated_data):
        """
        Create an individual, optionally creating/re-using a vital status object as well.
        """

        instance = super().create(validated_data)

        if vs := self.initial_data.get("vital_status"):
            vs_s = VitalStatusSerializer(data=vs)
            vs_s.is_valid(raise_exception=True)
            vs_obj, _ = VitalStatus.objects.get_or_create(**vs_s.validated_data)
            instance.vital_status = vs_obj
            instance.save()

        return instance

    # Updating a nested instance is difficult, so for now just support creating vital status via individual, not doing
    # any updates, since the REST API isn't the main supported way of ingesting data into Katsu.
