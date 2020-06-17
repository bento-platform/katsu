import uuid
import jsonschema
import logging

from chord_metadata_service.restapi.schemas import FHIR_BUNDLE_SCHEMA
from chord_metadata_service.patients.models import Individual

from .parse_fhir_mcode import parse_bundle
from .models import *


logger = logging.getLogger("mcode_ingest")
logger.setLevel(logging.INFO)


def ingest_mcodepacket(mcodepacket_data):
    """ Ingests a single mcodepacket in mcode app and patients' metadata int patients app."""
    new_mcodepacket = mcodepacket_data["id"]
    subject = mcodepacket_data["subject"]
    genomics_report_data = mcodepacket_data.get("genomics_report", None)
    cancer_condition_data = mcodepacket_data.get("cancer_condition", None)
    cancer_related_procedures = mcodepacket_data.get("cancer_related_procedures", None)
    medication_statement_data = mcodepacket_data.get("medication_statement", None)
    date_of_death_data = mcodepacket_data.get("date_of_death", None)
    cancer_disease_status_data = mcodepacket_data.get("cancer_disease_status", None)
    tumor_markers = mcodepacket_data.get("tumor_marker", None)

    # get and create Patient
    if subject:
        subject, _ = Individual.objects.get_or_create(**subject)

    if genomics_report_data:
        # don't have data for genomics report yet
        pass

    # get and create CancerCondition
    if cancer_condition_data:
        cancer_condition, _ = CancerCondition.objects.get_or_create(**cancer_condition_data)
        new_mcodepacket["cancer_condition"] = cancer_condition
        if "tnm_staging" in cancer_condition_data:
            for tnms in cancer_condition_data["tnm_staging"]:
                tnm_staging, _ = TNMStaging.objects.get_or_create(**tnms)

    # get and create Cancer Related Procedure
    crprocedures = []
    if cancer_related_procedures:
        for crp in cancer_related_procedures:
            cancer_related_procedure, _ = CancerRelatedProcedure.objects.get_or_create(
                id=crp["id"],
                code=crp["code"],
                procedure_type=crp["procedure_type"],
                body_site= crp.get("body_site", None),
                laterality=crp.get("laterality", None),
                treatment_intent=crp.get("treatment_intent", None),
                reason_code=crp.get("reason_code", None),
                extra_properties=crp.get("extra_properties", None)
            )
            crprocedures.append(cancer_related_procedure)
            if "reason_reference" in crp:
                for rr_id in crp["reason_reference"]:
                    related_cancer_condition = CancerCondition.objects.get(id=rr_id)
                    cancer_related_procedure.add(related_cancer_condition)

    # get and create CancerCondition
    if medication_statement_data:
        medication_statement, _ = MedicationStatement.objects.get_or_create(
            id=medication_statement_data["id"],
            medication_code=medication_statement_data["medication_code"]
        )
        new_mcodepacket["medication_statement"] = medication_statement

    # get date of death
    if date_of_death_data:
        new_mcodepacket["date_of_death"] = date_of_death_data

    # get cancer disease status
    if cancer_disease_status_data:
        new_mcodepacket["cancer_disease_status"] = cancer_disease_status_data

    # get tumor marker
    if tumor_markers:
        for tm in tumor_markers:
            tumor_marker, _ = LabsVital.objects.get_or_create(
                tumor_marker_code=tm["tumor_marker_code"],
                tumor_marker_data_value=tm.get("tumor_marker_data_value", None),
                individual=tm["individual"]
            )

    return new_mcodepacket
