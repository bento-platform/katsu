from chord_metadata_service.restapi.serializers import GenericSerializer
from .models import Experiment, ExperimentResult, Instrument
from rest_framework import serializers
from typing import Dict, Any

__all__ = ["ExperimentSerializer", "serialize_experiment", "ListExperimentSerializer", "serialize_experiment_result"]


class ExperimentResultSerializer(GenericSerializer):
    class Meta:
        model = ExperimentResult
        fields = "__all__"
        # set all fields to read only
        # read_only_fields = ["identifier", "description", "filename",
        #                     "file_format", "data_output_type", "usage", "creation_date",
        #                     "created_by", "extra_properties", "created", "updated"]


class InstrumentSerializer(GenericSerializer):
    class Meta:
        model = Instrument
        fields = "__all__"
        # read_only_fields = ["identifier", "platform", "description", "model",
        #                     "extra_properties", "created", "updated"]


class ExperimentSerializer(GenericSerializer):
    experiment_results = ExperimentResultSerializer(read_only=True, many=True)
    instrument = InstrumentSerializer()

    class Meta:
        model = Experiment
        fields = "__all__"
        # read_only_fields = ["id", "study_type", "experiment_type", "experiment_ontology",
        #                     "molecule", "molecule_ontology", "library_strategy", "library_source",
        #                     "library_selection", "library_layout", "extraction_protocol",
        #                     "reference_registry_id", "qc_flags", "biosample", "table",
        #                     "experiment_results", "instrument", "extra_properties",
        #                     "created", "updated"]


################################ new serializers ################################


class SimpleExperimentResultSerializer(serializers.Serializer):
    identifier = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    filename = serializers.CharField(read_only=True)
    file_format = serializers.CharField(read_only=True)
    data_output_type = serializers.CharField(read_only=True)
    usage = serializers.CharField(read_only=True)
    creation_date = serializers.CharField(read_only=True)
    created_by = serializers.CharField(read_only=True)
    extra_properties = serializers.JSONField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ExperimentResult


class SimpleInstrumentSerializer(serializers.Serializer):
    identifier = serializers.CharField(read_only=True)
    platform = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    model = serializers.CharField(read_only=True)
    extra_properties = serializers.JSONField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Instrument


def serialize_experiment_result(experiment_result: ExperimentResult) -> Dict[str, Any]:
    # .serializable_value() speeds up the response significantly
    return {
        'identifier': experiment_result.serializable_value("identifier"),
        'description': experiment_result.serializable_value("description"),
        'filename': experiment_result.serializable_value("filename"),
        'file_format': experiment_result.serializable_value("file_format"),
        'data_output_type': experiment_result.serializable_value("data_output_type"),
        'usage': experiment_result.serializable_value("usage"),
        'creation_date': experiment_result.serializable_value("creation_date"),
        'created_by': experiment_result.serializable_value("created_by"),
        'extra_properties': experiment_result.serializable_value("extra_properties"),
        'created': experiment_result.serializable_value("created"),
        'updated': experiment_result.serializable_value("updated"),
    }
    # return {
    #     'identifier': experiment_result.identifier,
    #     'description': experiment_result.description,
    #     'filename': experiment_result.filename,
    #     'file_format': experiment_result.file_format,
    #     'data_output_type': experiment_result.data_output_type,
    #     'usage': experiment_result.usage,
    #     'creation_date': experiment_result.creation_date,
    #     'created_by': experiment_result.created_by,
    #     'extra_properties': experiment_result.extra_properties,
    #     'created': experiment_result.created.isoformat(),
    #     'updated': experiment_result.updated.isoformat(),
    # }


def serialize_instrument(instrument: Instrument) -> Dict[str, Any]:
    return {
        'identifier': instrument.serializable_value("identifier"),
        'platform': instrument.serializable_value("platform"),
        'description': instrument.serializable_value("description"),
        'model': instrument.serializable_value("model"),
        'extra_properties': instrument.serializable_value("extra_properties"),
        'created': instrument.serializable_value("created"),
        'updated': instrument.serializable_value("updated"),
    }
    # return {
    #     'identifier': instrument.identifier,
    #     'platform': instrument.platform,
    #     'description': instrument.description,
    #     'model': instrument.model,
    #     'extra_properties': instrument.extra_properties,
    #     'created': instrument.created.isoformat(),
    #     'updated': instrument.updated.isoformat(),
    # }


