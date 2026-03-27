import asyncio
import itertools
import json

from adrf.decorators import api_view as async_api_view
from asgiref.sync import sync_to_async
from bento_lib.auth.permissions import P_QUERY_DATA
from bento_lib.responses import errors
from bento_lib.search import build_search_response, postgres
from datetime import datetime
from django.db import connection
from django.db.models import Count, F, Q, QuerySet
from django.db.models.functions import Coalesce
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.exceptions import ValidationError
from psycopg2 import sql
from rest_framework.decorators import permission_classes
from rest_framework.request import Request as DrfRequest
from rest_framework.response import Response
from rest_framework import status
from structlog.stdlib import BoundLogger

from typing import Awaitable, Callable

from chord_metadata_service.authz.helpers import get_data_type_query_permissions
from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoAllowAny, BentoDeferToHandler

from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope, get_request_discovery_scope

from chord_metadata_service.experiments.api_views import EXPERIMENT_SELECT_REL, EXPERIMENT_PREFETCH
from chord_metadata_service.experiments.models import Experiment
from chord_metadata_service.experiments.serializers import ExperimentSerializer
from chord_metadata_service.experiments.summaries import dt_experiment_summary

from chord_metadata_service.logger import logger as katsu_logger

from chord_metadata_service.phenopackets.api_views import PHENOPACKET_SELECT_REL, PHENOPACKET_PREFETCH
from chord_metadata_service.phenopackets.models import Phenopacket
from chord_metadata_service.phenopackets.serializers import PhenopacketSerializer
from chord_metadata_service.phenopackets.summaries import dt_phenopacket_summary
from chord_metadata_service.restapi.utils import build_experiments_by_subject, get_biosamples_with_experiment_details

from .data_types import DATA_TYPE_EXPERIMENT, DATA_TYPE_PHENOPACKET, DATA_TYPES
from .models import Dataset, DatasetV2, Project

OUTPUT_FORMAT_VALUES_LIST = "values_list"
OUTPUT_FORMAT_BENTO_SEARCH_RESULT = "bento_search_result"


def bad_request_response(message: str) -> Response:
    return Response(errors.bad_request_error(message), status=status.HTTP_400_BAD_REQUEST)


def get_field_lookup(field: list[str]) -> str:
    """
    Given a field identifier as a schema-like path e.g. ['biosamples', '[item]', 'id'],
    returns a Django ORM field lookup string e.g. 'biosamples__id'
    """
    return "__".join(f for f in field if f != "[item]")


def get_values_list(queryset: QuerySet, options):
    field_lookup = get_field_lookup(options.get("field", []))

    # Filter out null values because these values will be used to make joins,
    # or fetch back some records.
    queryset = queryset.filter(**{f"{field_lookup}__isnull": False})

    if "add_field" in options:
        # Return a list of the dict, with the additional field and the field
        # used for the value. It will require further processing to get a list
        # of values.
        # this is used to group values by table ID for example.
        return queryset.values(options["add_field"], value=F(field_lookup))

    # Only a list of values
    return queryset.values_list(field_lookup, flat=True)


def data_type_results(query: sql.Composable, params, key: str, logger: BoundLogger):
    with connection.cursor() as cursor:
        logger.debug("data_type_results: executing SQL", sql_query=query.as_string(cursor.connection))
        cursor.execute(query.as_string(cursor.connection), params)
        return set(dict(zip([col[0] for col in cursor.description], row))[key] for row in cursor.fetchall())


async def experiment_query_results(
    scope: ValidatedDiscoveryScope, query: sql.Composable, params, logger: BoundLogger, options: dict | None = None
):
    # TODO: possibly a quite inefficient way of doing things...
    # TODO: Prefetch related biosample or no?
    queryset = Experiment.get_model_scoped_queryset(scope).filter(
        id__in=await sync_to_async(data_type_results)(query, params, "id", logger))

    output_format = options.get("output") if options else None
    if output_format == OUTPUT_FORMAT_VALUES_LIST:
        return get_values_list(queryset, options)

    return queryset.select_related(*EXPERIMENT_SELECT_REL).prefetch_related(*EXPERIMENT_PREFETCH)


