import itertools
import json
import logging
import uuid

from bento_lib.responses import errors
from bento_lib.search import build_search_response, postgres

from datetime import datetime
from django.db import connection
from django.db.models import Count, F, Q
from django.db.models.functions import Coalesce
from django.contrib.postgres.aggregates import ArrayAgg
from django.conf import settings
from django.views.decorators.cache import cache_page
from psycopg2 import sql
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from typing import Any, Callable, Dict, Optional, Tuple, Union

from chord_metadata_service.cleanup import run_all_cleanup
from chord_metadata_service.logger import logger
from chord_metadata_service.restapi.utils import get_field_bins, queryset_stats_for_field

from chord_metadata_service.experiments.api_views import EXPERIMENT_SELECT_REL, EXPERIMENT_PREFETCH
from chord_metadata_service.experiments.models import Experiment
from chord_metadata_service.experiments.serializers import ExperimentSerializer

from chord_metadata_service.mcode.models import MCodePacket
from chord_metadata_service.mcode.serializers import MCodePacketSerializer

from chord_metadata_service.metadata.elastic import es
from chord_metadata_service.metadata.settings import CHORD_SERVICE_ARTIFACT, CHORD_SERVICE_ID

from chord_metadata_service.patients.models import Individual

from chord_metadata_service.phenopackets.api_views import PHENOPACKET_SELECT_REL, PHENOPACKET_PREFETCH
from chord_metadata_service.phenopackets.models import Phenopacket, Biosample
from chord_metadata_service.phenopackets.serializers import PhenopacketSerializer

from .data_types import DATA_TYPE_EXPERIMENT, DATA_TYPE_MCODEPACKET, DATA_TYPE_PHENOPACKET, DATA_TYPES
from .models import Dataset, TableOwnership, Table
from .permissions import ReadOnly, OverrideOrSuperUserOnly

from collections import defaultdict


OUTPUT_FORMAT_VALUES_LIST = "values_list"
OUTPUT_FORMAT_BENTO_SEARCH_RESULT = "bento_search_result"


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_list(_request):
    return Response(sorted(
        ({"id": k, "label": dt["label"], "schema": dt["schema"]} for k, dt in DATA_TYPES.items()),
        key=lambda dt: dt["id"]
    ))


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_detail(_request, data_type: str):
    if data_type not in DATA_TYPES:
        return Response(errors.not_found_error(f"Date type {data_type} not found"), status=404)

    return Response({"id": data_type, **DATA_TYPES[data_type]})


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_schema(_request, data_type: str):
    if data_type not in DATA_TYPES:
        return Response(errors.not_found_error(f"Date type {data_type} not found"), status=404)

    return Response(DATA_TYPES[data_type]["schema"])


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_metadata_schema(_request, data_type: str):
    if data_type not in DATA_TYPES:
        return Response(errors.not_found_error(f"Date type {data_type} not found"), status=404)

    return Response(DATA_TYPES[DATA_TYPE_PHENOPACKET]["metadata_schema"])


def chord_table_representation(table: Table) -> dict:
    return {
        "id": table.identifier,
        "name": table.name,
        "metadata": {
            "dataset_id": table.ownership_record.dataset_id,
            "created": table.created.isoformat(),
            "updated": table.updated.isoformat()
        },
        "data_type": table.data_type,
        "schema": DATA_TYPES[table.data_type]["schema"],
    }


@api_view(["GET", "POST"])
@permission_classes([OverrideOrSuperUserOnly | ReadOnly])
def table_list(request):
    if request.method == "POST":
        request_data = json.loads(request.body)  # TODO: Handle JSON errors here

        name = request_data.get("name", "").strip()
        data_type = request_data.get("data_type", "")
        dataset = request_data.get("dataset")

        if name == "":
            return Response(errors.bad_request_error("Missing or blank name field"), status=400)

        if data_type not in DATA_TYPES:
            return Response(errors.bad_request_error(f"Invalid data type for table: {data_type}"), status=400)

        table_id = str(uuid.uuid4())

        table_ownership = TableOwnership.objects.create(
            table_id=table_id,
            service_id=CHORD_SERVICE_ID,
            service_artifact=CHORD_SERVICE_ARTIFACT,
            dataset=Dataset.objects.get(identifier=dataset),
        )

        table = Table.objects.create(
            ownership_record=table_ownership,
            name=name,
            data_type=data_type,
        )

        return Response(chord_table_representation(table))

    # GET

    data_types = request.query_params.getlist("data-type")

    if len(data_types) == 0 or next((dt for dt in data_types if dt not in DATA_TYPES), None) is not None:
        return Response(errors.bad_request_error(f"Missing or invalid data type(s) (Specified: {data_types})"),
                        status=400)

    return Response([chord_table_representation(t) for t in Table.objects.filter(data_type__in=data_types)])


