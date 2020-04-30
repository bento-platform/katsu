import itertools

from collections import Counter
from datetime import datetime
from django.db import connection
from django.conf import settings
from psycopg2 import sql
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from chord_lib.responses import errors
from chord_lib.search import build_search_response, postgres
from chord_metadata_service.metadata.settings import DEBUG
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.api_views import PHENOPACKET_PREFETCH
from chord_metadata_service.phenopackets.models import Phenopacket
from chord_metadata_service.phenopackets.schemas import PHENOPACKET_SCHEMA
from chord_metadata_service.phenopackets.serializers import PhenopacketSerializer
from chord_metadata_service.metadata.elastic import es

from .models import Dataset
from .permissions import OverrideOrSuperUserOnly

PHENOPACKET_DATA_TYPE_ID = "phenopacket"

PHENOPACKET_METADATA_SCHEMA = {
    "type": "object"
    # TODO
}


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_list(_request):
    return Response([{"id": PHENOPACKET_DATA_TYPE_ID, "schema": PHENOPACKET_SCHEMA}])


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_phenopacket(_request):
    return Response({
        "id": PHENOPACKET_DATA_TYPE_ID,
        "schema": PHENOPACKET_SCHEMA,
        "metadata_schema": PHENOPACKET_METADATA_SCHEMA
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_phenopacket_schema(_request):
    return Response(PHENOPACKET_SCHEMA)


@api_view(["GET"])
@permission_classes([AllowAny])
def data_type_phenopacket_metadata_schema(_request):
    return Response(PHENOPACKET_METADATA_SCHEMA)


@api_view(["GET"])
@permission_classes([AllowAny])
def table_list(request):
    data_types = request.query_params.getlist("data-type")
    if PHENOPACKET_DATA_TYPE_ID not in data_types:
        return Response(errors.bad_request_error(f"Missing or invalid data type (Specified: {data_types})"), status=400)

    return Response([{
        "id": d.identifier,
        "name": d.title,
        "metadata": {
            "description": d.description,
            "project_id": d.project_id,
            "created": d.created.isoformat(),
            "updated": d.updated.isoformat()
        },
        "schema": PHENOPACKET_SCHEMA
    } for d in Dataset.objects.all()])


# TODO: Remove pragma: no cover when GET/POST implemented
# TODO: Should this exist? managed
@api_view(["DELETE"])
@permission_classes([OverrideOrSuperUserOnly])
def table_detail(request, table_id):  # pragma: no cover
    # TODO: Implement GET, POST
    # TODO: Permissions: Check if user has control / more direct access over this table and/or dataset?
    #  Or just always use owner...
    try:
        table = Dataset.objects.get(identifier=table_id)
    except Dataset.DoesNotExist:
        return Response(errors.not_found_error(f"Table with ID {table_id} not found"), status=404)

    if request.method == "DELETE":
        table.delete()
        return Response(status=204)


@api_view(["GET"])
@permission_classes([OverrideOrSuperUserOnly])
def chord_table_summary(_request, table_id):
    try:
        table = Dataset.objects.get(identifier=table_id)
        phenopackets = Phenopacket.objects.filter(dataset=table)

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

    except Dataset.DoesNotExist:
        return Response(errors.not_found_error(f"Table with ID {table_id} not found"), status=404)


# TODO: CHORD-standardized logging
def debug_log(message):  # pragma: no cover
    if DEBUG:
        print(f"[CHORD Metadata {datetime.now()}] [DEBUG] {message}", flush=True)


def phenopacket_results(query, params, key="id"):
    with connection.cursor() as cursor:
        debug_log(f"Executing SQL:\n    {query.as_string(cursor.connection)}")
        cursor.execute(query.as_string(cursor.connection), params)
        return set(dict(zip([col[0] for col in cursor.description], row))[key] for row in cursor.fetchall())


def phenopacket_query_results(query, params):
    # TODO: possibly a quite inefficient way of doing things...
    # To expand further on this query : the select_related call
    # will join on these tables we'd call anyway, thus 2 less request
    # to the DB. prefetch_related works on M2M relationships and makes
    # sure that, for instance, when querying diseases, we won't make multiple call
    # for the same set of data
    return Phenopacket.objects.filter(
        id__in=phenopacket_results(query, params, "id")
    ).select_related(
        'subject',
        'meta_data'
    ).prefetch_related(
        *PHENOPACKET_PREFETCH
    )


def search(request, internal_data=False):
    if "data_type" not in request.data:
        return Response(errors.bad_request_error("Missing data_type in request body"), status=400)

    if "query" not in request.data:
        return Response(errors.bad_request_error("Missing query in request body"), status=400)

    start = datetime.now()

    if request.data["data_type"] != PHENOPACKET_DATA_TYPE_ID:
        return Response(
            errors.bad_request_error(f"Missing or invalid data type (Specified: {request.data['data_type']})"),
            status=400
        )

    try:
        compiled_query, params = postgres.search_query_to_psycopg2_sql(request.data["query"], PHENOPACKET_SCHEMA)
    except (SyntaxError, TypeError, ValueError) as e:
        return Response(errors.bad_request_error(f"Error compiling query (message: {str(e)})"), status=400)

    if not internal_data:
        datasets = Dataset.objects.filter(identifier__in=phenopacket_results(
            query=compiled_query,
            params=params,
            key="dataset_id"
        ))  # TODO: Maybe can avoid hitting DB here
        return Response(build_search_response([{"id": d.identifier, "data_type": PHENOPACKET_DATA_TYPE_ID}
                                               for d in datasets], start))

    return Response(build_search_response({
        dataset_id: {
            "data_type": PHENOPACKET_DATA_TYPE_ID,
            "matches": list(PhenopacketSerializer(p).data for p in dataset_phenopackets)
        } for dataset_id, dataset_phenopackets in itertools.groupby(
            phenopacket_query_results(compiled_query, params),
            key=lambda p: str(p.dataset_id)
        )
    }, start))


@api_view(["POST"])
@permission_classes([AllowAny])
def chord_search(request):
    return search(request, internal_data=False)


# Mounted on /private/, so will get protected anyway; this allows for access from federation service
# TODO: Ugly and misleading permissions
@api_view(["POST"])
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


# TODO: unsure why we chose POST for this endpoint? Should be GET me thinks
def fhir_search(request, internal_data=False):
    # TODO: not all that sure about the query format we'll want
    # keep it simple for now
    if "query" not in request.data:
        return Response(errors.bad_request_error("Missing query in request body"), status=400)

    query = request.data["query"]
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
        return Response(build_search_response([{"id": d.identifier, "data_type": PHENOPACKET_DATA_TYPE_ID}
                                               for d in datasets], start))
    return Response(build_search_response({
        dataset_id: {
            "data_type": PHENOPACKET_DATA_TYPE_ID,
            "matches": list(PhenopacketSerializer(p).data for p in dataset_phenopackets)
        } for dataset_id, dataset_phenopackets in itertools.groupby(phenopackets, key=lambda p: str(p.dataset_id))
    }, start))


@api_view(["POST"])
@permission_classes([AllowAny])
def fhir_public_search(request):
    return fhir_search(request)


# Mounted on /private/, so will get protected anyway
# TODO: Ugly and misleading permissions
@api_view(["POST"])
@permission_classes([AllowAny])
def fhir_private_search(request):
    return fhir_search(request, internal_data=True)


def chord_table_search(request, table_id, internal=False):
    start = datetime.now()
    debug_log(f"Started {'private' if internal else 'public'} table search")

    if request.data is None or "query" not in request.data:
        # TODO: Better error
        return Response(errors.bad_request_error("Missing query in request body"), status=400)

    # Check that dataset exists
    dataset = Dataset.objects.get(identifier=table_id)

    try:
        compiled_query, params = postgres.search_query_to_psycopg2_sql(request.data["query"], PHENOPACKET_SCHEMA)
    except (SyntaxError, TypeError, ValueError) as e:
        print("[CHORD Metadata] Error encountered compiling query {}:\n    {}".format(request.data["query"], str(e)))
        return Response(errors.bad_request_error(f"Error compiling query (message: {str(e)})"), status=400)

    debug_log(f"Finished compiling query in {datetime.now() - start}")

    query_results = phenopacket_query_results(
        query=sql.SQL("{} AND dataset_id = {}").format(compiled_query, sql.Placeholder()),
        params=params + (dataset.identifier,)
    )

    debug_log(f"Finished running query in {datetime.now() - start}")

    if internal:
        serialized_data = PhenopacketSerializer(query_results, many=True).data
        debug_log(f"Finished running query and serializing in {datetime.now() - start}")

        return Response(build_search_response(serialized_data, start))

    return Response(len(query_results) > 0)


@api_view(["POST"])
@permission_classes([AllowAny])
def chord_public_table_search(request, table_id):
    # Search phenopacket data types in specific tables without leaking internal data
    return chord_table_search(request, table_id, internal=False)


# Mounted on /private/, so will get protected anyway; this allows for access from federation service
# TODO: Ugly and misleading permissions
@api_view(["POST"])
@permission_classes([AllowAny])
def chord_private_table_search(request, table_id):
    # Search phenopacket data types in specific tables
    # Private search endpoints are protected by URL namespace, not by Django permissions.
    return chord_table_search(request, table_id, internal=True)
