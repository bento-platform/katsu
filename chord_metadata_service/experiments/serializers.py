from chord_metadata_service.restapi.serializers import GenericSerializer
from .models import Experiment, ExperimentResult, Instrument
from chord_metadata_service.patients.models import Individual


__all__ = ["ExperimentSerializer", "ExperimentResultSerializer", "InstrumentSerializer"]


class ExperimentResultSerializer(GenericSerializer):
    class Meta:
        model = ExperimentResult
        fields = "__all__"


class InstrumentSerializer(GenericSerializer):
    class Meta:
        model = Instrument
        fields = "__all__"


# this is for dinamic field selection, allow the serializer include/exclude fields in the output
class DynamicFieldsMixin:
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class IndividualSerializer(DynamicFieldsMixin, GenericSerializer):
    class Meta:
        model = Individual
        fields = "__all__"


class ExperimentSerializer(GenericSerializer):
    experiment_results = ExperimentResultSerializer(read_only=True, many=True)
    instrument = InstrumentSerializer()
    biosample_individual = IndividualSerializer(source='biosample.individual', read_only=True, fields=['id'])

    class Meta:
        model = Experiment
        fields = "__all__"
