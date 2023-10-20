from __future__ import annotations

import os

from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.renderers import BaseRenderer
from rest_framework.response import Response

from bento_lib.responses import errors

from .metadata import WORKFLOWS_PATH, workflow_set


class WDLRenderer(BaseRenderer):
    media_type = "text/plain"
    format = "text"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data.encode(self.charset)


@api_view(["GET"])
@permission_classes([AllowAny])
def workflow_list(_request):
    return Response(workflow_set.workflow_dicts_by_type_and_id())


@api_view(["GET"])
@permission_classes([AllowAny])
def workflow_item(_request, workflow_id):
    if not workflow_set.workflow_exists(workflow_id):
        return Response(errors.not_found_error(f"No workflow with ID {workflow_id}"), status=404)

    return Response(workflow_set.get_workflow(workflow_id).model_dump(mode="json"))


@api_view(["GET"])
@permission_classes([AllowAny])
@renderer_classes([WDLRenderer])
def workflow_file(_request, workflow_id):
    if not workflow_set.workflow_exists(workflow_id):
        return Response(status=404, data="Not found")

    wdl_path = os.path.join(WORKFLOWS_PATH, workflow_set.get_workflow_resource(workflow_id))
    with open(wdl_path, "r") as wf:
        return Response(wf.read())
