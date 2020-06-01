import json
import jsonschema
import jsonschema.exceptions
import os
import uuid

from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.renderers import BaseRenderer
from rest_framework.response import Response

from chord_lib.schemas.chord import CHORD_INGEST_SCHEMA
from chord_lib.responses import errors
from chord_lib.workflows import get_workflow, get_workflow_resource, workflow_exists

from .data_types import DATA_TYPE_EXPERIMENT
from .ingest import METADATA_WORKFLOWS, WORKFLOWS_PATH, DATA_TYPE_INGEST_FUNCTION_MAP, ingest_resource
from .models import Table, TableOwnership


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
        return Response(errors.not_found_error(f"No workflow with ID {workflow_id}"), status=404)

    return Response(get_workflow(workflow_id, METADATA_WORKFLOWS))


@api_view(["GET"])
@permission_classes([AllowAny])
@renderer_classes([WDLRenderer])
def workflow_file(_request, workflow_id):
    if not workflow_exists(workflow_id, METADATA_WORKFLOWS):
        return Response(status=404, data="Not found")

    wdl_path = os.path.join(WORKFLOWS_PATH, get_workflow_resource(workflow_id, METADATA_WORKFLOWS))
    with open(wdl_path, "r") as wf:
        return Response(wf.read())


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
        jsonschema.validate(request.data, CHORD_INGEST_SCHEMA)
    except jsonschema.exceptions.ValidationError:
        return Response(errors.bad_request_error("Invalid ingest request body"), status=400)  # TODO: Validation errors

    table_id = request.data["table_id"]

    if not Table.objects.filter(ownership_record_id=table_id).exists():
        return Response(errors.bad_request_error(f"Table with ID {table_id} does not exist"), status=400)

    table_id = str(uuid.UUID(table_id))  # Normalize dataset ID to UUID's str format.

    dataset = TableOwnership.objects.get(table_id=table_id).dataset

    workflow_id = request.data["workflow_id"].strip()
    workflow_outputs = request.data["workflow_outputs"]

    if not workflow_exists(workflow_id, METADATA_WORKFLOWS):  # Check that the workflow exists
        return Response(errors.bad_request_error(f"Workflow with ID {workflow_id} does not exist"), status=400)

    workflow = get_workflow(workflow_id, METADATA_WORKFLOWS)

    if "json_document" not in workflow_outputs:
        return Response(errors.bad_request_error("Missing workflow output 'json_document'"), status=400)

    with open(workflow_outputs["json_document"], "r") as jf:
        try:
            dt = workflow["data_type"]
            json_data = json.load(jf)
            ingest_fn = DATA_TYPE_INGEST_FUNCTION_MAP[dt]

            # TODO: Better mechanism for workflow-specific ingestion handling

            if dt == DATA_TYPE_EXPERIMENT:
                for rs in json_data.get("resources", []):
                    dataset.additional_resources.add(ingest_resource(rs))

                for exp in json_data.get("experiments", []):
                    ingest_fn(exp, table_id)

            elif isinstance(json_data, list):
                for obj in json_data:
                    ingest_fn(obj, table_id)

            else:
                ingest_fn(json_data, table_id)

        except json.decoder.JSONDecodeError as e:
            return Response(errors.bad_request_error(f"Invalid JSON provided for ingest document (message: {e})"),
                            status=400)

        # TODO: Schema validation
        # TODO: Rollback in case of failures
        return Response(status=204)
