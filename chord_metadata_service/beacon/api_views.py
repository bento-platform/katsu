from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from adrf.decorators import api_view
from bento_lib.auth.permissions import P_QUERY_DATA
from bento_lib.auth.resources import RESOURCE_EVERYTHING
from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoAllowAny, BentoAllowAnyReadOnly, BentoDeferToHandler


async def _data_endpoint(request: Request, _entry_id: str | None = None):
    await authz_middleware.async_evaluate_one(request, RESOURCE_EVERYTHING, P_QUERY_DATA, mark_authz_done=True)
    return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])  # fix permissions here and below
async def individuals(request: Request, entry_id: str | None = None):
    return await _data_endpoint(request, entry_id)


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def individual_biosamples(request: Request, entry_id: str):
    return await _data_endpoint(request, entry_id)


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def biosamples(request: Request, entry_id: str | None = None):
    return await _data_endpoint(request, entry_id)


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def g_variant_biosamples(request: Request, entry_id: str):
    return await _data_endpoint(request, entry_id)


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def g_variant_individuals(request: Request, entry_id: str):
    return await _data_endpoint(request, entry_id)


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def biosample_runs(request: Request, entry_id: str):
    return await _data_endpoint(request, entry_id)


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def biosample_analyses(request: Request, entry_id: str):
    return await _data_endpoint(request, entry_id)


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def filtering_terms(request: Request, entry_id: str | None = None):
    return await _data_endpoint(request, entry_id)


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def g_variants(request: Request, entry_id: str | None = None):
    return await _data_endpoint(request, entry_id)


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def runs(request: Request, entry_id: str | None = None):
    return await _data_endpoint(request, entry_id)


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def analyses(request: Request, entry_id: str | None = None):
    return await _data_endpoint(request, entry_id)


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def cohorts(request: Request, entry_id: str | None = None):
    return await _data_endpoint(request, entry_id)


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def datasets(request: Request, entry_id: str | None = None):
    return await _data_endpoint(request, entry_id)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
def service_info(_request: Request):
    return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
def info(_request: Request):
    return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
def configuration(_request: Request):
    return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
def map(_request: Request):
    return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
def entry_types(_request: Request):
    return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