# TODO: Remove pragma: no cover when POST implemented
@api_view(["GET", "DELETE"])
@permission_classes([OverrideOrSuperUserOnly | ReadOnly])
def table_detail(request, table_id):  # pragma: no cover
    # TODO: Implement GET, POST
    # TODO: Permissions: Check if user has control / more direct access over this table and/or dataset?
    #  Or just always use owner...
    try:
        table = Table.objects.get(ownership_record_id=table_id)
        table_ownership = TableOwnership.objects.get(table_id=table_id)
    except Table.DoesNotExist:
        return Response(errors.not_found_error(f"Table with ID {table_id} not found"), status=404)
    except TableOwnership.DoesNotExist:
        return Response(
            errors.not_found_error(f"Table ownership record for table with ID {table_id} not found"), status=404)

    if request.method == "DELETE":
        # First, delete the table record itself - use the cascade from the ownership record
        table_ownership.delete()  # also deletes table

        # Then, run cleanup
        logger.info(f"Running cleanup after deleting table {table_id} via /tables Bento data service endpoint")
        n_removed = run_all_cleanup()
        logger.info(f"Cleanup: removed {n_removed} objects in total")

        return Response(status=204)

    # GET
    return Response(chord_table_representation(table))


def experiment_table_summary(table):
    experiments = Experiment.objects.filter(table=table)  # TODO

    return Response({
        "count": experiments.count(),
        "data_type_specific": {},  # TODO
    })


def mcodepacket_table_summary(table):
    mcodepackets = MCodePacket.objects.filter(table=table)  # TODO

    return Response({
        "count": mcodepackets.count(),
        "data_type_specific": {},  # TODO
    })


def phenopacket_table_summary(table):
    phenopacket_qs = Phenopacket.objects.filter(table=table)  # TODO

    # Sex related fields stats are precomputed here and post processed later
    # to include missing values inferred from the schema
    individuals_sex = queryset_stats_for_field(phenopacket_qs, "subject__sex")
    individuals_k_sex = queryset_stats_for_field(phenopacket_qs, "subject__karyotypic_sex")

    return Response({
        "count": phenopacket_qs.count(),
        "data_type_specific": {
            "biosamples": {
                "count": phenopacket_qs.values("biosamples__id").count(),
                "is_control_sample": queryset_stats_for_field(phenopacket_qs, "biosamples__is_control_sample"),
                "taxonomy": queryset_stats_for_field(phenopacket_qs, "biosamples__taxonomy__label"),
            },
            "diseases": queryset_stats_for_field(phenopacket_qs, "diseases__term__label"),
            "individuals": {
                "count": phenopacket_qs.values("subject__id").count(),
                "sex": {k: individuals_sex.get(k, 0) for k in (s[0] for s in Individual.SEX)},
                "karyotypic_sex": {k: individuals_k_sex.get(k, 0) for k in (s[0] for s in Individual.KARYOTYPIC_SEX)},
                "taxonomy": queryset_stats_for_field(phenopacket_qs, "subject__taxonomy__label"),
                "age": get_field_bins(phenopacket_qs, "subject__age_numeric", 10),
            },
            "phenotypic_features": queryset_stats_for_field(phenopacket_qs, "phenotypic_features__pftype__label"),
        }
    })


SUMMARY_HANDLERS: Dict[str, Callable[[Any], Response]] = {
    DATA_TYPE_EXPERIMENT: experiment_table_summary,
    DATA_TYPE_MCODEPACKET: mcodepacket_table_summary,
    DATA_TYPE_PHENOPACKET: phenopacket_table_summary,
}


