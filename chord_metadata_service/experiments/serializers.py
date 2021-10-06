from chord_metadata_service.restapi.serializers import GenericSerializer
from .models import Experiment, ExperimentResult, Instrument
from rest_framework import serializers

__all__ = ["ExperimentSerializer", "ListExperimentSerializer"]


class ExperimentResultSerializer(GenericSerializer):
    class Meta:
        model = ExperimentResult
        fields = "__all__"


class InstrumentSerializer(GenericSerializer):
    class Meta:
        model = Instrument
        fields = "__all__"


class ExperimentSerializer(GenericSerializer):
    experiment_results = ExperimentResultSerializer(read_only=True, many=True)
    instrument = InstrumentSerializer()

    class Meta:
        model = Experiment
        fields = "__all__"


# Serializer to be used for list view and when nested

class ListExperimentSerializer(GenericSerializer):
    id = serializers.CharField(read_only=True)
    experiment_type = serializers.CharField(read_only=True)

    class Meta:
        model = Experiment
        fields = ["id", "experiment_type"]
