import chord_lib
import json
import jsonschema
import jsonschema.exceptions
import os
import uuid

from dateutil.parser import isoparse

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import BaseRenderer
from rest_framework.response import Response

from chord_lib.workflows import get_workflow, get_workflow_resource, workflow_exists

from chord_metadata_service.chord.models import *
from chord_metadata_service.phenopackets.models import *


METADATA_WORKFLOWS = {
    "ingestion": {
        "phenopackets_json": {
            "name": "Phenopackets-Compatible JSON",
            "description": "This ingestion workflow will validate and import a Phenopackets schema-compatible "
                           "JSON document.",
            "data_types": ["phenopacket"],
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
def workflow_list(_request):
    return Response(METADATA_WORKFLOWS)


@api_view(["GET"])
def workflow_item(_request, workflow_id):
    if not workflow_exists(workflow_id, METADATA_WORKFLOWS):
        return Response(status=404)

    return Response(get_workflow(workflow_id, METADATA_WORKFLOWS))


@api_view(["GET"])
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
        pftype=pf["type"]["id"],
        negated=pf.get("negated", False),
        severity=pf.get("severity", None),
        modifiers=[],  # TODO
        onset=pf.get("onset", None),
        evidence=pf.get("evidence", None)  # TODO: Separate class?
    )

    pf_obj.save()
    return pf_obj


@api_view(["POST"])
def ingest(request):
    # TODO: Better errors
    # TODO: Schema for OpenAPI doc
    # TODO: Use serializers with basic objects and maybe some more complex ones too (but for performance, this might
    #  not be optimal...)

    try:
        jsonschema.validate(request.data, chord_lib.schemas.chord.CHORD_INGEST_SCHEMA)
    except jsonschema.exceptions.ValidationError:
        return Response(status=400)

    dataset_id = request.data["dataset_id"]

    if not Dataset.objects.filter(dataset_id=dataset_id).exists():
        return Response(status=400)

    dataset_id = str(uuid.UUID(dataset_id))  # Normalize dataset ID to UUID's str format.

    workflow_id = request.data["workflow_id"].strip()
    workflow_outputs = request.data["workflow_outputs"]

    if not chord_lib.workflows.workflow_exists(workflow_id, METADATA_WORKFLOWS):  # Check that the workflow exists
        return Response(status=400)

    if "json_document" not in workflow_outputs:
        return Response(status=400)

    with open(workflow_outputs["json_document"], "r") as jf:
        try:
            phenopacket_data = json.load(jf)
        except json.decoder.JSONDecodeError:
            # TODO: Nicer error message
            return Response(status=400)

        # TODO: Schema validation
        # TODO: Rollback in case of failures

        new_phenopacket_id = str(uuid.uuid4())  # TODO: Is this provided?

        subject = phenopacket_data.get("subject", None)
        phenotypic_features = phenopacket_data.get("phenotypicFeatures", [])
        biosamples = phenopacket_data.get("biosamples", [])
        genes = phenopacket_data.get("genes", [])
        diseases = phenopacket_data.get("diseases", [])
        meta_data = phenopacket_data["meta_data"]

        if subject:
            subject, _ = Individual.objects.get_or_create(
                id=subject["id"],
                alternate_ids=subject.get("alternate_ids", None),
                date_of_birth=isoparse(subject["date_of_birth"]) if "date_of_birth" in subject else None,
                age=subject.get("age", ""),  # TODO: Shouldn't this be nullable, since it's recommended in the spec?
                sex=subject.get("sex", None),
                karyotypic_sex=subject.get("karyotypic_sex", None),
                taxonomy=subject.get("taxonomy", None)
            )

        phenotypic_features_db = [create_phenotypic_feature(pf) for pf in phenotypic_features]

        biosamples_db = []
        for bs in biosamples:
            # TODO: This should probably be a JSON field, or compound key with code/body_site
            procedure, _ = Procedure.objects.get_or_create(
                code=bs["procedure"]["code"],
                body_site=bs["procedure"].get("body_site", None)
            )

            bs_pfs = [create_phenotypic_feature(pf) for pf in bs.get("phenotypic_features", [])]

            bs_obj, _ = Biosample.objects.get_or_create(
                id=bs["id"],
                individual=(Individual.objects.get(id=bs["individual_id"])
                            if "individual_id" in bs else None),
                description=bs.get("description", ""),
                sampled_tissue=bs.get("sampled_tissue", None),
                taxonomy=bs.get("taxonomy", None),
                individual_age_at_collection=bs.get("individual_age_at_collection", None),
                histological_diagnosis=bs.get("histological_diagnosis", None),
                tumor_progression=bs.get("tumor_progression", None),
                tumor_grade=bs.get("tumor_grade", None),
                procedure=procedure,
                is_control_sample=bs.get("is_control_sample", False),

                diagnostic_markers=bs.get("diagnostic_markers", [])
            )

            bs_obj.phenotypic_features.set(bs_pfs)

            biosamples_db.append(bs_obj)

        # TODO: May want to augment alternate_ids
        genes_db = []
        for g in genes:
            # TODO: Validate CURIE
            # TODO: Rename alternate_id

            g_obj, _ = Gene.objects.get_or_create(
                id=g["id"],
                alternate_id=g.get("alternate_ids", []),
                symbol=g["symbol"]
            )

            genes_db.append(g_obj)

        diseases_db = []
        for d in diseases:
            # TODO: Primary key, should this be a model?

            d_obj = Disease(term=d["term"], age_of_onset=d.get("onset", None), tumor_stage=d.get("tumor_stage", []))
            d_obj.save()

        resources_db = []
        for rs in meta_data.get("resources", []):
            rs_obj = Resource(
                resource_id=rs["id"],  # TODO: This ID is a bit iffy, because they're researcher-provided
                name=rs["name"],
                namespace_prefix=rs["namespace_prefix"],
                url=rs["url"],
                version=rs["version"],
                iri_prefix=rs["iri_prefix"]
            )
            rs_obj.save()
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
            dataset=Dataset.objects.get(dataset_id=dataset_id)
        )
        new_phenopacket.save()

        new_phenopacket.phenotypic_features.set(phenotypic_features_db)
        new_phenopacket.biosamples.set(biosamples_db)
        new_phenopacket.genes.set(genes_db)
        new_phenopacket.diseases.set(diseases_db)

        return Response(status=204)
