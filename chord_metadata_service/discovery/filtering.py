from bento_lib.discovery import DiscoveryEntity, FieldDefinition
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from structlog.stdlib import BoundLogger

from chord_metadata_service.authz.types import DataTypeDiscoveryPermissions, DataPermissions
from .exceptions import DiscoveryEmptyException
from .field_definition_provider import FieldDefinitionProvider
from .fields import (
    is_curie_format,
    is_number_query_format,
    is_date_query_format,
    get_field_options,
    filter_queryset_field_value,
    field_value_is_in_options,
)
from .pydantic_models import DiscoveryQueryFilterOneOf, DiscoveryQuery
from .scope import ValidatedDiscoveryScope
from .utils import empty_discovery

__all__ = [
    "discovery_filter_queryset",
]


async def validate_field_query_value(
    queryset_entity: DiscoveryEntity,
    scope: ValidatedDiscoveryScope,
    field_id: str,
    field_def: FieldDefinition,
    value: str | DiscoveryQueryFilterOneOf,
    field_permissions: DataPermissions
):
    """
    Validate a query value for a particular field against the discovery configuration and raise a ValidationError if the
    value is not a valid query for the field.
    """

    # Validation for the field filter value:
    #  - check it is in our pre-determined array of options
    #  - or, if an {enum: null} string field, check that the passed value is in the database
    #    [above the censorship threshold as needed]
    #  - or, if the requester has query:data permissions, check that the passed value matches a valid format for the
    #    field (a range query for a number or date)

    options = await get_field_options(queryset_entity, field_def, scope, field_permissions)
    if (
        not field_value_is_in_options(value, frozenset(options), field_def.datatype)
        and not (
            # TODO: this might be not correct?
            # no restriction when enum is not set for categories
            field_def.datatype == "string" and field_def.config.enum is None  # narrowed type via datatype ==
        )
        and not (
            # TODO: this might be not correct?
            # no restriction when enum is not set for categories
            field_def.datatype == "ontology-class" and field_def.config.enum is None and is_curie_format(value)
        )
        and not (
            # with query:data permissions, we can query ANY range of numbers
            field_permissions.data and field_def.datatype == "number" and is_number_query_format(value)
        )
        and not (
            # with query:data permissions, we can query ANY range of dates
            field_permissions.data and field_def.datatype == "date" and is_date_query_format(value)
        )
    ):
        raise ValidationError(f"Invalid value used in field query: {field_id}={value} ({repr(scope)})")


async def discovery_filter_queryset(
    discovery_scope: ValidatedDiscoveryScope,
    field_definition_provider: FieldDefinitionProvider,
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
    :param field_definition_provider: Field definition provider (supporting both discovery config + ad-hoc field defs.)
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

    searchable_fields = field_definition_provider.searchable_fields

    # get individual field permissions needed for our query and validate overall permissions
    _, qf_permissions = query.get_and_validate_permissions(discovery_scope, dt_permissions)

    f_queryset = queryset

    queried_entities: set[DiscoveryEntity] = set()
    field_queried_entities: dict[str, DiscoveryEntity] = {}

    for field, value in query.filters.items():
        if field not in searchable_fields:
            raise ValidationError(f"Unsupported field used in query: {field} ({repr(discovery_scope)})")

        field_def = field_definition_provider[field]

        # Ensure the passed value is in our allowed options:
        #  - pass original queryset in for determining valid filter values
        #  - can throw DiscoveryFilterRewriteException if we cannot rewrite the field mapping as a subpath of the
        #    queryset model
        if validate_field:
            await validate_field_query_value(
                queryset_entity, discovery_scope, field, field_def, value, qf_permissions[field]
            )

        # Update queryset to include the Django ORM filter for this query field/value
        #  - can throw DiscoveryFilterRewriteException if we cannot rewrite the field mapping as a subpath of the
        #    queryset model, but every case SHOULD be covered here.
        f_queryset, queried_entity = await filter_queryset_field_value(
            queryset_entity, f_queryset, field_def, value, lg
        )

        queried_entities.add(queried_entity)
        field_queried_entities[field] = queried_entity

    return f_queryset, frozenset(queried_entities)