# Cache page for the requested url
@cache_page(60 * 60 * 2)
@api_view(["GET"])
@permission_classes([OverrideOrSuperUserOnly])
def chord_table_summary(_request, table_id):
    try:
        table = Table.objects.get(ownership_record_id=table_id)
        return SUMMARY_HANDLERS[table.data_type](table)
    except Table.DoesNotExist:
        return Response(errors.not_found_error(f"Table with ID {table_id} not found"), status=404)


# TODO: CHORD-standardized logging
def debug_log(message):  # pragma: no cover
    logging.debug(f"[CHORD Metadata {datetime.now()}] [DEBUG] {message}")


def get_field_lookup(field):
    """
    Given a field identifier as a schema-like path e.g. ['biosamples', '[item]', 'id'],
    returns a Django ORM field lookup string e.g. 'biosamples__id'
    """
    return "__".join(f for f in field if f != "[item]")


def get_values_list(queryset, options):
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


def data_type_results(query, params, key="id"):
    with connection.cursor() as cursor:
        debug_log(f"Executing SQL:\n    {query.as_string(cursor.connection)}")
        cursor.execute(query.as_string(cursor.connection), params)
        return set(dict(zip([col[0] for col in cursor.description], row))[key] for row in cursor.fetchall())


def experiment_query_results(query, params, options=None):
    # TODO: possibly a quite inefficient way of doing things...
    # TODO: Prefetch related biosample or no?
    queryset = Experiment.objects\
        .filter(id__in=data_type_results(query, params, "id"))

    output_format = options.get("output") if options else None
    if output_format == OUTPUT_FORMAT_VALUES_LIST:
        return get_values_list(queryset, options)

    return queryset.select_related(*EXPERIMENT_SELECT_REL) \
        .prefetch_related(*EXPERIMENT_PREFETCH)


def mcodepacket_query_results(query, params, options=None):
    # TODO: possibly a quite inefficient way of doing things...
    # TODO: select_related / prefetch_related for instant performance boost!
    queryset = MCodePacket.objects.filter(
        id__in=data_type_results(query, params, "id")
    )

    output_format = options.get("output") if options else None
    if output_format == OUTPUT_FORMAT_VALUES_LIST:
        return get_values_list(queryset, options)

    return queryset


def get_biosamples_with_experiment_details(subject_ids):
    """
    The function returns a queryset where each entry represents a biosample obtained from a subject, along with
    details of any associated experiment. If a biosample does not have an associated experiment, the experiment
    details are returned as None.
    """
    biosamples_exp_tissue_details = Biosample.objects.filter(phenopacket__subject_id__in=subject_ids)\
        .values(
            subject_id=F("phenopacket__subject_id"),
            biosample_id=F("id"),
            experiment_id=F("experiment__id"),
            experiment_type=F("experiment__experiment_type"),
            study_type=F("experiment__study_type"),
            tissue_id=F("sampled_tissue__id"),
            tissue_label=F("sampled_tissue__label")
        )
    return biosamples_exp_tissue_details


def phenopacket_query_results(query, params, options=None):
    queryset = Phenopacket.objects \
        .filter(id__in=data_type_results(query, params, "id"))

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
            num_experiments=Count("biosamples__experiment"),
            biosamples=Coalesce(ArrayAgg("biosamples__id", distinct=True, filter=Q(biosamples__id__isnull=False)), []),
        )

        # Get the biosamples with experiments data
        phenopacket_ids = [result['subject_id'] for result in results]
        biosamples_experiments_details = get_biosamples_with_experiment_details(phenopacket_ids)

        # Group the experiments with biosamples by subject_id
        experiments_with_biosamples = defaultdict(list)
        for b in biosamples_experiments_details:
            experiments_with_biosamples[b["subject_id"]].append({
                "biosample_id": b["biosample_id"],
                "sampled_tissue": {
                    "id": b["tissue_id"],
                    "label": b["tissue_label"]
                },
                "experiment": {
                    "experiment_id": b["experiment_id"],
                    "experiment_type": b["experiment_type"],
                    "study_type": b["study_type"]
                }
            })

        # Add the experiments_with_biosamples data to the results
        for result in results:
            result["experiments_with_biosamples"] = experiments_with_biosamples[result['subject_id']]

        return results
    else:
        return queryset.select_related(*PHENOPACKET_SELECT_REL) \
            .prefetch_related(*PHENOPACKET_PREFETCH)


