from rest_framework import serializers

from chord_metadata_service.patients.models import Individual
from chord_metadata_service.restapi.serializers import GenericSerializer
from .models import Experiment, ExperimentResult, Instrument


__all__ = ["ExperimentSerializer", "ExperimentResultSerializer", "InstrumentSerializer"]


class ExperimentResultSerializer(GenericSerializer):
    # The dataset (i.e., "study") this result belongs to, reached via its linked experiment(s) - read-only/derived,
    # used by the download-manifest export. A result could in principle be linked to multiple experiments (M2M), so
    # this just takes the first one.
    study = serializers.SerializerMethodField()

    class Meta:
        model = ExperimentResult
        exclude = ("fts_extra",)

    def get_study(self, obj: ExperimentResult) -> str | None:
        experiment = next(iter(obj.experiments.all()), None)
        if experiment is None or experiment.dataset_id is None:
            return None
        return str(experiment.dataset.identifier)


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
        exclude = ("fts_extra",)
