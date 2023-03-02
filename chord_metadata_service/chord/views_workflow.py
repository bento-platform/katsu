from __future__ import annotations

import os

from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.renderers import BaseRenderer
from rest_framework.response import Response

from bento_lib.responses import errors
from bento_lib.workflows import get_workflow, get_workflow_resource, workflow_exists

from .workflows.metadata import METADATA_WORKFLOWS, WORKFLOWS_PATH


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