async def phenopacket_query_results(
    scope: ValidatedDiscoveryScope, query: sql.Composable, params, logger: BoundLogger, options: dict | None = None
):
    queryset = Phenopacket.get_model_scoped_queryset(scope).filter(
        id__in=await sync_to_async(data_type_results)(query, params, "id", logger))

    output_format = options.get("output") if options else None
    if output_format == OUTPUT_FORMAT_VALUES_LIST:
        return get_values_list(queryset, options)

    if output_format == OUTPUT_FORMAT_BENTO_SEARCH_RESULT:
        fields = ["subject_id"]
        if "add_field" in options:
            fields.append(options["add_field"])

        results = queryset.values(
            *fields,
            alternate_ids=Coalesce(F("subject__alternate_ids"), []),
        ).annotate(
            num_experiments=Count("biosamples__experiments"),
            biosamples=Coalesce(ArrayAgg("biosamples__id", distinct=True, filter=Q(biosamples__id__isnull=False)), []),
        )

        # Get the biosamples with experiments data
        subject_ids = [result['subject_id'] async for result in results]
        biosamples_experiments_details = get_biosamples_with_experiment_details(subject_ids)

        # Group the experiments with biosamples by subject_id
        experiments_with_biosamples = await sync_to_async(build_experiments_by_subject)(biosamples_experiments_details)

        # Add the experiments_with_biosamples data to the results
        async for result in results:
            result["experiments_with_biosamples"] = experiments_with_biosamples[result["subject_id"]]

        return results
    else:
        return queryset.select_related(*PHENOPACKET_SELECT_REL).prefetch_related(*PHENOPACKET_PREFETCH)


QUERY_RESULTS_FN: dict[
    str,
    Callable[
        [ValidatedDiscoveryScope, sql.Composed, tuple[str | int | float, ...], BoundLogger, dict | None],
        Awaitable[QuerySet],
    ]
] = {
    DATA_TYPE_EXPERIMENT: experiment_query_results,
    DATA_TYPE_PHENOPACKET: phenopacket_query_results,
}

QUERY_RESULT_SERIALIZERS = {
    DATA_TYPE_EXPERIMENT: ExperimentSerializer,
    DATA_TYPE_PHENOPACKET: PhenopacketSerializer,
}


def _search_response(data_type, serializer_class, queryset: QuerySet, start):
    return Response(
        build_search_response({
            dataset_id: {
                "data_type": data_type,
                "matches": list(serializer_class(p).data for p in dataset_objects)
            } for dataset_id, dataset_objects in itertools.groupby(
                queryset if queryset is not None else [],
                key=lambda o: str(o.dataset_id)  # object here
            )
        }, start)
    )


async def _async_group_by_dataset_id(queryset: QuerySet) -> itertools.groupby:
    # Queryset is in an async context, so it becomes an async iterator. We need to convert it to a "normal"
    # iterable object for itertools.groupby.
    return itertools.groupby(
        [r async for r in queryset],
        key=lambda d: str(d["dataset_id"])
    )


async def search(request: DrfRequest, logger: BoundLogger):
    """
    Generic function that takes a request object containing the following parameters:
    - query: a Bento specific string representation of a query. e.g.
        ["#eq", ["#resolve", "experiment_results", "[item]", "file_format"], "VCF"]
    - data_type: one of "experiment", "phenopacket"
    This function returns matches grouped by their "owning" datasets.
    The request can be made using POST or GET methods.
    """

    scope = await get_request_discovery_scope(request)

    search_params, err = get_chord_search_parameters(request, logger)
    if err:
        authz_middleware.mark_authz_done(request)
        return bad_request_response(err)

    if (search_params["output"] == OUTPUT_FORMAT_VALUES_LIST
       or search_params["output"] == OUTPUT_FORMAT_BENTO_SEARCH_RESULT):
        search_params["add_field"] = "dataset_id"

    start = datetime.now()
    data_type = search_params["data_type"]
    compiled_query = search_params["compiled_query"]
    query_params = search_params["params"]

    res = await authz_middleware.async_evaluate_one(
        request, scope.as_authz_resource(data_type), P_QUERY_DATA, mark_authz_done=True
    )
    if not res:
        return Response(errors.forbidden_error("Forbidden"), status=status.HTTP_403_FORBIDDEN)

    serializer_class = QUERY_RESULT_SERIALIZERS[data_type]
    query_function = QUERY_RESULTS_FN[data_type]
    queryset = await query_function(scope, compiled_query, query_params, logger, search_params)

    if search_params["output"] == OUTPUT_FORMAT_VALUES_LIST:
        result = {
            dataset_id: {
                "data_type": data_type,
                "matches": [p["value"] for p in dataset_dicts]
            } for dataset_id, dataset_dicts in await _async_group_by_dataset_id(queryset)
        }
        return Response(build_search_response(result, start))

    elif search_params["output"] == OUTPUT_FORMAT_BENTO_SEARCH_RESULT:
        # The queryset for the bento_search_result output is based on the
        # usage of Django ORM `values()` to restrict its content to specific fields.
        # This result in a slight change of the queryset iterable where
        # items are dictionaries instead of objects.
        result = {
            dataset_id: {
                "data_type": data_type,
                "matches": [
                    {key: value for key, value in p.items() if key != "dataset_id"}
                    for p in dataset_dicts
                ]
            } for dataset_id, dataset_dicts in await _async_group_by_dataset_id(queryset)
        }
        return Response(build_search_response(result, start))

    return await sync_to_async(_search_response)(data_type, serializer_class, queryset, start)


