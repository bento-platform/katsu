import itertools
import json

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
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from typing import Callable

from chord_metadata_service.authz.middleware import authz_middleware

from chord_metadata_service.logger import logger
from chord_metadata_service.restapi.utils import queryset_stats_for_field

from chord_metadata_service.experiments.api_views import EXPERIMENT_SELECT_REL, EXPERIMENT_PREFETCH
from chord_metadata_service.experiments.models import Experiment
from chord_metadata_service.experiments.serializers import ExperimentSerializer


from chord_metadata_service.metadata.elastic import es

from chord_metadata_service.patients.models import Individual

from chord_metadata_service.phenopackets.api_views import PHENOPACKET_SELECT_REL, PHENOPACKET_PREFETCH
from chord_metadata_service.phenopackets.models import Phenopacket, Biosample
from chord_metadata_service.phenopackets.serializers import PhenopacketSerializer

from .data_types import DATA_TYPE_EXPERIMENT, DATA_TYPE_PHENOPACKET, DATA_TYPES
from .models import Dataset

from collections import defaultdict


OUTPUT_FORMAT_VALUES_LIST = "values_list"
OUTPUT_FORMAT_BENTO_SEARCH_RESULT = "bento_search_result"


def experiment_dataset_summary(dataset):
    # TODO; deduplicate with chord_metadata_service.restapi

    experiments = Experiment.objects.filter(dataset=dataset)

    return {
        "count": experiments.count(),
        "data_type_specific": {},  # TODO
    }


async def phenopacket_dataset_summary(dataset):
    # TODO; deduplicate with chord_metadata_service.restapi
    phenopacket_qs = Phenopacket.objects.filter(dataset=dataset)  # TODO

    # Sex related fields stats are precomputed here and post processed later
    # to include missing values inferred from the schema
    individuals_sex = await queryset_stats_for_field(phenopacket_qs, "subject__sex")
    individuals_k_sex = await queryset_stats_for_field(phenopacket_qs, "subject__karyotypic_sex")

    return {
        "count": phenopacket_qs.count(),
        "data_type_specific": {
            # TODO: deduplicate with biosamples summary from REST API
            "biosamples": {
                "count": phenopacket_qs.values("biosamples__id").count(),
                "is_control_sample": queryset_stats_for_field(phenopacket_qs, "biosamples__is_control_sample"),
                "taxonomy": queryset_stats_for_field(phenopacket_qs, "biosamples__taxonomy__label"),
            },
            # TODO: deduplicate with diseases summary from REST API
            "diseases": queryset_stats_for_field(phenopacket_qs, "diseases__term__label"),
            # TODO: deduplicate with individuals summary from REST API
            "individuals": {
                "count": phenopacket_qs.values("subject__id").count(),
                "sex": {k: individuals_sex.get(k, 0) for k in (s[0] for s in Individual.SEX)},
                "karyotypic_sex": {k: individuals_k_sex.get(k, 0) for k in (s[0] for s in Individual.KARYOTYPIC_SEX)},
                "taxonomy": queryset_stats_for_field(phenopacket_qs, "subject__taxonomy__label"),
                "date_of_birth": phenopacket_qs.values("subject__date_of_birth")
            },
            # TODO: deduplicate with phenotypic features summary from REST API
            "phenotypic_features": queryset_stats_for_field(phenopacket_qs, "phenotypic_features__pftype__label"),
        }
    }


def get_field_lookup(field: list[str]) -> str:
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
        logger.debug(f"Executing SQL:\n    {query.as_string(cursor.connection)}")
        cursor.execute(query.as_string(cursor.connection), params)
        return set(dict(zip([col[0] for col in cursor.description], row))[key] for row in cursor.fetchall())


def experiment_query_results(query, params, options=None):
    # TODO: possibly a quite inefficient way of doing things...
    # TODO: Prefetch related biosample or no?
    queryset = Experiment.objects.filter(id__in=data_type_results(query, params, "id"))

    output_format = options.get("output") if options else None
    if output_format == OUTPUT_FORMAT_VALUES_LIST:
        return get_values_list(queryset, options)

    return queryset.select_related(*EXPERIMENT_SELECT_REL) \
        .prefetch_related(*EXPERIMENT_PREFETCH)


def get_biosamples_with_experiment_details(subject_ids):
    """
    The function returns a queryset where each entry represents a biosample obtained from a subject, along with
    details of any associated experiment. If a biosample does not have an associated experiment, the experiment
    details are returned as None.
    """
    biosamples_exp_tissue_details = (
        Biosample.objects
        .filter(phenopacket__subject_id__in=subject_ids)
        .values(
            subject_id=F("phenopacket__subject_id"),
            biosample_id=F("id"),
            experiment_id=F("experiment__id"),
            experiment_type=F("experiment__experiment_type"),
            study_type=F("experiment__study_type"),
            tissue_id=F("sampled_tissue__id"),
            tissue_label=F("sampled_tissue__label")
        )
    )
    return biosamples_exp_tissue_details


def phenopacket_query_results(query, params, options=None):
    queryset = Phenopacket.objects.filter(id__in=data_type_results(query, params, "id"))

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


QUERY_RESULTS_FN: dict[str, Callable] = {
    DATA_TYPE_EXPERIMENT: experiment_query_results,
    DATA_TYPE_PHENOPACKET: phenopacket_query_results,
}

QUERY_RESULT_SERIALIZERS = {
    DATA_TYPE_EXPERIMENT: ExperimentSerializer,
    DATA_TYPE_PHENOPACKET: PhenopacketSerializer,
}


