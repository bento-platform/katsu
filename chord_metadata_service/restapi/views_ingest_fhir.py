import json
import uuid
import jsonschema

from .schemas import FHIR_INGEST_SCHEMA, FHIR_BUNDLE_SCHEMA
from .fhir_utils import (
    patient_to_individual,
    observation_to_phenotypic_feature,
    condition_to_disease,
    specimen_to_biosample
)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from chord_lib.responses.errors import *

from chord_metadata_service.chord.models import *
from chord_metadata_service.phenopackets.models import *


INGEST_BODY_EXAMPLE = {
    "table_id": "62b5fc67-d925-4409-bb59-e1e9a1ef10ae",
    "patients": "examples/patients.json",
    "observations": "examples/observations.json",
    "conditions": "examples/conditions.json",
    "specimens": "examples/specimens.json",
    "metadata": {
        "created_by": "Ksenia Zaytseva"
    }
}


def _parse_reference(ref):
    """ FHIR test data has reference object in a format "ResourceType/uuid" """
    return ref.split('/')[-1]


def _check_schema(schema, obj, additional_info=None):
    """ Validates schema and catches errors. """
    try:
        jsonschema.validate(obj, schema)
    except jsonschema.exceptions.ValidationError:
        v = jsonschema.Draft7Validator(schema)
        errors = [e for e in v.iter_errors(obj)]
        error_messages = []
        for i, error in enumerate(errors, 1):
            error_messages.append(f"{i} validation error {'.'.join(str(v) for v in error.path)}: {error.message}")
        raise ValidationError(f"{additional_info + ' ' if additional_info else None}errors: {error_messages}")


@api_view(["POST"])
@permission_classes([AllowAny])
def ingest_fhir(request):
    """
    View to ingest FHIR data.
    Takes FHIR Bundles (collections of resources) of the following types:
    Patient, Observation, Condition, Specimen.
    """

    # check schema of ingest body
    _check_schema(FHIR_INGEST_SCHEMA, request.data, 'ingest body')

    # check if table exists
    table_id = request.data["table_id"]

    if not Table.objects.filter(ownership_record_id=table_id).exists():
        return Response(bad_request_error(f"Table with ID {table_id} does not exist"), status=400)

    # patients-individuals
    with open(request.data["patients"], "r") as p_file:
        try:
            patients_data = json.load(p_file)
            # check if Patients data follows FHIR Bundle schema
            _check_schema(FHIR_BUNDLE_SCHEMA, patients_data, 'patients data')
            for item in patients_data["entry"]:
                individual_data = patient_to_individual(item["resource"])
                individual, _ = Individual.objects.get_or_create(**individual_data)
                # create metadata for Phenopacket
                meta_data_obj, _ = MetaData.objects.get_or_create(
                    created_by=request.data["metadata"]["created_by"],
                    phenopacket_schema_version="1.0.0-RC3",
                    external_references=[]
                )
                # create new phenopacket for each individual
                phenopacket = Phenopacket.objects.create(
                    id=str(uuid.uuid4()),
                    subject=individual,
                    meta_data=meta_data_obj,
                    table=Table.objects.get(ownership_record_id=table_id)
                )
                print(f'Phenopacket {phenopacket.id} created')
        except json.decoder.JSONDecodeError as e:
            return Response(bad_request_error(f"Invalid JSON provided (message: {e})"), status=400)

    # observations-phenotypicFeatures
    if "observations" in request.data:
        with open(request.data["observations"], "r") as obs_file:
            try:
                observations_data = json.load(obs_file)
                # check if Observations data follows FHIR Bundle schema
                _check_schema(FHIR_BUNDLE_SCHEMA, observations_data, 'observations data')
                for item in observations_data["entry"]:
                    phenotypic_feature_data = observation_to_phenotypic_feature(item["resource"])
                    # Observation must have a subject
                    if not item["resource"]["subject"]:
                        return Response(bad_request_error(f"Observation's subject is required."), status=404)

                    subject = _parse_reference(item["resource"]["subject"]["reference"])
                    phenotypic_feature, _ = PhenotypicFeature.objects.get_or_create(
                        phenopacket=Phenopacket.objects.get(subject=Individual.objects.get(id=subject)),
                        **phenotypic_feature_data
                    )
            except json.decoder.JSONDecodeError as e:
                return Response(bad_request_error(f"Invalid JSON provided (message: {e})"), status=400)

    # conditions-diseases
    if "conditions" in request.data:
        with open(request.data["conditions"]) as c_file:
            try:
                conditions_data = json.load(c_file)
                # check if Conditions data follows FHIR Bundle schema
                _check_schema(FHIR_BUNDLE_SCHEMA, conditions_data, 'conditions data')
                for item in conditions_data["entry"]:
                    disease_data = condition_to_disease(item["resource"])
                    disease = Disease.objects.create(**disease_data)
                    # Condition must have a subject
                    if not item["resource"]["subject"]:
                        return Response(bad_request_error(f"Subject is required."), status=404)
                    subject = _parse_reference(item["resource"]["subject"]["reference"])
                    phenopacket = Phenopacket.objects.get(subject=Individual.objects.get(id=subject))
                    phenopacket.diseases.add(disease)

            except json.decoder.JSONDecodeError as e:
                return Response(bad_request_error(f"Invalid JSON provided (message: {e})"), status=400)

    # specimens-biosamples
    if "specimens" in request.data:
        with open(request.data["specimens"], "r") as s_file:
            try:
                specimens_data = json.load(s_file)
                # check if Specimens data follows FHIR Bundle schema
                _check_schema(FHIR_BUNDLE_SCHEMA, specimens_data, 'specimens data')
                for item in specimens_data["entry"]:
                    biosample_data = specimen_to_biosample(item["resource"])
                    procedure, _ = Procedure.objects.get_or_create(**biosample_data["procedure"])
                    # Specimen must have a subject
                    if not biosample_data["individual"]:
                        return Response(bad_request_error(f"Specimen's subject is required."), status=404)

                    individual_id = _parse_reference(biosample_data["individual"])
                    biosample, _ = Biosample.objects.get_or_create(
                        id=biosample_data["id"],
                        procedure=procedure,
                        individual=Individual.objects.get(id=individual_id),
                        sampled_tissue=biosample_data["sampled_tissue"]
                    )
                    phenopacket = Phenopacket.objects.get(subject=Individual.objects.get(id=individual_id))
                    phenopacket.biosamples.add(biosample)


            except json.decoder.JSONDecodeError as e:
                return Response(bad_request_error(f"Invalid JSON provided (message: {e})"), status=400)

    return Response(status=204)
