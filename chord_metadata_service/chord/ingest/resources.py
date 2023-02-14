from chord_metadata_service.resources import models as rm, utils as ru

__all__ = ["ingest_resource"]


def ingest_resource(resource: dict) -> rm.Resource:
    namespace_prefix = resource["namespacePrefix"].strip()
    version = resource.get("version", "").strip()
    assigned_resource_id = ru.make_resource_id(namespace_prefix, version)

    rs_obj, _ = rm.Resource.objects.get_or_create(
        # If this doesn't match assigned_resource_id, it'll throw anyway
        id=assigned_resource_id,
        name=resource["name"],
        namespace_prefix=namespace_prefix,
        url=resource["url"],
        version=version,
        iri_prefix=resource["iriPrefix"],
        extra_properties=resource.get("extra_properties", {})
        # TODO extra_properties
    )

    return rs_obj