QUERY_RESULTS_FN: Dict[str, Callable] = {
    DATA_TYPE_EXPERIMENT: experiment_query_results,
    DATA_TYPE_MCODEPACKET: mcodepacket_query_results,
    DATA_TYPE_PHENOPACKET: phenopacket_query_results,
}

QUERY_RESULT_SERIALIZERS = {
    DATA_TYPE_EXPERIMENT: ExperimentSerializer,
    DATA_TYPE_MCODEPACKET: MCodePacketSerializer,
    DATA_TYPE_PHENOPACKET: PhenopacketSerializer,
}


def search(request, internal_data=False):
    """
    Generic function that takes a request object containing the following parameters:
    - query: a Bento specific string representation of a query. e.g.
        ["#eq", ["#resolve", "experiment_results", "[item]", "file_format"], "VCF"]
    - data_type: one of "experiment", "mcode", "phenopacket"
    If internal_data is False, this function returns the tables id where matches
    are found.
    If internal_data is True, this function returns matches grouped by their
    "owning" tables.
    The request can be made using POST or GET methods.
    """
    search_params, err = get_chord_search_parameters(request)
    if err:
        return Response(errors.bad_request_error(err), status=400)

    if (search_params["output"] == OUTPUT_FORMAT_VALUES_LIST
       or search_params["output"] == OUTPUT_FORMAT_BENTO_SEARCH_RESULT):
        search_params["add_field"] = "table_id"

    start = datetime.now()
    data_type = search_params["data_type"]
    compiled_query = search_params["compiled_query"]
    query_params = search_params["params"]

    if not internal_data:
        tables = Table.objects.filter(ownership_record_id__in=data_type_results(
            query=compiled_query,
            params=query_params,
            key="table_id"
        ))  # TODO: Maybe can avoid hitting DB here
        return Response(build_search_response([{"id": t.identifier, "data_type": data_type} for t in tables], start))

    serializer_class = QUERY_RESULT_SERIALIZERS[data_type]
    query_function = QUERY_RESULTS_FN[data_type]
    queryset = query_function(compiled_query, query_params, search_params)

    if search_params["output"] == OUTPUT_FORMAT_VALUES_LIST:
        return Response(build_search_response({
            table_id: {
                "data_type": data_type,
                "matches": [p["value"] for p in table_dicts]
            } for table_id, table_dicts in itertools.groupby(
                queryset,
                key=lambda d: str(d["table_id"])    # dict here
            )
        }, start))

    if search_params["output"] == OUTPUT_FORMAT_BENTO_SEARCH_RESULT:
        # The queryset for the bento_search_result output is based on the
        # usage of Django ORM `values()` to restrict its content to specific fields.
        # This result in a slight change of the queryset iterable where
        # items are dictionaries instead of objects.
        return Response(build_search_response({
            table_id: {
                "data_type": data_type,
                "matches": [
                    {key: value for key, value in p.items() if key != "table_id"}
                    for p in table_dicts
                ]
            } for table_id, table_dicts in itertools.groupby(
                queryset,
                key=lambda d: str(d["table_id"])    # dict here
            )
        }, start))

    return Response(build_search_response({
        table_id: {
            "data_type": data_type,
            "matches": list(serializer_class(p).data for p in table_objects)
        } for table_id, table_objects in itertools.groupby(
            queryset if queryset is not None else [],
            key=lambda o: str(o.table_id)  # object here
        )
    }, start))


# Cache page for the requested url
@cache_page(60 * 60 * 2)
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def chord_search(request):
    """
    Free-form search using Bento specific syntax. Returns the list of tables
    having matches (does not leak values from records)
    - request parameters: see chord_private_search
    """
    return search(request, internal_data=False)