def search(request, internal_data=False):
    """
    Generic function that takes a request object containing the following parameters:
    - query: a Bento specific string representation of a query. e.g.
        ["#eq", ["#resolve", "experiment_results", "[item]", "file_format"], "VCF"]
    - data_type: one of "experiment", "phenopacket"
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
        search_params["add_field"] = "dataset_id"

    start = datetime.now()
    data_type = search_params["data_type"]
    compiled_query = search_params["compiled_query"]
    query_params = search_params["params"]

    if not internal_data:
        datasets = Dataset.objects.filter(identifier__in=data_type_results(
            query=compiled_query,
            params=query_params,
            key="dataset_id"
        ))
        return Response(build_search_response([{"id": d.identifier, "data_type": data_type} for d in datasets], start))

    serializer_class = QUERY_RESULT_SERIALIZERS[data_type]
    query_function = QUERY_RESULTS_FN[data_type]
    queryset = query_function(compiled_query, query_params, search_params)

    if search_params["output"] == OUTPUT_FORMAT_VALUES_LIST:
        result = {
            dataset_id: {
                "data_type": data_type,
                "matches": [p["value"] for p in dataset_dicts]
            } for dataset_id, dataset_dicts in itertools.groupby(
                queryset,
                key=lambda d: str(d["dataset_id"])    # dict here
            )
        }
        return Response(build_search_response(result, start))

    if search_params["output"] == OUTPUT_FORMAT_BENTO_SEARCH_RESULT:
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
            } for dataset_id, dataset_dicts in itertools.groupby(
                queryset,
                key=lambda d: str(d["dataset_id"])    # dict here
            )
        }
        return Response(build_search_response(result, start))

    return Response(build_search_response({
        dataset_id: {
            "data_type": data_type,
            "matches": list(serializer_class(p).data for p in dataset_objects)
        } for dataset_id, dataset_objects in itertools.groupby(
            queryset if queryset is not None else [],
            key=lambda o: str(o.dataset_id)  # object here
        )
    }, start))


# Cache page for the requested url
@cache_page(60 * 60 * 2)
@api_view(["GET", "POST"])
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
def chord_private_search(request):
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
        datasets = Dataset.objects.filter(identifier__in=frozenset(p.dataset_id for p in phenopackets))
        return Response(build_search_response([{"id": d.identifier, "data_type": DATA_TYPE_PHENOPACKET}
                                               for d in datasets], start))

    ext_result = {
        dataset_id: {
            "data_type": DATA_TYPE_PHENOPACKET,
            "matches": list(PhenopacketSerializer(p).data for p in dataset_phenopackets)
        } for dataset_id, dataset_phenopackets in itertools.groupby(phenopackets, key=lambda p: str(p.dataset_id))
    }
    return Response(build_search_response(ext_result, start))


@api_view(["GET", "POST"])
def fhir_public_search(request):
    return fhir_search(request)


# Mounted on /private/, so will get protected anyway
# TODO: Ugly and misleading permissions
@api_view(["GET", "POST"])
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


def chord_dataset_search(
    search_params,
    dataset_id,
    start,
    internal=False,
) -> tuple[None | bool | list, str | None]:
    """
    Performs a search based on a psycopg2 object and paramaters and restricted
    to a given table.
    """
    data_type = search_params["data_type"]
    serializer_class = QUERY_RESULT_SERIALIZERS[data_type]
    query_function = QUERY_RESULTS_FN[data_type]

    queryset = query_function(
        query=sql.SQL("{} AND dataset_id = {}").format(search_params["compiled_query"], sql.Placeholder()),
        params=search_params["params"] + (dataset_id,),
        options=search_params
    )
    if not internal:  # TODO: boolean, check if count above configured threshold instead!
        return queryset.exists(), None    # True if at least one match

    if search_params["output"] == OUTPUT_FORMAT_VALUES_LIST:
        return list(queryset), None
    if search_params["output"] == OUTPUT_FORMAT_BENTO_SEARCH_RESULT:
        return list(queryset), None

    logger.debug(f"Started fetching from queryset and serializing data at {datetime.now() - start}")
    serialized_data = serializer_class(queryset, many=True).data
    logger.debug(f"Finished running query and serializing in {datetime.now() - start}")

    return serialized_data, None


def chord_dataset_representation(dataset: Dataset) -> dict:
    return {
        "id": dataset.identifier,
        "title": dataset.title,
        "metadata": {
            "project_id": dataset.project_id,
            "created": dataset.created.isoformat(),
            "updated": dataset.updated.isoformat(),
        },
    }


def dataset_search(request: Request, dataset_id: str, internal=False):
    # TODO: permissions on request

    start = datetime.now()
    search_params, err = get_chord_search_parameters(request)
    if err:
        authz_middleware.mark_authz_done(request)
        return Response(errors.bad_request_error(err), status=status.HTTP_400_BAD_REQUEST)

    # TODO: permissions checking + incorporating internal...

    data, err = chord_dataset_search(search_params, dataset_id, start, internal)

    if err:
        return Response(errors.bad_request_error(err), status=status.HTTP_400_BAD_REQUEST)
    return Response(build_search_response(data, start) if internal else data)


@api_view(["GET", "POST"])
def public_dataset_search(request: Request, dataset_id: str):
    return dataset_search(request, dataset_id)


@api_view(["GET", "POST"])
def private_dataset_search(request: Request, dataset_id: str):
    return dataset_search(request, dataset_id, internal=True)


@api_view(["GET"])
def dataset_summary(request: Request, dataset_id: str):
    # TODO: PERMISSIONS
    dataset = Dataset.objects.get(identifier=dataset_id)
    return Response({
        DATA_TYPE_PHENOPACKET: phenopacket_dataset_summary(dataset=dataset),
        DATA_TYPE_EXPERIMENT: experiment_dataset_summary(dataset=dataset),
    })
