from collections.abc import Iterable

from bento_lib.discovery import DiscoveryEntity
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from rest_framework.request import Request as DrfRequest
from structlog.stdlib import BoundLogger

from chord_metadata_service.authz.types import DataTypeDiscoveryPermissions, DataPermissions
from .censorship import get_max_query_parameters
from .exceptions import DiscoveryEmptyException
from .fields import get_field_options, filter_queryset_field_value
from .pydantic_models import DiscoveryQuery
from .scope import ValidatedDiscoveryScope
from .utils import get_discovery_field_set_permissions, empty_discovery

__all__ = [
    "discovery_filter_queryset",
]


def _in_case_insensitive(val: str, i: Iterable[str]) -> bool:
    """
    Case-insensitive version of `in` operator for strings.
    """
    val_lower = val.lower()
    return any(val_lower == o.lower() for o in i)


async def validate_field_query_value(
    scope: ValidatedDiscoveryScope, field_id: str, value: str, field_permissions: DataPermissions
):
    """
    Validate a query value for a particular field against the discovery configuration and raise a ValidationError if the
    value is not a valid query for the field.
    """

    field_props = scope.discovery.fields[field_id]

    # Ensure the passed value is in our pre-determined array of options:
    options = await get_field_options(field_id, scope, field_permissions)
    if (
        value not in options
        and not (
            # case-insensitive search on categories
            field_props.datatype == "string" and _in_case_insensitive(value, options)
        )
        and not (
            # no restriction when enum is not set for categories
            field_props.datatype == "string" and field_props.config.enum is None  # narrowed type via datatype ==
        )
    ):
        raise ValidationError(f"Invalid value used in query: {value} ({repr(scope)})")


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
    :param queryset_model_name: The discovery entity being queried.
    :param queryset: The starting queryset for the discovery entity being queried.
    :param dt_permissions: Permissions meta-dictionary of {data type: permissions dictionary}.
    :param lg: BoundLogger object.
    """

    discovery = discovery_scope.discovery

    if empty_discovery(discovery):
        # If there are no fields defined, it means implicitly that we also have no search filters or charts defined.
        # If neither overview nor search have entries, it means no discovery is allowed.
        raise DiscoveryEmptyException()

    # Process query parameters and check validity
    query = DiscoveryQuery.model_validate({
        k: v[0] if isinstance(v, list) else v
        for k, v in request.query_params.items()
        if k not in ("project", "dataset")
        # - remove project/dataset (i.e., scope) query parameters; otherwise, they get included in the fields and the
        #   response yields an error, as they are (presumably) not queryable fields in the discovery config.
    })

    # Now we have the DiscoveryQuery object, and we need to run this query on our Phenopackets: ------------------------

    searchable_fields = set(discovery.get_searchable_field_ids())

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
        if field not in searchable_fields:
            raise ValidationError(f"Unsupported field used in query: {field} ({scope_repr})")

        # Ensure the passed value is in our allowed options:
        await validate_field_query_value(discovery_scope, field, value, qf_permissions[field])

        # Update queryset to include the Django ORM filter for this query field/value
        queryset = filter_queryset_field_value(queryset_model_name, queryset, discovery.fields[field], value, lg)

    return queryset, queried_fields