# Mounted on /private/, so will get protected anyway; this allows for access from federation service
# TODO: Ugly and misleading permissions
# Cache page for the requested url
@cache_page(60 * 60 * 2)
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def chord_private_search(request):
    """
    Free-form search using Bento specific syntax. Results are grouped by table
    of origin.
    request parameters (either via GET or POST) must contain:
    - query: a Bento specific object representing a query e.g.:
        ["#eq", ["#resolve", "experiment_results", "[item]", "file_format"], "VCF"]
        Note: for GET method, it must be encoded as a JSON string.
    - data_type: one of "phenopackets"/"experiments"/"mcodepackets"
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
    return search(request, internal_data=True)


def phenopacket_filter_results(subject_ids, htsfile_ids, disease_ids, biosample_ids,
                               phenotypicfeature_ids, phenopacket_ids):
    query = Phenopacket.objects.get_queryset()

    if subject_ids:
        query = query.filter(subject__id__in=subject_ids)

    if htsfile_ids:
        query = query.filter(htsfiles__id__in=htsfile_ids)

    if disease_ids:
        query = query.filter(diseases__id__in=disease_ids)

    if biosample_ids:
        query = query.filter(biosamples__id__in=biosample_ids)

    if phenotypicfeature_ids:
        query = query.filter(phenotypic_features__id__in=phenotypicfeature_ids)

    if phenopacket_ids:
        query = query.filter(id__in=phenopacket_ids)

    res = query.prefetch_related(*PHENOPACKET_PREFETCH)

    return res


def fhir_search(request, internal_data=False):
    # TODO: not all that sure about the query format we'll want
    # keep it simple for now

    if request.method == "POST":
        query = (request.data or {}).get("query")
    else:
        query = request.query_params.get("query")

    if query is None:
        return Response(errors.bad_request_error("Missing query in request body"), status=400)

    start = datetime.now()

    if not es:
        return Response(build_search_response([], start))

    res = es.search(index=settings.FHIR_INDEX_NAME, body=query)

    def hits_for(resource_type: str):
        return frozenset(hit["_id"].split("|")[1] for hit in res["hits"]["hits"]
                         if hit['_source']['resourceType'] == resource_type)

    subject_ids = hits_for('Patient')
    htsfile_ids = hits_for('DocumentReference')
    disease_ids = hits_for('Condition')
    biosample_ids = hits_for('Specimen')
    phenotypicfeature_ids = hits_for('Observation')
    phenopacket_ids = hits_for('Composition')

    if all((not subject_ids, not htsfile_ids, not disease_ids, not biosample_ids, not phenotypicfeature_ids,
            not phenopacket_ids)):
        return Response(build_search_response([], start))

    phenopackets = phenopacket_filter_results(
        subject_ids,
        htsfile_ids,
        disease_ids,
        biosample_ids,
        phenotypicfeature_ids,
        phenopacket_ids
    )

    if not internal_data:
        # TODO: Maybe can avoid hitting DB here
        datasets = Table.objects.filter(ownership_record_id__in=frozenset(p.table_id for p in phenopackets))
        return Response(build_search_response([{"id": d.identifier, "data_type": DATA_TYPE_PHENOPACKET}
                                               for d in datasets], start))
    return Response(build_search_response({
        table_id: {
            "data_type": DATA_TYPE_PHENOPACKET,
            "matches": list(PhenopacketSerializer(p).data for p in table_phenopackets)
        } for table_id, table_phenopackets in itertools.groupby(phenopackets, key=lambda p: str(p.table_id))
    }, start))


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def fhir_public_search(request):
    return fhir_search(request)


# Mounted on /private/, so will get protected anyway
# TODO: Ugly and misleading permissions
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def fhir_private_search(request):
    return fhir_search(request, internal_data=True)


def get_chord_search_parameters(request, data_type=None):
    """
    Extracts, either from the request body (POST) or the request query parameters,
    the information to make the search.
    - parameters:
        - request: DRF Request object. See `chord_private_table_search` for a
        detail of the possible values. Note that the "output" parameter is not
        implemented for this search.
        - data_type: optional argument. Can be "experiment"/"phenopacket"/"mcodepacket"
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
        # print(request.query_params)
        try:
            query = json.loads(query)
        except json.decoder.JSONDecodeError:
            return None, f"Invalid query JSON: {query}"

    try:
        compiled_query, params = postgres.search_query_to_psycopg2_sql(query, DATA_TYPES[data_type]["schema"])
    except (SyntaxError, TypeError, ValueError) as e:
        logger.exception(f"[CHORD Metadata] Error encountered compiling query {query}:\n    {str(e)}")
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


