import itertools
import json
import logging
import uuid

from bento_lib.responses import errors
from bento_lib.search import build_search_response, postgres
from collections import Counter
from datetime import datetime
from django.db import connection
from django.conf import settings
from django.views.decorators.cache import cache_page
from psycopg2 import sql
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from typing import Any, Callable, Dict, Optional, Tuple, Union

from chord_metadata_service.experiments.api_views import EXPERIMENT_SELECT_REL, EXPERIMENT_PREFETCH
from chord_metadata_service.experiments.models import Experiment
from chord_metadata_service.experiments.serializers import ExperimentSerializer

from chord_metadata_service.metadata.elastic import es
from chord_metadata_service.metadata.settings import DEBUG, CHORD_SERVICE_ARTIFACT, CHORD_SERVICE_ID

from chord_metadata_service.patients.models import Individual

from chord_metadata_service.phenopackets.api_views import PHENOPACKET_SELECT_REL, PHENOPACKET_PREFETCH
from chord_metadata_service.phenopackets.models import Phenopacket
from chord_metadata_service.phenopackets.serializers import PhenopacketSerializer

from .data_types import DATA_TYPE_EXPERIMENT, DATA_TYPE_PHENOPACKET, DATA_TYPES
from .models import Dataset, TableOwnership, Table
from .permissions import ReadOnly, OverrideOrSuperUserOnly

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_list(_request):
    return Response(sorted(
        ({"id": k, "schema": dt["schema"]} for k, dt in DATA_TYPES.items()),
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
    except Table.DoesNotExist:
        return Response(errors.not_found_error(f"Table with ID {table_id} not found"), status=404)

    if request.method == "DELETE":
        table.delete()
        return Response(status=204)

    # GET
    return Response(chord_table_representation(table))


def experiment_table_summary(table):
    experiments = Experiment.objects.filter(table=table)  # TODO

    return Response({
        "count": experiments.count(),
        "data_type_specific": {},  # TODO
    })


def phenopacket_table_summary(table):
    phenopackets = Phenopacket.objects.filter(table=table)  # TODO

    diseases_counter = Counter()
    phenotypic_features_counter = Counter()

    biosamples_set = set()
    individuals_set = set()

    biosamples_cs = Counter()
    biosamples_taxonomy = Counter()

    individuals_sex = Counter()
    individuals_k_sex = Counter()
    individuals_taxonomy = Counter()

    def count_individual(ind):
        individuals_set.add(ind.id)
        individuals_sex.update((ind.sex,))
        individuals_k_sex.update((ind.karyotypic_sex,))
        if ind.taxonomy is not None:
            individuals_taxonomy.update((ind.taxonomy["id"],))

    for p in phenopackets.prefetch_related("biosamples"):
        for b in p.biosamples.all():
            biosamples_set.add(b.id)
            biosamples_cs.update((b.is_control_sample,))

            if b.taxonomy is not None:
                biosamples_taxonomy.update((b.taxonomy["id"],))

            if b.individual is not None:
                count_individual(b.individual)

            for pf in b.phenotypic_features.all():
                phenotypic_features_counter.update((pf.pftype["id"],))

        for d in p.diseases.all():
            diseases_counter.update((d.term["id"],))

        for pf in p.phenotypic_features.all():
            phenotypic_features_counter.update((pf.pftype["id"],))

        # Currently, phenopacket subject is required so we can assume it's not None
        count_individual(p.subject)

    return Response({
        "count": phenopackets.count(),
        "data_type_specific": {
            "biosamples": {
                "count": len(biosamples_set),
                "is_control_sample": dict(biosamples_cs),
                "taxonomy": dict(biosamples_taxonomy),
            },
            "diseases": dict(diseases_counter),
            "individuals": {
                "count": len(individuals_set),
                "sex": {k: individuals_sex[k] for k in (s[0] for s in Individual.SEX)},
                "karyotypic_sex": {k: individuals_k_sex[k] for k in (s[0] for s in Individual.KARYOTYPIC_SEX)},
                "taxonomy": dict(individuals_taxonomy),
                # TODO: age histogram
            },
            "phenotypic_features": dict(phenotypic_features_counter),
        }
    })


SUMMARY_HANDLERS: Dict[str, Callable[[Any], Response]] = {
    DATA_TYPE_EXPERIMENT: experiment_table_summary,
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
    logging.debug(f"[CHORD Metadata {datetime.now()}] [DEBUG] {message}", flush=True)


def data_type_results(query, params, key="id"):
    with connection.cursor() as cursor:
        debug_log(f"Executing SQL:\n    {query.as_string(cursor.connection)}")
        cursor.execute(query.as_string(cursor.connection), params)
        return set(dict(zip([col[0] for col in cursor.description], row))[key] for row in cursor.fetchall())


def experiment_query_results(query, params):
    # TODO: possibly a quite inefficient way of doing things...
    # TODO: Prefetch related biosample or no?
    return Experiment.objects \
        .filter(id__in=data_type_results(query, params, "id")) \
        .select_related(*EXPERIMENT_SELECT_REL) \
        .prefetch_related(*EXPERIMENT_PREFETCH)


def phenopacket_query_results(query, params):
    # TODO: possibly a quite inefficient way of doing things...
    # To expand further on this query : the select_related call
    # will join on these tables we'd call anyway, thus 2 less request
    # to the DB. prefetch_related works on M2M relationships and makes
    # sure that, for instance, when querying diseases, we won't make multiple call
    # for the same set of data
    return Phenopacket.objects \
        .filter(id__in=data_type_results(query, params, "id")) \
        .select_related(*PHENOPACKET_SELECT_REL) \
        .prefetch_related(*PHENOPACKET_PREFETCH)


QUERY_RESULTS_FN: Dict[str, Callable] = {
    DATA_TYPE_EXPERIMENT: experiment_query_results,
    DATA_TYPE_PHENOPACKET: phenopacket_query_results,
}

QUERY_RESULT_SERIALIZERS = {
    DATA_TYPE_EXPERIMENT: ExperimentSerializer,
    DATA_TYPE_PHENOPACKET: PhenopacketSerializer,
}


def search(request, internal_data=False):
    if request.method == "POST":
        data_type = (request.data or {}).get("data_type")
    else:
        data_type = request.query_params.get("data_type")

    if not data_type:
        return Response(errors.bad_request_error("Missing data_type in request body"), status=400)

    if request.method == "POST":
        query = (request.data or {}).get("query")
    else:
        logger.info(request.query_params)
        query = request.query_params.get("query", "null")  # This'll get decoded to None as a fallback case

        try:
            query = json.loads(query)
        except json.decoder.JSONDecodeError:
            return Response(errors.bad_request_error(f"Invalid query JSON: {query}"), status=400)

    if query is None:
        return Response(errors.bad_request_error("Missing query in request body"), status=400)

    start = datetime.now()

    if data_type not in DATA_TYPES:
        return Response(errors.bad_request_error(f"Missing or invalid data type (Specified: {data_type})"), status=400)

    try:
        compiled_query, params = postgres.search_query_to_psycopg2_sql(query, DATA_TYPES[data_type]["schema"])
    except (SyntaxError, TypeError, ValueError) as e:
        return Response(errors.bad_request_error(f"Error compiling query (message: {str(e)})"), status=400)

    if not internal_data:
        tables = Table.objects.filter(ownership_record_id__in=data_type_results(
            query=compiled_query,
            params=params,
            key="table_id"
        ))  # TODO: Maybe can avoid hitting DB here
        return Response(build_search_response([{"id": t.identifier, "data_type": data_type} for t in tables], start))

    serializer_class = QUERY_RESULT_SERIALIZERS[data_type]
    query_function = QUERY_RESULTS_FN[data_type]

    return Response(build_search_response({
        table_id: {
            "data_type": data_type,
            "matches": list(serializer_class(p).data for p in table_objects)
        } for table_id, table_objects in itertools.groupby(
            query_function(compiled_query, params),
            key=lambda o: str(o.table_id)
        )
    }, start))


# Cache page for the requested url
@cache_page(60 * 60 * 2)
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def chord_search(request):
    return search(request, internal_data=False)


# Mounted on /private/, so will get protected anyway; this allows for access from federation service
# TODO: Ugly and misleading permissions
# Cache page for the requested url
@cache_page(60 * 60 * 2)
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def chord_private_search(request):
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


def chord_table_search(query, table_id, start, internal=False) -> Tuple[Union[None, bool, list], Optional[str]]:
    # Check that dataset exists
    table = Table.objects.get(ownership_record_id=table_id)

    try:
        compiled_query, params = postgres.search_query_to_psycopg2_sql(query, DATA_TYPES[table.data_type]["schema"])
    except (SyntaxError, TypeError, ValueError) as e:
        logger.exception(f"[CHORD Metadata] Error encountered compiling query {query}:\n    {str(e)}")
        return None, f"Error compiling query (message: {str(e)})"

    debug_log(f"Finished compiling query in {datetime.now() - start}")

    query_results = QUERY_RESULTS_FN[table.data_type](
        query=sql.SQL("{} AND table_id = {}").format(compiled_query, sql.Placeholder()),
        params=params + (table.identifier,)
    )

    if internal:
        debug_log(f"Started fetching from queryset and serializing data at {datetime.now() - start}")
        serialized_data = QUERY_RESULT_SERIALIZERS[table.data_type](query_results, many=True).data
        debug_log(f"Finished running query and serializing in {datetime.now() - start}")

        return serialized_data, None

    return len(query_results) > 0, None


def chord_table_search_response(request, table_id, internal=False):
    start = datetime.now()
    debug_log(f"Started {'private' if internal else 'public'} table search")

    # We let people either use GET or POST. Get stuff from params if GET, or data if POST.

    if request.method == "POST":
        query = (request.data or {}).get("query")

    else:
        query = request.query_params.get("query", "null")  # This will get decoded to None as a fallback case

        try:
            query = json.loads(query)
        except json.decoder.JSONDecodeError:
            return Response(errors.bad_request_error("Invalid query JSON"), status=400)

    if query is None:
        # TODO: Better error
        return Response(errors.bad_request_error("Missing query in request body"), status=400)

    data, err = chord_table_search(query, table_id, start, internal=internal)

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
    # Search data types in specific tables without leaking internal data
    return chord_table_search_response(request, table_id, internal=False)


# Mounted on /private/, so will get protected anyway; this allows for access from federation service
# TODO: Ugly and misleading permissions
# Cache page for the requested url
@cache_page(60 * 60 * 2)
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def chord_private_table_search(request, table_id):
    # Search data types in specific tables
    # Private search endpoints are protected by URL namespace, not by Django permissions.
    return chord_table_search_response(request, table_id, internal=True)
