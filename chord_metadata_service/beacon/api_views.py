from adrf.decorators import api_view
from bento_lib.auth.permissions import P_QUERY_DATA
from bento_lib.auth.resources import RESOURCE_EVERYTHING

# from chord_metadata_service.authz.middleware import authz_middleware
# from chord_metadata_service.authz.permissions import BentoAllowAny, BentoAllowAnyReadOnly, BentoDeferToHandler
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.authz.permissions import BentoAllowAny, BentoAllowAnyReadOnly, BentoDeferToHandler

from .. import __version__
from ..logger import logger
from .models import BeaconRequest
from .utils import get_beacon_format_service_info, get_service_info


async def _data_endpoint(request: Request, _entry_id: str | None = None):
    await authz_middleware.async_evaluate_one(request, RESOURCE_EVERYTHING, P_QUERY_DATA, mark_authz_done=True)
    return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


# Mandatory endpoints:  ---------------------------------------------------------------------------


# required by beacon spec even if we don't consider this a service
# "environment" value is set by build_service_info()
@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def service_info(_request: Request):
    return Response(await get_service_info())


@api_view(["GET"])
@permission_classes([BentoAllowAny])
async def info(_request: Request):

    # needs to be wrapped in beacon response
    return Response(await get_beacon_format_service_info())


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


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def filtering_terms(request: Request, entry_id: str | None = None):
    return await _data_endpoint(request, entry_id)


# Model endpoints:  ---------------------------------------------------------------------------


# individuals ---------------------------------


@api_view(["GET", "POST"])
@permission_classes([BentoDeferToHandler])  # fix permissions here and below
async def individuals(request: Request, entry_id: str | None = None):
    query = BeaconRequest.from_drf_request(request)

    # 1 mark entity as phenopacket
    # 2 parse out filters, do discovery search, get biosample ids
    # 3 parse out variants, gohan search
    # 4 intersect 3 & 4
    # 5 somehow return the correct entity from a list of biosamples 


    return Response(query)

    # search but inject entity "phenopacket"

    # beacon_request = BeaconRequest.from_drf_request(request)
    # search_request = to_katsu_search(beacon_request, entity="phenopacket")


# not implemented:
# /individuals/{id} (client currently uses /phenopackets/{id} although we could switch
# /individuals/{id}/biosamples (these are included in phenopacket response)
# /individuals/{id}/g_variants (we typically refer to the vcf)
# /individuals/filtering_terms (not particularly useful)


# biosamples ---------------------------------


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def biosamples(request: Request, entry_id: str | None = None):

    # search but inject entity "biosample"

    return await _data_endpoint(request, entry_id)


# not implemented:
# /biosamples/{id} (currently get this from /phenopackets/{id})
# /biosamples/{id}/g_variants (prefer vcf)
# /biosamples/{id}/analyses (already packaged together with biosample at /phenopackets/{id} )
# /biosamples/{id}/runs (same)


# runs ---------------------------------

# effectively equivalent to bento experiments


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def runs(request: Request, entry_id: str | None = None):
    return await _data_endpoint(request, entry_id)


# not implemented:
# /runs/{id}  (currently pulled from phenopacket response, also available at katsu /experiments/{id}
# /runs/{id}/g_variants (redundant to vcf display)
# /runs/{id}/analyses (currently pulled from phenopackets response, not sure if katsu has an endpoint for this )


# analyses ---------------------------------

# effectively equivalent to bento experiment results


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def analyses(request: Request, entry_id: str | None = None):
    return await _data_endpoint(request, entry_id)


# not implemented:
# /analyses/{id} (currently pulled from phenopackets response)
# /analyses/{id}/g_variants  (prefer vcf display)

# variants ---------------------------------

# bento currently doesn't show variants in the client, except for
#  - variants singled out in the phenopacket
#  - showing vcfs in igv
# .... neither of which requires this endpoint


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def g_variants(request: Request, entry_id: str | None = None):

    # beacon entity "g_variant" doesn't exist in katsu
    # here we can mostly forward any variants service response

    return await _data_endpoint(request, entry_id)


# not implemented:
# /g_variants/{id}  (currently unused in bento)
# /g_variants/{id}/biosamples (should be able to get this from search)
# /g_variants/{id}/individuals (we can already get this from searching /individuals with a variant query)


# cohorts ---------------------------------