@async_api_view(["GET", "POST"])
@permission_classes([BentoDeferToHandler])
async def chord_private_search(request: DrfRequest):
    """
    Free-form search using Bento specific syntax. Results are grouped by table
    of origin.
    request parameters (either via GET or POST) must contain:
    - query: a Bento specific object representing a query e.g.:
        ["#eq", ["#resolve", "experiment_results", "[item]", "file_format"], "VCF"]
        Note: for GET method, it must be encoded as a JSON string.
    - data_type: one of "phenopackets"/"experiments"
    - optional parameters:
        see chord_private_table_search

    - Returns:
        {
            time: query duration,
            results: {
                table_id#1: {
                    data_type: "phenopacket",
                    matches: [serialized results]
                }
            }.
        }
        The optional `output` parameter can be used to define a more restrictive
        response.
    """
    # Private search endpoints are protected by URL namespace, not by Django permissions.
    return await search(request, logger=katsu_logger)


def get_chord_search_parameters(request, logger: BoundLogger, data_type=None):
    """
    Extracts, either from the request body (POST) or the request query parameters,
    the information to make the search.
    - parameters:
        - request: DRF Request object. See `chord_private_table_search` for a
        detail of the possible values. Note that the "output" parameter is not
        implemented for this search.
        - data_type: optional argument. Can be "experiment"/"phenopacket"
            This value is provided for the chord searches that are restricted to
            a specific table (values inferred from the table properties)
    - returns:
        {
            - data_type: type of data table. This value is used to infer the
                proper search schema, serializers and search functions
            - query: a nested array, defining the query using Bento specific syntax
            - compiled_query: a psycopg2 SQL object defined from `query`
            - params: values used for interpolations in the compiled_query
            - output: optional parameter
            - field: optional parameter, set when output is "values_list"
        }
    """

    query_params = request.query_params if request.method == "GET" else (request.data or {})
    data_type = query_params.get("data_type") or data_type

    if not data_type:
        return None, "Missing data_type in request body"

    if data_type not in DATA_TYPES:
        return None, f"Missing or invalid data type (Specified: {data_type})"

    query = query_params.get("query")
    if query is None:
        return None, "Missing query in request body"

    if request.method == "GET":     # Query passed as a JSON in the URL: must be decoded.
        try:
            query = json.loads(query)
        except json.decoder.JSONDecodeError:
            return None, f"Invalid query JSON: {query}"

    try:
        compiled_query, params = postgres.search_query_to_psycopg2_sql(query, DATA_TYPES[data_type]["schema"])
    except (SyntaxError, TypeError, ValueError) as e:
        logger.exception("error encountered compiling query", exc_info=e, query=query)
        return None, f"Error compiling query (message: {str(e)})"

    field = query_params.get("field", None)
    if isinstance(field, str):
        try:
            field = json.loads(field)
        except json.decoder.JSONDecodeError:
            return None, f"Invalid field identifier as JSON string: {field}"

    return {
        "query": query,
        "compiled_query": compiled_query,
        "params": params,
        "data_type": data_type,
        "output": query_params.get("output", None),
        "field": field
    }, None


def _serialize_many(serializer_class, queryset):
    return serializer_class(queryset, many=True).data


