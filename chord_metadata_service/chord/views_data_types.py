import asyncio

from bento_lib.auth.permissions import P_DELETE_DATA
from bento_lib.auth.resources import build_resource
from bento_lib.responses import errors
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from adrf.decorators import api_view
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response

from typing import Callable

from chord_metadata_service.authz.middleware import authz_middleware as authz
from chord_metadata_service.authz.permissions import BentoAllowAny, BentoDeferToHandler
from chord_metadata_service.authz.types import DataPermissions
from chord_metadata_service.cleanup import run_all_cleanup
from chord_metadata_service.discovery.censorship import thresholded_count
from chord_metadata_service.discovery.exceptions import DiscoveryScopeException
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope, get_request_discovery_scope
from chord_metadata_service.discovery.utils import get_discovery_data_type_permissions
from chord_metadata_service.experiments.models import Experiment
from chord_metadata_service.logger import logger
from chord_metadata_service.phenopackets.models import Phenopacket

from . import data_types as dt
from .models import Dataset, DatasetV2, Project

QUERYSET_FN: dict[str, Callable] = {
    dt.DATA_TYPE_EXPERIMENT: lambda dataset_id: Experiment.objects.filter(dataset_id=dataset_id),
    dt.DATA_TYPE_PHENOPACKET: lambda dataset_id: Phenopacket.objects.filter(dataset_id=dataset_id),
}


def not_found_response(message: str) -> Response:
    return Response(errors.not_found_error(message), status=status.HTTP_404_NOT_FOUND)


async def _filtered_query(data_type: str, scope: ValidatedDiscoveryScope) -> QuerySet:
    """
    Returns a filtered query based on the data type, project, and dataset.
    """

    q: QuerySet | None = None

    if data_type in (dt.DATA_TYPE_PHENOPACKET, dt.DATA_TYPE_EXPERIMENT):
        q = (Phenopacket if data_type == dt.DATA_TYPE_PHENOPACKET else Experiment).objects.prefetch_related("dataset")
        if (dataset := scope.dataset_id) is not None:
            q = q.filter(dataset_id=dataset)
        if (project := scope.project_id) is not None:
            q = q.filter(dataset__project_id=project)

    if q is None:
        raise ValueError(f"Unsupported data type: {data_type}")

    return q


async def get_count_for_data_type(
    data_type: str,
    scope: ValidatedDiscoveryScope,
    permissions: DataPermissions,
) -> int:
    """
    Returns the count for a particular data type. If dataset is provided, project will be ignored. If neither are
    provided, the count will be for the whole node.
    """
    q = await _filtered_query(data_type, scope)
    return thresholded_count(await q.acount(), scope.discovery, permissions)


async def get_last_ingested_for_data_type(data_type: str, scope: ValidatedDiscoveryScope) -> dict | None:

    q = await _filtered_query(data_type, scope)
    latest_obj = await q.order_by('-created').afirst()

    if not latest_obj:
        return None

    return latest_obj.created


async def make_data_type_response_object(
    data_type_id: str,
    data_type_details: dict,
    scope: ValidatedDiscoveryScope,
    permissions: DataPermissions,
) -> dict:
    return {
        **data_type_details,
        "id": data_type_id,
        **(
            {"count": await get_count_for_data_type(data_type_id, scope, permissions)}
            if permissions.counts else {}
        ),
        "last_ingested": await get_last_ingested_for_data_type(data_type_id, scope)
    }


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def data_type_list(request: DrfRequest):
    # TODO: Permissions: only return counts when we are authenticated/have access to counts or full data.

    try:
        discovery_scope = await get_request_discovery_scope(request)
    except DiscoveryScopeException as e:
        # Does not exist, or a UUID validation error - used to be triggered later but scope validation does some of the
        # Django validation for us.
        return not_found_response(e.message)

    dt_permissions = await get_discovery_data_type_permissions(request, discovery_scope)

    dt_response: list[dict] = list(
        await asyncio.gather(*(
            make_data_type_response_object(dt_id, dt_d, discovery_scope, dt_permissions[dt_id])
            for dt_id, dt_d in dt.DATA_TYPES.items()
        ))
    )

    dt_response.sort(key=lambda d: d["id"])
    return Response(dt_response)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def data_type_detail(request: DrfRequest, data_type: str):
    # TODO: Permissions: only return counts when we are authenticated/have access to counts or full data.

    if data_type not in dt.DATA_TYPES:
        return Response(errors.not_found_error(f"Data type {data_type} not found"), status=status.HTTP_404_NOT_FOUND)

    try:
        discovery_scope = await get_request_discovery_scope(request)
    except DiscoveryScopeException as e:
        # Does not exist, or a UUID validation error - used to be triggered later but scope validation does some of the
        # Django validation for us.
        return not_found_response(e.message)

    # TODO: just get the one data type
    dt_permissions = await get_discovery_data_type_permissions(request, discovery_scope)

    return Response(
        await make_data_type_response_object(
            data_type, dt.DATA_TYPES[data_type], discovery_scope, dt_permissions[data_type]
        )
    )


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def data_type_schema(_request: DrfRequest, data_type: str):
    # TODO: exclude extra_properties schema
    if data_type not in dt.DATA_TYPES:
        return not_found_response(f"Data type {data_type} not found")

    return Response(dt.DATA_TYPES[data_type]["schema"])


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def data_type_metadata_schema(_request: DrfRequest, data_type: str):
    if data_type not in dt.DATA_TYPES:
        return not_found_response(errors.not_found_error(f"Data type {data_type} not found"))

    return Response(dt.DATA_TYPES[data_type]["metadata_schema"])