# only very roughly equivalent to bento projects
# does not seem to be a commonly used endpoints among beacons


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def cohorts(request: Request, entry_id: str | None = None):
    return await _data_endpoint(request, entry_id)


# not implemented
# /cohorts/{id}
# /cohorts/{id}/individuals  (use project instead)
# /cohorts/{id}/filtering_terms  (use filtering terms per project instead)


# datasets ---------------------------------

# effectively the same as bento datasets


@api_view(["GET"])
@permission_classes([BentoAllowAnyReadOnly | BentoDeferToHandler])
async def datasets(request: Request, entry_id: str | None = None):
    return await _data_endpoint(request, entry_id)


# not implemented:
# /datasets/{id} (currently using katsu /datasets instead)
# /datasets/{id}/biosamples (available from search)
# /datasets/{id}/individuals (available from search)
# /datasets/{id}/g_variants
# /datasets/{id}/filtering_terms


# .... choose:
# 1. code as original beacon, but call katsu with function calls rather than https
# 2. pull do querysets, etc here and serialize.. but this involves lots of redundant code

# katsu discovery search can return results for four entities:
# - phenopackets (proxy for individuals)
# - biosamples
# - experiments
#  - experiment results
# ... covering 4 of the 7 beacon entities
#  the missing ones are dataset, cohort, variants
# datasets and cohorts very roughly correspond to bento dataset / project
# we don't have a currently search like this in bento
# .... (the dataset search in the data catalogue searches only dataset metadata)

# so we want to perform a search and return the correct entity
# (katsu already knows how to do this)


# is there a beacon-spec way to handle this?
# currently pull project from url and dataset from imaginary "datasetIds" field in POST
#


# note that all granularities can now use full-record format of response
# ... this is permitted by the spec but is very non-obvious
# still need some some of distinction between full / count / bool responses
# also require separate error response

# need to call gohan and get ids back
# will still need to workaround gohan issues:
# - no scoping at all
# - some endpoints return uppercase sample ids, some return lowercase
# - endpoint structure is non-standard (not REST)
# - some query params are dubious, eg "alternative" instead of "alternate" for a variant nucleotide
# on top of this, we may want to be able to swap in a different variants service
# .. which means mappings for all this weird stuff


# to intersect with gohan results we can either:
#  1. call katsu & gohan, intersect results, and then somewhow be able to produce overview stats / full results from the resulting list of biosample ids
#  2. call gohan first, then query katsu with an additional parameter to filter results by the list of biosample ids returned by gohan
# ... and we need to allow for the cases where either gohan or katsu query can be empty (eg if just searching for variants, return all results)


# current bento public chart / overview values come from /discovery
# detailed results come from /discovery_matches, includes an "_entity" parameter
# beacon uses /search_overview to generate stats from arbitrary ids


# REQUEST

# discovery_matches() handles a bento-format request
# but we need to handles a beacon-formatted request instead
# here we can do either POST or GET
# discovery fields are already processed as get params
# but we will have to handle other
# this needs to be changed in the client

# project & dataset are given as params:
# project=fd4828ab-19e7-4096-ad52-1fa47b09fc41&dataset=8d73d397-e4d0-4151-9f8d-8fb525674919
# ... these are not beacon standard params
# however you will see similar extra params in progenetix
# ... even requestedGranularity is not a real param
# lists are stacked in the expected way: &diseases=Hashimoto+Thyroiditis&diseases=Marfan+syndrome
# but beacon will need an explicit param called "filters", so something like this:
# filters=diseases=Hashimoto+Thyroiditis&filters=diseases=Marfan+syndrome
# ... does this even work with the double equals in each param?

# note that there is already code to map beacon requests to katsu requests
# except we don't want to map from http -> http anymore, we just want to pull out params


# RESPONSE
# somewhat more freedom here
# similar to the code already written that maps katsu response to beacon response


# @classmethod
# def from_drf_request(cls, request: Request) -> "BeaconRequest":
#     if request.method == "POST":
#         payload = request.data  # Keep the nested Beacon JSON intact.
#     elif request.method == "GET":
#         payload = beacon_get_params_to_payload(request.query_params)
#     else:
#         raise ValueError("Beacon requests support GET and POST")

#     return cls.model_validate(payload)


# beacon_request = BeaconRequest.from_drf_request(request)
# search_request = to_katsu_search(beacon_request, entity="phenopacket")
