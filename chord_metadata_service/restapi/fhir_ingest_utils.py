import json
import uuid

from fhirclient.models import observation as obs, patient as p, condition as cond, specimen as s

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from chord_lib.responses.errors import *

from chord_metadata_service.chord.models import *
from chord_metadata_service.phenopackets.models import *

FHIR_INGEST = {
    "dataset_id": "",
    "patients": "",
    "observations": "",
    "conditions": "",
    "specimens": ""
}


@api_view(["POST"])
@permission_classes([AllowAny])
def ingest_fhir(request):
    if not request.data["dataset_id"]:
        return Response(bad_request_error(f"Dataset ID is required."), status=404)
    else:
        if not Dataset.objects.filter(identifier=request.data["dataset_id"]).exists():
            return Response(bad_request_error(f"Dataset with ID {request.data['dataset_id']} does not exist"), status=400)

    if not request.data["patients"]:
        return Response(bad_request_error(f"Patients data is required."), status=404)


    # create new phenopacket for each individual, it uuid, subject, meta_data and dataset_id
    # fake metadata
    meta_data_obj = MetaData.objects.create(
        created_by="unknown",
        submitted_by="unknown",
        phenopacket_schema_version="1.0.0-RC3",
        external_references=[]
    )

    with open(request.data["patients"], "r") as p_file:
        try:
            patients_data = json.load(p_file)
            if isinstance(patients_data, dict):
                # List of FHIR resources is of ResourceType "Bundle"
                for item in patients_data["entry"]:
                    individual_data = patient_to_individual(item["resource"])
                    individual, _ = Individual.objects.get_or_create(**individual_data)
                    phenopacket = Phenopacket.objects.create(
                        id=str(uuid.uuid4()),
                        subject=individual,
                        meta_data=meta_data_obj,
                        dataset=Dataset.objects.get(identifier=request.data["dataset_id"])
                    )
                    print(f'Phenopacket {phenopacket.id} created')
        except json.decoder.JSONDecodeError as e:
            return Response(bad_request_error(f"Invalid JSON provided (message: {e})"), status=400)

    with open(request.data["observations"], "r") as obs_file:
        try:
            observations_data = json.load(obs_file)
            for item in observations_data["entry"]:
                phenotypic_feature_data = observation_to_phenotypic_feature(item["resource"])
                if not item["resource"]["subject"]:
                    return Response(bad_request_error(f"Subject is required."), status=404)
                # FHIR test data has reference object in a format "ResourceType/uuid"
                subject = item["resource"]["subject"]["reference"].split('Patient/')[1] # Individual ID
                phenotypic_feature, _ = PhenotypicFeature.objects.get_or_create(
                    phenopacket=Phenopacket.objects.get(subject=Individual.objects.get(id=subject)),
                    **phenotypic_feature_data
                )
        except json.decoder.JSONDecodeError as e:
            return Response(bad_request_error(f"Invalid JSON provided (message: {e})"), status=400)

    with open(request.data["conditions"]) as c_file:
        try:
            conditions_data = json.load(c_file)
            for item in conditions_data["entry"]:
                disease_data = condition_to_disease(item["resource"])
                disease = Disease.objects.create(**disease_data)
                if not item["resource"]["subject"]:
                    return Response(bad_request_error(f"Subject is required."), status=404)
                # FHIR test data has reference object in a format "ResourceType/uuid"
                subject = item["resource"]["subject"]["reference"].split('Patient/')[1] # Individual ID
                # a1.publications.add(p1)
                phenopacket = Phenopacket.objects.get(subject=Individual.objects.get(id=subject))
                phenopacket.diseases.add(disease)

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
