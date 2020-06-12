import uuid
import json

from .mappings.mappings import *
from .mappings.mcode_profiles import *
from chord_metadata_service.restapi.schemas import FHIR_BUNDLE_SCHEMA
from chord_metadata_service.restapi.fhir_ingest import _check_schema
from chord_metadata_service.restapi.fhir_utils import patient_to_individual


def observation_to_labs_vital(resource):
    """ Observation with tumor marker to LabsVital. """
    labs_vital = {
        "id": resource["id"]
    }
    if "code" in resource:
        labs_vital["tumor_marker_code"] = {
            "id": f"{resource['code']['coding'][0]['system']}:{resource['code']['coding'][0]['code']}",
            "label": f"{resource['code']['coding'][0]['display']}"
        }
    if "valueCodeableConcept" in resource:
        labs_vital["tumor_marker_data_value"] = {
            "id": f"{resource['valueCodeableConcept']['coding'][0]['system']}:{resource['code']['coding'][0]['code']}",
            "label": f"{resource['valueCodeableConcept']['coding'][0]['display']}"
        }
    return labs_vital


def condition_to_cancer_condition(resource):
    """ FHIR Condition to Mcode Cancer Condition. """

    cancer_condition = {}
    cancer_condition["id"] = resource["id"]
    # condition = cond.Condition(resource)
    if "clinicalStatus" in resource:
        cancer_condition["clinical_status"] = {
            "id": f"{resource['clinicalStatus']['coding'][0]['code']}",
            "label": f"{resource['clinicalStatus']['coding'][0]['code']}"
        }
    if "verificationStatus" in resource:
        cancer_condition["verification_status"] = {
            "id": f"{resource['verificationStatus']['coding'][0]['code']}",
            "label": f"{resource['verificationStatus']['coding'][0]['code']}"
        }
    if "code" in resource:
        cancer_condition["code"] = {
            "id": f"{resource['code']['coding'][0]['system']}:{resource['code']['coding'][0]['code']}",
            "label": f"{resource['code']['coding'][0]['display']}"
        }
    if "recordedDate" in resource:
        cancer_condition["date_of_diagnosis"] = resource["recordedDate"]
    if "bodySite" in resource:
        cancer_condition["body_site"] = []
        for item in resource["bodySite"]['coding']:
            coding = {
                "id": f"{item['system']}:{item['code']}",
                "label": f"{item['display']}",
            }
            cancer_condition["body_site"].append(coding)
    if "laterality" in resource:
        cancer_condition["laterality"] = {
            "id": f"{resource['laterality']['coding'][0]['system']}:"
                  f"{resource['laterality']['coding'][0]['code']}",
            "label": f"{resource['laterality']['coding'][0]['display']}"
        }
    if "histologyMorphologyBehavior" in resource:
        cancer_condition["histology_morphology_behavior"] = {
            "id": f"{resource['histologyMorphologyBehavior']['coding'][0]['system']}:"
                  f"{resource['histologyMorphologyBehavior']['coding'][0]['code']}",
            "label": f"{resource['histologyMorphologyBehavior']['coding'][0]['display']}"
        }
    return cancer_condition


def parse_bundle(bundle):
    """
    Parse fhir Bundle and extract all relevant profiles.
    :param bundle: FHIR resourceType Bundle object
    :return:
    """
    _check_schema(FHIR_BUNDLE_SCHEMA, bundle, 'bundle')
    mcodepacket = {
        "id": str(uuid.uuid4())
    }
    tumor_markers = []
    for item in bundle["entry"]:
        resource = item["resource"]
        if resource["resourceType"] == "Patient":
            # patient = patient_to_individual(resource)
            mcodepacket["subject"] = {
                "id": resource["id"]
            }
        if resource["resourceType"] == "Condition":
            resource_profiles = resource["meta"]["profile"]
            cancer_conditions = [MCODE_PRIMARY_CANCER_CONDITION, MCODE_SECONDARY_CANCER_CONDITION]
            for cc in cancer_conditions:
                if cc in resource_profiles:
                    cancer_condition = condition_to_cancer_condition(resource)
                    for key, value in MCODE_PROFILES_MAPPING["cancer_condition"]["profile"].items():
                        if cc == value:
                            cancer_condition["condition_type"] = key
                            mcodepacket["cancer_condition"] = cancer_condition

        if resource["resourceType"] == "Observation" and "meta" in resource:
            if MCODE_TUMOR_MARKER in resource["meta"]["profile"]:
                labs_vital = observation_to_labs_vital(resource)
                tumor_markers.append(labs_vital)
    mcodepacket["tumor_marker"] = tumor_markers

    return mcodepacket