def serialize_experiment(experiment: Experiment) -> Dict[str, Any]:
    #return experiment.serializable_value("id")
    return {
        'id': experiment.serializable_value("id"),
        'study_type': experiment.serializable_value("study_type"),
        'experiment_type': experiment.serializable_value("experiment_type"),
        'experiment_ontology': experiment.serializable_value("experiment_ontology"),

        'molecule': experiment.serializable_value("molecule"),
        'molecule_ontology': experiment.serializable_value("molecule_ontology"),
        'library_strategy': experiment.serializable_value("library_strategy"),
        'library_source': experiment.serializable_value("library_source"),

        'library_selection': experiment.serializable_value("library_selection"),
        'library_layout': experiment.serializable_value("library_layout"),
        'extraction_protocol': experiment.serializable_value("extraction_protocol"),
        'reference_registry_id': experiment.serializable_value("reference_registry_id"),
        'qc_flags': experiment.serializable_value("qc_flags"),
        'biosample': str(experiment.serializable_value("biosample")),
        'table': str(experiment.serializable_value("table")),
        'extra_properties': experiment.serializable_value("extra_properties"),
        'created': experiment.serializable_value("created"),
        'updated': experiment.serializable_value("updated"),
        #'instrument': serialize_instrument(experiment.instrument),
        #'experiment_results': [serialize_experiment_result(er) for er in experiment.experiment_results.all()]
    }
    # return {
    #     'id': experiment.id,
    #     'study_type': experiment.study_type,
    #     'experiment_type': experiment.experiment_type,
    #     'experiment_ontology': experiment.experiment_ontology,
    #
    #     'molecule': experiment.molecule,
    #     'molecule_ontology': experiment.molecule_ontology,
    #     'library_strategy': experiment.library_strategy,
    #     'library_source': experiment.library_source,
    #
    #     'library_selection': experiment.library_selection,
    #     'library_layout': experiment.library_layout,
    #     'extraction_protocol': experiment.extraction_protocol,
    #     'reference_registry_id': experiment.reference_registry_id,
    #     'qc_flags': experiment.qc_flags,
    #     'biosample': str(experiment.biosample),
    #     'table': str(experiment.table),
    #     'extra_properties': experiment.extra_properties,
    #     'created': experiment.created.isoformat(),
    #     'updated': experiment.updated.isoformat(),
    #     'instrument': serialize_instrument(experiment.instrument),
    #     'experiment_results': [serialize_experiment_result(er) for er in experiment.experiment_results.all()]
    # }


class ListExperimentSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    # study_type = serializers.CharField(read_only=True)
    experiment_type = serializers.CharField(read_only=True)

    # experiment_ontology = serializers.JSONField(read_only=True)
    # molecule = serializers.CharField(read_only=True)
    # molecule_ontology = serializers.JSONField(read_only=True)
    # library_strategy = serializers.CharField(read_only=True)
    # library_source = serializers.CharField(read_only=True)
    # library_selection = serializers.CharField(read_only=True)
    # library_layout = serializers.CharField(read_only=True)
    # extraction_protocol = serializers.CharField(read_only=True)
    # reference_registry_id = serializers.CharField(read_only=True)
    # qc_flags = serializers.ListField(read_only=True)
    # biosample = serializers.CharField(read_only=True)
    # table = serializers.CharField(read_only=True)
    # Experiment results
    # experiment_results = SimpleExperimentResultSerializer(many=True, )
    # set to a method serializer
    # experiment_results = serializers.SerializerMethodField()
    # Instrument
    # instrument = SimpleInstrumentSerializer()
    # set to a method serializer
    # instrument = serializers.SerializerMethodField()

    # extra_properties = serializers.JSONField()
    # created = serializers.DateTimeField()
    # updated = serializers.DateTimeField()

    class Meta:
        model = Experiment
        # read_only_fields = ["id", "study_type", "experiment_type", "experiment_ontology",
        #                     "molecule", "molecule_ontology", "library_strategy", "library_source",
        #                     "library_selection", "library_layout", "extraction_protocol",
        #                     "reference_registry_id", "qc_flags", "biosample", "table",
        #                     "experiment_results", "instrument", "extra_properties",
        #                     "created", "updated"]

    # def get_experiment_results(self, obj):
    #     return [serialize_experiment_result(e) for e in obj.experiment_results.all()]
    #
    # def get_instrument(self, obj):
    #     return serialize_instrument(obj.instrument)

#####################################################################
