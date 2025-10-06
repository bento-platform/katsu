from bento_lib.discovery import DiscoveryEntity
from collections.abc import Iterable
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
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
    queryset_entity: DiscoveryEntity,
    queryset: QuerySet,
    scope: ValidatedDiscoveryScope,
    field_id: str,
    value: str,
    field_permissions: DataPermissions
):
    """
    Validate a query value for a particular field against the discovery configuration and raise a ValidationError if the
    value is not a valid query for the field.
    """

    field_props = scope.discovery.fields[field_id]

    # Ensure the passed value is in our pre-determined array of options (or, if an {enum: null} string field, check that
    # the passed value is in the database [above the censorship threshold as needed]):
    options = await get_field_options(queryset_entity, queryset, field_id, scope, field_permissions)
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
        raise ValidationError(f"Invalid value used in field query: {field_id}={value} ({repr(scope)})")


async def discovery_filter_queryset(
    discovery_scope: ValidatedDiscoveryScope,
    query: DiscoveryQuery,
    queryset_entity: DiscoveryEntity,
    queryset: QuerySet,
    dt_permissions: DataTypeDiscoveryPermissions,
    lg: BoundLogger,
    validate_field: bool = True,
) -> tuple[QuerySet, frozenset[DiscoveryEntity]]:
    """
    Process query parameters, check validity, and filter the queryset by the passed parameters.
    :param discovery_scope: Discovery scope for the queryset we're filtering.
    :param query: The query to execute.
    :param queryset_entity: The discovery entity being queried.
    :param queryset: The starting queryset for the discovery entity being queried.
    :param dt_permissions: Permissions meta-dictionary of {data type: permissions dictionary}.
    :param lg: BoundLogger object.
    :param validate_field: Whether we should validate the field's query value against options/allowed values. Be VERY
               DELIBERATE when turning this off! This should only be used if we've already validated the field options,
               e.g., from a previous call to this function.
    """

    discovery = discovery_scope.discovery

    if empty_discovery(discovery):
        # If there are no fields defined, it means implicitly that we also have no search filters or charts defined.
        # If neither overview nor search have entries, it means no discovery is allowed.
        raise DiscoveryEmptyException()

    # We need to run the provided query on our Phenopackets: -----------------------------------------------------------

    searchable_fields = set(discovery.get_searchable_field_ids())

    queried_fields = query.queried_filter_fields()  # fields for determining field permissions
    overall_permissions, qf_permissions = get_discovery_field_set_permissions(discovery, queried_fields, dt_permissions)

    # TODO: in the future, scope repr passing to exceptions should be structured data:
    scope_repr = repr(discovery_scope)

    f_queryset = queryset

    # right now, a user cannot be filtering based on more than one value for the same field
    if (n_queried := len(query.filters)) > get_max_query_parameters(discovery, overall_permissions):
        raise ValidationError(f"Wrong number of fields: {n_queried} ({scope_repr})")

    if not overall_permissions.bool_:
        raise ValidationError(f"Insufficient permissions to access discovery ({scope_repr})")

    queried_entities: set[DiscoveryEntity] = set()
    field_queried_entities: dict[str, DiscoveryEntity] = {}

    for field, value in query.filters.items():
        if field not in searchable_fields:
            raise ValidationError(f"Unsupported field used in query: {field} ({scope_repr})")

        # Ensure the passed value is in our allowed options:
        #  - pass original queryset in for determining valid filter values
        #  - can throw DiscoveryFilterRewriteException if we cannot rewrite the field mapping as a subpath of the
        #    queryset model
        if validate_field:
            await validate_field_query_value(
                queryset_entity, queryset, discovery_scope, field, value, qf_permissions[field]
            )

        # Update queryset to include the Django ORM filter for this query field/value
        #  - can throw DiscoveryFilterRewriteException if we cannot rewrite the field mapping as a subpath of the
        #    queryset model, but every case SHOULD be covered here.
        f_queryset, queried_entity = await filter_queryset_field_value(
            queryset_entity, f_queryset, discovery.fields[field], value, lg
        )

        queried_entities.add(queried_entity)
        field_queried_entities[field] = queried_entity

    return f_queryset, frozenset(queried_entities)
