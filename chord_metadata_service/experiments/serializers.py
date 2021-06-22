from chord_metadata_service.restapi.serializers import GenericSerializer
from .models import Experiment, ExperimentResult, Instrument


__all__ = ["ExperimentSerializer"]


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