@api_view(["GET", "DELETE"])
@permission_classes([BentoDeferToHandler])
async def dataset_data_type(request: DrfRequest, dataset_id: str, data_type: str):
    try:
        dataset = await Dataset.objects.aget(identifier=dataset_id)
    except (Dataset.DoesNotExist, ValidationError) as e:
        authz.mark_authz_done(request)
        return not_found_response(str(e))

    project = await Project.objects.aget(datasets=dataset)
    project_id = str(project.identifier)

    if data_type not in QUERYSET_FN:
        authz.mark_authz_done(request)
        return not_found_response(f"Data type {data_type} doesn't exist")

    qs = QUERYSET_FN[data_type](dataset_id)

    if request.method == "DELETE":
        if not (
            await authz.async_evaluate_one(request, build_resource(project_id, dataset_id, data_type), P_DELETE_DATA)
        ):
            authz.mark_authz_done(request)
            return Response(errors.forbidden_error(), status=status.HTTP_403_FORBIDDEN)

        authz.mark_authz_done(request)

        await qs.adelete()

        lg = logger.bind(dataset_id=dataset_id, data_type=data_type)
        n_removed = await run_all_cleanup(lg)
        await lg.ainfo("ran cleanup after clearing data type via API", n_removed=n_removed)

        return Response(status=status.HTTP_204_NO_CONTENT)

    # we've already validated that the project and dataset exist above, so we are allowed to directly build a validated
    # discovery scope.
    discovery_scope = ValidatedDiscoveryScope(project, dataset)

    dt_permissions = await get_discovery_data_type_permissions(request, discovery_scope)

    response_object = await make_data_type_response_object(
        data_type,
        dt.DATA_TYPES[data_type],
        discovery_scope,
        permissions=dt_permissions[data_type],
    )

    authz.mark_authz_done(request)
    return Response(response_object)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def dataset_data_type_summary(request: DrfRequest, dataset_id: str):
    try:
        dataset = await Dataset.objects.aget(identifier=dataset_id)
    except (Dataset.DoesNotExist, ValidationError) as e:
        return not_found_response(str(e))

    # we've already validated that the project and dataset exist above, so we can build an instance of
    # ValidatedDiscoveryScope directly.
    discovery_scope = ValidatedDiscoveryScope(await Project.objects.aget(datasets=dataset), dataset)
    dt_permissions = await get_discovery_data_type_permissions(request, discovery_scope)

    dt_response = sorted(
        await asyncio.gather(*(
            make_data_type_response_object(dt_id, dt_d, discovery_scope, dt_permissions[dt_id])
            for dt_id, dt_d in dt.DATA_TYPES.items()
        )),
        key=lambda d: d["id"]
    )

    return Response(dt_response)


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def dataset_v2_data_type_summary(request: DrfRequest, identifier: str):
    try:
        dataset = await DatasetV2.objects.aget(identifier=identifier)
    except DatasetV2.DoesNotExist:
        return not_found_response(f"Dataset {identifier} not found")

    project = await Project.objects.aget(identifier=dataset.project_id)
    discovery_scope = ValidatedDiscoveryScope(project, dataset)
    dt_permissions = await get_discovery_data_type_permissions(request, discovery_scope)

    dt_response = sorted(
        await asyncio.gather(*(
            make_data_type_response_object(dt_id, dt_d, discovery_scope, dt_permissions[dt_id])
            for dt_id, dt_d in dt.DATA_TYPES.items()
        )),
        key=lambda d: d["id"],
    )
    return Response(dt_response)


@api_view(["GET", "DELETE"])
@permission_classes([BentoDeferToHandler])
async def dataset_v2_data_type(request: DrfRequest, identifier: str, data_type: str):
    try:
        dataset = await DatasetV2.objects.aget(identifier=identifier)
    except DatasetV2.DoesNotExist:
        authz.mark_authz_done(request)
        return not_found_response(f"Dataset {identifier} not found")

    project = await Project.objects.aget(identifier=dataset.project_id)
    project_id = str(project.identifier)

    if data_type not in QUERYSET_FN:
        authz.mark_authz_done(request)
        return not_found_response(f"Data type {data_type} doesn't exist")

    qs = QUERYSET_FN[data_type](identifier)

    if request.method == "DELETE":
        if not (
            await authz.async_evaluate_one(request, build_resource(project_id, identifier, data_type), P_DELETE_DATA)
        ):
            authz.mark_authz_done(request)
            return Response(errors.forbidden_error(), status=status.HTTP_403_FORBIDDEN)

        authz.mark_authz_done(request)
        await qs.adelete()
        lg = logger.bind(dataset_id=identifier, data_type=data_type)
        n_removed = await run_all_cleanup(lg)
        await lg.ainfo("ran cleanup after clearing data type via API", n_removed=n_removed)
        return Response(status=status.HTTP_204_NO_CONTENT)

    discovery_scope = ValidatedDiscoveryScope(project, dataset)
    dt_permissions = await get_discovery_data_type_permissions(request, discovery_scope)
    response_object = await make_data_type_response_object(
        data_type, dt.DATA_TYPES[data_type], discovery_scope, permissions=dt_permissions[data_type],
    )
    authz.mark_authz_done(request)
    return Response(response_object)
