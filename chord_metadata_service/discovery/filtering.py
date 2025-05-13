from copy import deepcopy

from bento_lib.discovery import DiscoveryEntity
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http.request import QueryDict
from rest_framework.request import Request as DrfRequest
from structlog.stdlib import BoundLogger

from chord_metadata_service.authz.types import DataTypeDiscoveryPermissions
from .censorship import get_max_query_parameters
from .exceptions import DiscoveryEmptyException
from .fields import get_field_options, filter_queryset_field_value
from .pydantic_models import DiscoveryQuery
from .scope import ValidatedDiscoveryScope
from .utils import get_discovery_queryable_fields, get_discovery_field_set_permissions, empty_discovery

__all__ = [
    "discovery_filter_queryset",
]


async def discovery_filter_queryset(
    discovery_scope: ValidatedDiscoveryScope,
    request: DrfRequest,
    queryset_model_name: DiscoveryEntity,
    queryset: QuerySet,
    dt_permissions: DataTypeDiscoveryPermissions,
    lg: BoundLogger,
) -> tuple[QuerySet, list[str]]:
    """
    Process query parameters, check validity, and filter the queryset by the passed parameters.
    :param discovery_scope: Discovery scope for the queryset we're filtering.
    :param request: The request to extract the query parameters from.
    :param queryset_model_name: TODO
    :param queryset: TODO
    :param dt_permissions: Permissions meta-dictionary of {data type: permissions dictionary}.
    :param lg: BoundLogger object.
    """

    discovery = discovery_scope.discovery

    if empty_discovery(discovery):
        # If there are no fields defined, it means implicitly that we also have no search filters or charts defined.
        # If neither overview nor search have entries, it means no discovery is allowed.
        raise DiscoveryEmptyException()

    # Process query parameters and check validity

    qp: QueryDict = deepcopy(request.query_params)

    # - remove project/dataset (i.e., scope) query parameters; otherwise, they get included in the fields and the
    #   response yields an error, as they are (presumably) not queryable fields in the discovery config.
    # - store project and dataset before we remove them for logging purposes.
    if "project" in qp:
        del qp["project"]
    if "dataset" in qp:
        del qp["dataset"]

    query = DiscoveryQuery.model_validate({k: v[0] if isinstance(v, list) else v for k, v in qp.items()})
    del qp

    # Now we have the DiscoveryQuery object, and we need to run this query on our Phenopackets: ------------------------

    queryable_fields = get_discovery_queryable_fields(discovery)

    queried_fields = query.queried_fields()  # fields for determining field permissions
    overall_permissions, qf_permissions = get_discovery_field_set_permissions(discovery, queried_fields, dt_permissions)

    # TODO: in the future, scope repr passing to exceptions should be structured data:
    scope_repr = repr(discovery_scope)

    # we check against qp, not queried_fields, for max query parameters, since a user may be filtering based on more
    # than one value for the same field (not that this works most of the time, at the moment.)
    if (n_queried := len(query)) > get_max_query_parameters(discovery, overall_permissions):
        raise ValidationError(f"Wrong number of fields: {n_queried} ({scope_repr})")

    if not overall_permissions.counts:
        raise ValidationError(f"Insufficient permissions to access counts ({scope_repr})")

    for field, value in query.items():
        if field not in queryable_fields:
            raise ValidationError(f"Unsupported field used in query: {field} ({scope_repr})")

        field_props = queryable_fields[field]

        # Ensure the passed value is in our pre-determined array of options:
        options = await get_field_options(field, discovery_scope, qf_permissions[field])
        if (
            value not in options
            and not (
                # case-insensitive search on categories
                field_props.datatype == "string"
                and value.lower() in [o.lower() for o in options]
            )
            and not (
                # no restriction when enum is not set for categories
                field_props.datatype == "string"
                and getattr(field_props.config, "enum") is None
            )
        ):
            raise ValidationError(f"Invalid value used in query: {value} ({scope_repr})")

        # recursion
        queryset = filter_queryset_field_value(queryset_model_name, queryset, field_props, value, lg)

    return queryset, queried_fields
