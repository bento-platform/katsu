import chord_lib
import json
import jsonschema
import jsonschema.exceptions
import os
import uuid

from dateutil.parser import isoparse

from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.renderers import BaseRenderer
from rest_framework.response import Response

from chord_lib.responses.errors import *
from chord_lib.workflows import get_workflow, get_workflow_resource, workflow_exists

from typing import Callable

from chord_metadata_service.chord.models import *
from chord_metadata_service.phenopackets.models import *


METADATA_WORKFLOWS = {
    "ingestion": {
        "phenopackets_json": {
            "name": "Phenopackets-Compatible JSON",
            "description": "This ingestion workflow will validate and import a Phenopackets schema-compatible "
                           "JSON document.",
            "data_type": "phenopacket",
            "file": "phenopackets_json.wdl",
            "inputs": [
                {
                    "id": "json_document",
                    "type": "file",
                    "extensions": [".json"]
                }
            ],
            "outputs": [
                {
                    "id": "json_document",
                    "type": "file",
                    "value": "{json_document}"
                }
            ]
        },
    },
    "analysis": {}
}


class WDLRenderer(BaseRenderer):
    media_type = "text/plain"
    format = "text"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data.encode(self.charset)


@api_view(["GET"])
@permission_classes([AllowAny])
def workflow_list(_request):
    return Response(METADATA_WORKFLOWS)


@api_view(["GET"])
@permission_classes([AllowAny])
def workflow_item(_request, workflow_id):
    if not workflow_exists(workflow_id, METADATA_WORKFLOWS):
        return Response(not_found_error(f"No workflow with ID {workflow_id}"), status=404)

    return Response(get_workflow(workflow_id, METADATA_WORKFLOWS))


@api_view(["GET"])
@permission_classes([AllowAny])
@renderer_classes([WDLRenderer])
def workflow_file(_request, workflow_id):
    if not workflow_exists(workflow_id, METADATA_WORKFLOWS):
        return Response(status=404, data="Not found")

    wdl_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "workflows",
                            get_workflow_resource(workflow_id, METADATA_WORKFLOWS))

    with open(wdl_path, "r") as wf:
        return Response(wf.read())


def create_phenotypic_feature(pf):
    pf_obj = PhenotypicFeature(
        description=pf.get("description", ""),
        pftype=pf["type"],
        negated=pf.get("negated", False),
        severity=pf.get("severity", None),
        modifier=pf.get("modifier", []),  # TODO: Validate ontology term in schema...
        onset=pf.get("onset", None),
        evidence=pf.get("evidence", None)  # TODO: Separate class?
    )

    pf_obj.save()
    return pf_obj


# Mounted on /private/, so will get protected anyway; this allows for access from WES
# TODO: Ugly and misleading permissions
@api_view(["POST"])
@permission_classes([AllowAny])
def ingest(request):
    # Private ingest endpoints are protected by URL namespace, not by Django permissions.

    # TODO: Schema for OpenAPI doc
    # TODO: Use serializers with basic objects and maybe some more complex ones too (but for performance, this might
    #  not be optimal...)

    try:
        jsonschema.validate(request.data, chord_lib.schemas.chord.CHORD_INGEST_SCHEMA)
    except jsonschema.exceptions.ValidationError:
        return Response(bad_request_error("Invalid ingest request body"), status=400)  # TODO: Validation errors

    table_id = request.data["table_id"]

    if not Dataset.objects.filter(identifier=table_id).exists():
        return Response(bad_request_error(f"Table with ID {table_id} does not exist"), status=400)

    table_id = str(uuid.UUID(table_id))  # Normalize dataset ID to UUID's str format.

    workflow_id = request.data["workflow_id"].strip()
    workflow_outputs = request.data["workflow_outputs"]

    if not chord_lib.workflows.workflow_exists(workflow_id, METADATA_WORKFLOWS):  # Check that the workflow exists
        return Response(bad_request_error(f"Workflow with ID {workflow_id} does not exist"), status=400)

    if "json_document" not in workflow_outputs:
        return Response(bad_request_error("Missing workflow output 'json_document'"), status=400)

    with open(workflow_outputs["json_document"], "r") as jf:
        try:
            phenopacket_data = json.load(jf)
            if isinstance(phenopacket_data, list):
                for item in phenopacket_data:
                    ingest_phenopacket(item, table_id)
            else:
                ingest_phenopacket(phenopacket_data, table_id)

        except json.decoder.JSONDecodeError as e:
            return Response(bad_request_error(f"Invalid JSON provided for phenopacket document (message: {e})"),
                            status=400)

        # TODO: Schema validation
        # TODO: Rollback in case of failures
        return Response(status=204)


