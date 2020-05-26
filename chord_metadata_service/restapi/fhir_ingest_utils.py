import json
import uuid
import jsonschema

from fhirclient.models import observation as obs, patient as p, condition as cond, specimen as s

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from chord_lib.responses.errors import *

from chord_metadata_service.chord.models import *
from chord_metadata_service.phenopackets.models import *

FHIR_INGEST_SCHEMA = {
    "$id": "chord_metadata_service_fhir_ingest_schema",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "description": "FHIR Ingest schema",
    "type": "object",
    "properties": {
        "dataset_id": {"type": "string"},
        "patients": {"type": "string", "description": "Path to a patients file location."},
        "observations": {"type": "string", "description": "Path to an observations file location."},
        "conditions": {"type": "string", "description": "Path to a conditions file location."},
        "specimens": {"type": "string", "description": "Path to a specimens file location."},
        "metadata": {
            "type": "object",
            "properties": {
                "created_by": {"type": "string"}
            },
            "required": ["created_by"]
        }
    },
    "required": [
        "dataset_id",
        "patients",
        "metadata"
    ],
}


FHIR_BUNDLE_SCHEMA = {
    "$id": "chord_metadata_service_fhir_bundle_schema",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "description": "FHIR Bundle schema",
    "type": "object",
    "properties": {
        "resourceType": {
            "type": "string",
            "const": "Bundle",
            "description": "Collection of resources."
        },
        "entry": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "resource": {"type": "object"}
                },
                "additionalProperties": True,
                "required": ["resource"]
            }
        }
    },
    "additionalProperties": True,
    "required": ["resourceType", "entry"]
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
        raise ValidationError(f"{additional_info+' ' if additional_info else None}errors: {error_messages}")


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

    # check if dataset exists
    if not Dataset.objects.filter(identifier=request.data["dataset_id"]).exists():
        return Response(bad_request_error(f"Dataset with ID {request.data['dataset_id']} does not exist"),
                        status=400)

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
                    dataset=Dataset.objects.get(identifier=request.data["dataset_id"])
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
                    disease= Disease.objects.create(**disease_data)
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

            except json.decoder.JSONDecodeError as e:
                return Response(bad_request_error(f"Invalid JSON provided (message: {e})"), status=400)

    return Response(status=204)


################################# FHIR to Phenopackets #################################
# There is no guide to map FHIR to Phenopackets

def patient_to_individual(obj):
    """ FHIR Patient to Individual. """

    patient = p.Patient(obj)
    individual = {
        "id": patient.id
    }
    if patient.identifier:
        individual["alternate_ids"] = [alternate_id.value for alternate_id in patient.identifier]
    gender_to_sex = {
        "male": "MALE",
        "female": "FEMALE",
        "other": "OTHER_SEX",
        "unknown": "UNKNOWN_SEX"
    }
    if patient.gender:
        individual["sex"] = gender_to_sex.get(patient.gender, "unknown")
    if patient.birthDate:
        individual["date_of_birth"] = patient.birthDate.isostring
    if patient.active:
        individual["active"] = patient.active
    if patient.deceasedBoolean:
        individual["deceased"] = patient.deceasedBoolean
    return individual


def observation_to_phenotypic_feature(obj):
    """ FHIR Observation to Phenopackets PhenotypicFeature. """

    observation = obs.Observation(obj)
    codeable_concept = observation.code  # CodeableConcept
    phenotypic_feature = {
        # id is an integer AutoField, store legacy id in description
        # TODO change
        "description": observation.id,
        "pftype": {
            "id": codeable_concept.coding[0].code,
            "label": codeable_concept.coding[0].display
            # TODO collect system info in metadata
        }
    }
    if observation.specimen:  # FK to Biosample
        phenotypic_feature["biosample"] = observation.specimen.reference
    return phenotypic_feature


def condition_to_disease(obj):
    """ FHIR Condition to Phenopackets Disease. """

    condition = cond.Condition(obj)
    codeable_concept = condition.code  # CodeableConcept
    disease = {
        # id is an integer AutoField, legacy id can be a string
        # "id": condition.id,
        "term": {
            "id": codeable_concept.coding[0].code,
            "label": codeable_concept.coding[0].display
            # TODO collect system info in metadata
        }
    }
    # condition.stage.type is only in FHIR 4.0.0 version
    return disease


def diagnostic_report_to_interpretation(obj):
    """ FHIR DiagnosticReport to Phenopackets Interpretation. """
    # it hardly maps at all
    return


def procedure_to_procedure(obj):
    """ FHIR Procedure to Phenopackets Procedure.
    The main semantic difference:
    - phenopackets procedure is a procedure performed to extract a biosample;
    - fhir procedure is a procedure performed on or for a patient
    (e.g. documentation of patient's medication)
    """

    return


def specimen_to_biosample(obj):
    """ FHIR Specimen to Phenopackets Biosample. """

    specimen = s.Specimen(obj)
    biosample = {
        "id": specimen.id
    }
    if specimen.subject:
        biosample["individual"] = specimen.subject.reference
    if specimen.type:
        codeable_concept = specimen.type  # CodeableConcept
        biosample["sampled_tissue"] = {
            "id": codeable_concept.coding[0].code,
            "label": codeable_concept.coding[0].display
            # TODO collect system info in metadata
        }
    if specimen.collection:
        method_codeable_concept = specimen.collection.method
        bodysite_codeable_concept = specimen.collection.bodySite
        biosample["procedure"] = {
            "code": {
                "id": method_codeable_concept.coding[0].code,
                "label": method_codeable_concept.coding[0].display
            },
            "body_site": {
                "id": bodysite_codeable_concept.coding[0].code,
                "label": bodysite_codeable_concept.coding[0].display
            }
        }
    return biosample
