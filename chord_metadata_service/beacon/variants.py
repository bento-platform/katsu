from abc import ABC, abstractmethod
from logging import Logger

from .exceptions import InvalidBeaconQuery
from .models import BeaconGenomicVariantRequestParameters

__all__ = ["VariantsService", "Gohan"]


# noinspection PyUnusedLocal
class VariantsService(ABC):
    @abstractmethod
    def __init__(self, config: dict, logger: Logger):  # pragma: no cover
        pass

    # should return list of biosample ids, typing for return type could be better
    # in fact we may want more details returned
    # also, query will need more input than this
    # permissions? (we could check these before launching)
    # dataset and project scope (although these are meaningless to gohan )
    # bearer token
    # .... may simply need to attach entire request here
    @abstractmethod
    async def query(self, query: BeaconGenomicVariantRequestParameters) -> list[str]:  # pragma: no cover
        pass


class Gohan(VariantsService):
    def __init__(self, config: dict, logger: Logger):
        self.config = config  # what goes in here?
        self.logger = logger

    async def query(self, beacon_variants_query: BeaconGenomicVariantRequestParameters, ids_only=True) -> list[str]:
        # map beacon query -> variants query (presumably GET)

        # control flow for beacon variant query types
        # http://docs.genomebeacons.org/variant-queries/
        start = beacon_variants_query.get("start")
        end = beacon_variants_query.get("end")
        geneId = beacon_variants_query.get("geneId")

        numStart = len(start) if start is not None else 0
        numEnd = len(end) if end is not None else 0

        sequence_query = numStart == 1 and numEnd == 0
        range_query = numStart == 1 and numEnd == 1
        bracket_query = numStart == 2 and numEnd == 2
        geneId_query = geneId is not None

        if geneId_query:
            if start is not None or end is not None:
                raise InvalidBeaconQuery("invalid mix of geneId and start/end parameters")
            return await geneId_query_to_gohan(beacon_args, granularity, ids_only)

        # required everywhere except geneId query
        if beacon_args.get("referenceName") is None:
            raise InvalidBeaconQuery(message="referenceName parameter required")

        if sequence_query:
            return await sequence_query_to_gohan(beacon_args, granularity, ids_only)

        if range_query:
            return await range_query_to_gohan(beacon_args, granularity, ids_only)

        if bracket_query:
            return await bracket_query_to_gohan(beacon_args, granularity, ids_only)

        # no other cases
        raise InvalidBeaconQuery()

        # ##### control flow: which type of query?
        # geneId query
        # sequence query
        # range_query
        # bracket_query

        # presumably some variant service implementations should be able to do this stuff themselves
        # so we don't necessarily need abstract methods for these

        # make http request to query url
        # return results, ideally a list of biosample ids
        return []

    # static? do we even need to have this in the superclass? All we really care about is query()
    # plus this has the same function signature as query(), which is weird
    def _map_beacon_query_to_gohan_query(self, beacon_query: BeaconGenomicVariantRequestParameters):
        return {}

    # needs better biosample id typing
    # exists in phenopackets model, but is more complex than needed
    def _map_gohan_results_to_biosample_ids(self, gohan_response) -> list[str]:
        pass


# code for variants search

# - make a request to a variants service
# - handle the response,
#
# Currently we expect to use gohan, but code should be generalizable

# Gohan issues:
# - doesn't follow any kind of standard for request or response
# - endpoint structure is also non-standard
# So make sure to package gohan stuff in its own class or something, since other services will behave differently

# The main utility we want from a variant service :

# 1. accept a request about variants with params:
# - at least do bare minimum params (assemblyId, chromosome, start, end, alt, ref)... start and end can be tuples in beacon (aka "brackets")
# other possible params from beacon spec:
# - variantType (eg DEL, INS, DUP, INV, CNV, BND)
# - variantMaxLength
# - variantMinLength
# - molecularEffects (eg frameshift, missense... confusingly VLM seems to call this "variant type")
# - aminoacidChange
# - ... and more, but possibly to change with upcoming beacon "VQS" query format
#
# - other params that could be either handled by the reference service or mapped here:
# - query by geneId (could be mapped to start, end before passing on request)
# - liftover between assemblies
#

# 2. return a response to search
# - our main interest currently is not in receiving full variant records, in e.g. VRS format
# - we mainly want a list of biosample ids (the ids in the vcfs matching the search) so that we can intersect them with katsu results


# xxxxxxxxxxxxxxx so, any service needs:
# urls: a variant query url, /service-info, some kind of overview for e.g. num files ingested
# query schema (ie query params and their expected values)
# response schema
# ... both query and response schemas should specify whether coordinates are zero or one based
# auth details?

# abstract class for DRS backend:
# https://github.com/bento-platform/bento_drs/blob/master/chord_drs/backends/base.py


# already have mapping code for gohan in beacon
# each implementation will have its own request and response mapping code
# request: map from beacon query to variants service query
# response: map from variants service query to what we need to intersect with katsu (so, a list of biosample ids)
# ... if we ever want full-record variants response we may also want to map from variants service response to beacon response
# in particular this will require pagination, which should be less important for the other responses, unless we are stuck
# calling a variants service that can't return a simple list

# biosample_ids
# num_results