def _query_and_check_nulls(obj: dict, key: str, transform: Callable = lambda x: x):
    value = obj.get(key, None)
    return {f"{key}__isnull": True} if value is None or value == "" else {key: transform(value)}


def ingest_phenopacket(phenopacket_data, table_id):
    """ Ingests one phenopacket. """

    new_phenopacket_id = phenopacket_data.get("id", str(uuid.uuid4()))

    subject = phenopacket_data.get("subject", None)
    phenotypic_features = phenopacket_data.get("phenotypic_features", [])
    biosamples = phenopacket_data.get("biosamples", [])
    genes = phenopacket_data.get("genes", [])
    diseases = phenopacket_data.get("diseases", [])
    meta_data = phenopacket_data["meta_data"]

    if subject:
        subject_query = _query_and_check_nulls(subject, "date_of_birth", transform=isoparse)
        for k in ("alternate_ids", "age", "sex", "karyotypic_sex", "taxonomy"):
            subject_query.update(_query_and_check_nulls(subject, k))
        subject, _ = Individual.objects.get_or_create(id=subject["id"], **subject_query)

    phenotypic_features_db = [create_phenotypic_feature(pf) for pf in phenotypic_features]

    biosamples_db = []
    for bs in biosamples:
        # TODO: This should probably be a JSON field, or compound key with code/body_site
        procedure, _ = Procedure.objects.get_or_create(**bs["procedure"])

        bs_query = _query_and_check_nulls(bs, "individual_id", lambda i: Individual.objects.get(id=i))
        for k in ("sampled_tissue", "taxonomy", "individual_age_at_collection", "histological_diagnosis",
                  "tumor_progression", "tumor_grade"):
            bs_query.update(_query_and_check_nulls(bs, k))

        bs_obj, bs_created = Biosample.objects.get_or_create(
            id=bs["id"],
            description=bs.get("description", ""),
            procedure=procedure,
            is_control_sample=bs.get("is_control_sample", False),
            diagnostic_markers=bs.get("diagnostic_markers", []),
            **bs_query
        )

        if bs_created:
            bs_pfs = [create_phenotypic_feature(pf) for pf in bs.get("phenotypic_features", [])]
            bs_obj.phenotypic_features.set(bs_pfs)

        # TODO: Update phenotypic features otherwise?

        biosamples_db.append(bs_obj)

    # TODO: May want to augment alternate_ids
    genes_db = []
    for g in genes:
        # TODO: Validate CURIE
        # TODO: Rename alternate_id
        g_obj, _ = Gene.objects.get_or_create(
            id=g["id"],
            alternate_ids=g.get("alternate_ids", []),
            symbol=g["symbol"]
        )
        genes_db.append(g_obj)

    diseases_db = []
    for disease in diseases:
        # TODO: Primary key, should this be a model?
        d_obj, _ = Disease.objects.get_or_create(
            term=disease["term"],
            disease_stage=disease.get("disease_stage", []),
            tnm_finding=disease.get("tnm_finding", []),
            onset=disease.get("onset", None)
        )
        diseases_db.append(d_obj.id)

    resources_db = []
    for rs in meta_data.get("resources", []):
        rs_obj, _ = Resource.objects.get_or_create(
            id=rs["id"],  # TODO: This ID is a bit iffy, because they're researcher-provided
            name=rs["name"],
            namespace_prefix=rs["namespace_prefix"],
            url=rs["url"],
            version=rs["version"],
            iri_prefix=rs["iri_prefix"]
        )
        resources_db.append(rs_obj)

    meta_data_obj = MetaData(
        created_by=meta_data["created_by"],
        submitted_by=meta_data.get("submitted_by", None),
        phenopacket_schema_version="1.0.0-RC3",
        external_references=meta_data.get("external_references", [])
    )
    meta_data_obj.save()

    meta_data_obj.resources.set(resources_db)  # TODO: primary key ???

    new_phenopacket = Phenopacket(
        id=new_phenopacket_id,
        subject=subject,
        meta_data=meta_data_obj,
        dataset=Dataset.objects.get(identifier=table_id)
    )

    new_phenopacket.save()

    new_phenopacket.phenotypic_features.set(phenotypic_features_db)
    new_phenopacket.biosamples.set(biosamples_db)
    new_phenopacket.genes.set(genes_db)
    new_phenopacket.diseases.set(diseases_db)

    return new_phenopacket
