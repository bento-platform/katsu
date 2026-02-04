import json
from chord_metadata_service.resources import models as rm, utils as ru
from structlog.stdlib import BoundLogger

__all__ = ["ingest_resource"]


def ingest_resource(resource: dict, logger: BoundLogger) -> rm.Resource:
    namespace_prefix = resource["namespace_prefix"].strip()
    version = resource.get("version", "").strip()
    assigned_resource_id = ru.make_resource_id(namespace_prefix, version)

    try:
        # if we already have a resource with this assigned ID, update it with the latest definition during this
        # ingestion run (allowing us to fix IRI prefixes, for example):

        existing_rs = rm.Resource.objects.get(
            id=assigned_resource_id, namespace_prefix=namespace_prefix, version=version
        )

        if (
            existing_rs.name != resource["name"]
            or existing_rs.url != resource["url"]
            or existing_rs.iri_prefix != resource["iri_prefix"]
            or (
                json.dumps(resource.get("extra_properties", {}), sort_keys=True)
                != json.dumps(existing_rs.extra_properties, sort_keys=True)
            )
        ):
            logger.warning("updating existing resource", resource=resource)

            existing_rs.name = resource["name"]
            existing_rs.url = resource["url"]
            existing_rs.iri_prefix = resource["iri_prefix"]
            existing_rs.extra_properties = resource.get("extra_properties", existing_rs.extra_properties)
            existing_rs.save()

        return existing_rs

    except rm.Resource.DoesNotExist:
        pass

    rs_obj, _ = rm.Resource.objects.get_or_create(
        id=assigned_resource_id,
        name=resource["name"],
        namespace_prefix=namespace_prefix,
        url=resource["url"],
        version=version,
        iri_prefix=resource["iri_prefix"],
        extra_properties=resource.get("extra_properties", {}),
        # TODO extra_properties
    )

    return rs_obj
