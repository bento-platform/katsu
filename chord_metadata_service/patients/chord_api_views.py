import chord_lib
import os

from jsonschema import validate, ValidationError

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import BaseRenderer
from rest_framework.response import Response

from chord_lib.workflows import get_workflow, get_workflow_resource, workflow_exists


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
        return Response(status=404)

    wdl_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "workflows",
                            get_workflow_resource(workflow_id, METADATA_WORKFLOWS))

    with open(wdl_path, "r") as wf:
        return Response(wf.read())


@api_view(["POST"])
def ingest(request):
    try:
        validate(request.data, chord_lib.schemas.chord.CHORD_INGEST_SCHEMA)
    except ValidationError:
        return Response(status=400)

    # TODO: Schema for OpenAPI doc
    # TODO
