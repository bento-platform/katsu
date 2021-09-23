from chord_metadata_service.restapi.serializers import GenericSerializer
from .models import Experiment, ExperimentResult, Instrument
from rest_framework import serializers
from typing import Dict, Any


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


################################ new serializers ################################


class SimpleExperimentResultSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    description = serializers.CharField()
    filename = serializers.CharField()
    file_format = serializers.CharField()
    data_output_type = serializers.CharField()
    usage = serializers.CharField()
    creation_date = serializers.CharField()
    created_by = serializers.CharField()
    extra_properties = serializers.JSONField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()

    class Meta:
        model = ExperimentResult


class SimpleInstrumentSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    platform = serializers.CharField()
    description = serializers.CharField()
    model = serializers.CharField()
    extra_properties = serializers.JSONField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()

    class Meta:
        model = Instrument


def serialize_experiment_result(experiment_result: ExperimentResult) -> Dict[str, Any]:
    return {
        'identifier': experiment_result.identifier,
        'description': experiment_result.description,
        'filename': experiment_result.filename,
        'file_format': experiment_result.file_format,
        'data_output_type': experiment_result.data_output_type,
        'usage': experiment_result.usage,
        'creation_date': experiment_result.creation_date,
        'created_by': experiment_result.created_by,
        'extra_properties': experiment_result.extra_properties,
        'created': experiment_result.created.isoformat(),
        'updated': experiment_result.updated.isoformat(),
    }


def serialize_instrument(instrument: Instrument) -> Dict[str, Any]:
    return {
        'identifier': instrument.identifier,
        'platform': instrument.platform,
        'description': instrument.description,
        'model': instrument.model,
        'extra_properties': instrument.extra_properties,
        'created': instrument.created.isoformat(),
        'updated': instrument.updated.isoformat(),
    }


class NewExperimentSerializer(serializers.Serializer):
    id = serializers.CharField()
    study_type = serializers.CharField()
    experiment_type = serializers.CharField()
    experiment_ontology = serializers.JSONField()
    molecule = serializers.CharField()
    molecule_ontology = serializers.JSONField()
    library_strategy = serializers.CharField()
    library_source = serializers.CharField()
    library_selection = serializers.CharField()
    library_layout = serializers.CharField()
    extraction_protocol = serializers.CharField()
    reference_registry_id = serializers.CharField()
    qc_flags = serializers.ListField()
    biosample = serializers.CharField()
    table = serializers.CharField()
    # Experiment results
    experiment_results = SimpleExperimentResultSerializer(many=True)
    # set to a method serializer
    # experiment_results = serializers.SerializerMethodField()
    # Instrument
    instrument = SimpleInstrumentSerializer()
    # set to a method serializer
    # instrument = serializers.SerializerMethodField()

    extra_properties = serializers.JSONField()
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()

    class Meta:
        model = Experiment

    # def get_experiment_results(self, obj):
    #     return [serialize_experiment_result(e) for e in obj.experiment_results.all()]
    #
    # def get_instrument(self, obj):
    #     return serialize_instrument(obj.instrument)


#####################################################################