async def chord_dataset_search(
    scope: ValidatedDiscoveryScope, search_params, start, logger: BoundLogger,
) -> tuple[bool | list | None, str | None]:
    """
    Performs a search based on a psycopg2 object and paramaters and restricted
    to a given table.
    """
    data_type = search_params["data_type"]
    serializer_class = QUERY_RESULT_SERIALIZERS[data_type]
    query_function = QUERY_RESULTS_FN[data_type]

    queryset = await query_function(
        scope,
        sql.SQL("{} AND dataset_id = {}").format(search_params["compiled_query"], sql.Placeholder()),
        search_params["params"] + (scope.dataset_id,),
        logger,
        search_params,
    )

    if search_params["output"] == OUTPUT_FORMAT_VALUES_LIST:
        return [v async for v in queryset], None
    if search_params["output"] == OUTPUT_FORMAT_BENTO_SEARCH_RESULT:
        return [v async for v in queryset], None

    await logger.adebug(
        "chord_dataset_search started fetching from queryset and serializing data",
        delta=datetime.now() - start,
    )
    serialized_data = await sync_to_async(_serialize_many)(serializer_class, queryset)
    await logger.adebug("chord_dataset_search finished query and serializing", delta=datetime.now() - start)

    return serialized_data, None


@async_api_view(["GET", "POST"])
@permission_classes([BentoDeferToHandler])
async def private_dataset_search(request: DrfRequest, dataset_id: str):
    try:
        dataset = await Dataset.objects.aget(identifier=dataset_id)
    except (Dataset.DoesNotExist, ValidationError) as e:
        authz_middleware.mark_authz_done(request)
        return Response(errors.not_found_error(str(e)), status=status.HTTP_404_NOT_FOUND)

    project = await Project.objects.aget(identifier=dataset.project_id)

    # don't use request scope - the project/dataset are validated by the aget calls above and fixed
    scope = ValidatedDiscoveryScope(project, dataset)

    # TODO: narrow based on queried data types
    if not await authz_middleware.async_evaluate_one(
        request, scope.as_authz_resource(), P_QUERY_DATA, mark_authz_done=True
    ):
        authz_middleware.mark_authz_done(request)
        return Response(errors.forbidden_error("Forbidden"), status=status.HTTP_403_FORBIDDEN)

    # perform search: --------------------------------------------------------------------------------------------------

    start = datetime.now()
    logger = katsu_logger.bind(project_id=str(project.identifier), dataset_id=dataset_id, start=start)

    search_params, err = get_chord_search_parameters(request, logger)
    if err:
        return bad_request_response(err)

    logger = logger.bind(search_params=search_params)
    await logger.adebug("executing chord_dataset_search")

    data, err = await chord_dataset_search(scope, search_params, start, logger)
    if err:
        return bad_request_response(err)

    return Response(build_search_response(data, start))


DATASET_DATA_TYPE_SUMMARY_FUNCTIONS = {
    DATA_TYPE_PHENOPACKET: dt_phenopacket_summary,
    DATA_TYPE_EXPERIMENT: dt_experiment_summary,
}


@async_api_view(["GET"])
@permission_classes([BentoAllowAny])
async def dataset_summary(request: DrfRequest, dataset_id: str):
    try:
        dataset = await Dataset.objects.aget(identifier=dataset_id)
    except (Dataset.DoesNotExist, ValidationError) as e:
        return Response(errors.not_found_error(str(e)), status=status.HTTP_404_NOT_FOUND)

    project = await Project.objects.aget(identifier=dataset.project_id)

    # don't use request scope - the project/dataset are validated by the aget calls above and fixed
    discovery_scope = ValidatedDiscoveryScope(project, dataset)
    dt_permissions = await get_data_type_query_permissions(
        request,
        data_types=list(DATASET_DATA_TYPE_SUMMARY_FUNCTIONS.keys()),
        resource=discovery_scope.as_authz_resource(),
    )

    summaries = await asyncio.gather(
        *map(lambda dt: DATASET_DATA_TYPE_SUMMARY_FUNCTIONS[dt](discovery_scope, dt_permissions[dt]),
             DATASET_DATA_TYPE_SUMMARY_FUNCTIONS.keys())
    )

    return Response({dt: s for dt, s in zip(DATASET_DATA_TYPE_SUMMARY_FUNCTIONS.keys(), summaries)})


@async_api_view(["GET"])
@permission_classes([BentoAllowAny])
async def dataset_v2_summary(request: DrfRequest, identifier: str):
    dataset = await DatasetV2.objects.filter(identifier=identifier).afirst()
    if dataset is None:
        return Response(errors.not_found_error("Dataset not found"), status=status.HTTP_404_NOT_FOUND)

    authz_middleware.mark_authz_done(request)
    counts = dataset.data.get("counts") or []
    return Response({"counts": counts})