def chord_table_search(search_params, table_id, start, internal=False) -> Tuple[Union[None, bool, list], Optional[str]]:
    """
    Performs a search based on a psycopg2 object and paramaters and restricted
    to a given table.
    """
    data_type = search_params["data_type"]
    serializer_class = QUERY_RESULT_SERIALIZERS[data_type]
    query_function = QUERY_RESULTS_FN[data_type]

    queryset = query_function(
        query=sql.SQL("{} AND table_id = {}").format(search_params["compiled_query"], sql.Placeholder()),
        params=search_params["params"] + (table_id,),
        options=search_params
    )
    if not internal:
        return queryset.exists(), None    # True if at least one match

    if search_params["output"] == OUTPUT_FORMAT_VALUES_LIST:
        return list(queryset), None
    if search_params["output"] == OUTPUT_FORMAT_BENTO_SEARCH_RESULT:
        return list(queryset), None

    debug_log(f"Started fetching from queryset and serializing data at {datetime.now() - start}")
    serialized_data = serializer_class(queryset, many=True).data
    debug_log(f"Finished running query and serializing in {datetime.now() - start}")

    return serialized_data, None


def chord_table_search_response(request, table_id, internal=False):
    """
    Executes a free-form query using the Bento specific syntax, restricted to
    a given table and generates DRF Responses.
    - Parameters:
        - request: DRF Request object, see `chord_table_private_search` for
            the expected values
        - table_id: table_id to restrict the results to. Extracted from the
            URL (hence, unverified)
        - internal: if set to True, the response contains values from records.
            if set to False, the response is a Boolean (no private data can
            be leaked).
    """
    start = datetime.now()
    debug_log(f"Started {'private' if internal else 'public'} table search")

    table = Table.objects.get(ownership_record_id=table_id)
    data_type = table.data_type

    search_params, err = get_chord_search_parameters(request, data_type)
    if err:
        return Response(errors.bad_request_error(err), status=400)

    debug_log(f"Finished compiling query in {datetime.now() - start}")
    data, err = chord_table_search(search_params, table_id, start, internal)

    if err:
        return Response(errors.bad_request_error(err), status=400)

    if internal:
        return Response(build_search_response(data, start))

    return Response(data)


# Cache page for the requested url
@cache_page(60 * 60 * 2)
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def chord_public_table_search(request, table_id):
    """
    Returns a Boolean value to indicate that a match with the query exists in
    the given table.
    See `chord_private_table_search for a detail of the request parameters

    - Returns
      {
        time: query duration,
        results: boolean
      }
    """
    # Search data types in specific tables without leaking internal data
    return chord_table_search_response(request, table_id, internal=False)


# Mounted on /private/, so will get protected anyway; this allows for access from federation service
# TODO: Ugly and misleading permissions
# Cache page for the requested url
@cache_page(60 * 60 * 2)
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def chord_private_table_search(request, table_id):
    """
    Free-form search using Bento specific syntax in a given table.
    request parameters (either via GET or POST) must contain:
    - query: a Bento specific object representing a query e.g.:
        ["#eq", ["#resolve", "experiment_results", "[item]", "file_format"], "VCF"]
        Note: for GET method, it must be encoded as a JSON string.
    - optional parameters:
        - output: predefined output types in {"values_list", "bento_search_result"}
          If not set, the objects in the results
          set will be serialized using the default serializer for this data-type
          (for example: phenopackets serializer)
        - field: when `output="values_list"`, defines which field should be in
           used to get the list of values.

    - Returns:
        {
            time: query duration,
            results: [] see infra.
        }
        Serialized objects of the result set. If the table `data-type` is `experiment`
        the Experiments serializer will be used.
        The optional `output` parameter can be used to define a more restrictive
        response.
    """
    # Search data types in specific tables
    # Private search endpoints are protected by URL namespace, not by Django permissions.
    return chord_table_search_response(request, table_id, internal=True)
