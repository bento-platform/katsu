from bento_lib.discovery import DiscoveryEntity
from collections.abc import Iterable
from django.core.exceptions import ValidationError
from django.db.models import Prefetch, QuerySet
from structlog.stdlib import BoundLogger

from chord_metadata_service.authz.types import DataTypeDiscoveryPermissions, DataPermissions
from .censorship import get_max_query_parameters
from .exceptions import DiscoveryEmptyException, DiscoveryFilterRewriteException
from .fields import get_field_options, filter_queryset_field_value
from .fields_utils import resolve_filter_mapping_to_queryset_model
from .model_lookups import DISCOVERY_ENTITY_NAMES_TO_MODEL
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
    queryset_model_name: DiscoveryEntity,
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
    options = await get_field_options(queryset_model_name, queryset, field_id, scope, field_permissions)
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
    query: DiscoveryQuery,
    queryset_model_name: DiscoveryEntity,
    queryset: QuerySet,
    dt_permissions: DataTypeDiscoveryPermissions,
    lg: BoundLogger,
    nested_prefetch: bool = False,
    already_fetched: frozenset[DiscoveryEntity] = frozenset(),
) -> tuple[QuerySet, frozenset[DiscoveryEntity]]:
    """
    Process query parameters, check validity, and filter the queryset by the passed parameters.
    :param discovery_scope: Discovery scope for the queryset we're filtering.
    :param query: The query to execute.
    :param queryset_model_name: The discovery entity being queried.
    :param queryset: The starting queryset for the discovery entity being queried.
    :param dt_permissions: Permissions meta-dictionary of {data type: permissions dictionary}.
    :param nested_prefetch: If true, it means we're filtering in a "prefetch" context, meaning we skip out-of-bounds
                            fields (e.g., querying individual.sex from biosample) instead of erroring out, and we don't
                            further recursively do more prefetching.
    :param already_fetched: If we're in a nested prefetch, we don't want to enter an infinite loop, so this stores
                            entities which have already been fetched.
    :param lg: BoundLogger object.
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
        raise ValidationError(f"Insufficient permissions to access counts ({scope_repr})")

    queried_entities: set[DiscoveryEntity] = set()
    field_queried_entities: dict[str, DiscoveryEntity] = {}

    for field, value in query.filters.items():
        if field not in searchable_fields:
            raise ValidationError(f"Unsupported field used in query: {field} ({scope_repr})")

        try:
            # Ensure the passed value is in our allowed options:
            #  - pass original queryset in for determining valid filter values
            #  - can throw DiscoveryFilterRewriteException if we cannot rewrite the field mapping as a subpath of the
            #    queryset model
            await validate_field_query_value(
                queryset_model_name, queryset, discovery_scope, field, value, qf_permissions[field]
            )

            # Update queryset to include the Django ORM filter for this query field/value
            #  - can throw DiscoveryFilterRewriteException if we cannot rewrite the field mapping as a subpath of the
            #    queryset model
            f_queryset, queried_entity = filter_queryset_field_value(
                queryset_model_name, f_queryset, discovery.fields[field], value, lg
            )

            queried_entities.add(queried_entity)
            field_queried_entities[field] = queried_entity

        except DiscoveryFilterRewriteException as e:
            if not nested_prefetch:
                raise e

    # Build filtered "join" prefetches to limit *queried* nested entities to those which match filters: ----------------

    # TODO: explain this:

    # TODO: determine if we need to do this
    # TODO: refactor to get this from the field normalizing code (so it can give us the "path" of queried entities...)
    if queryset_model_name in ("individual", "phenopacket") and "experiment_result" in queried_entities:
        queried_entities.add("experiment")
        # may trigger the next if-statement right below
    if queryset_model_name in ("individual", "phenopacket") and "experiment" in queried_entities:
        queried_entities.add("biosample")
        # may trigger the next if-statement right below
    if queryset_model_name == "individual" and "biosample" in queried_entities:
        queried_entities.add("phenopacket")
    if queryset_model_name == "biosample" and "experiment_result" in queried_entities:
        queried_entities.add("experiment")

    if (  # not nested_prefetch and
        nested_queried_entities := tuple(
            filter(lambda ee: ee != queryset_model_name and ee not in already_fetched, queried_entities)
        )
    ):
        # If we're not in a "nested prefetch" context already, we may have nested discovery entities we're querying.
        # We want to limit the Django ORM "join" with these nested entities to only include nested objects which also
        # match the subset of our query applying to the nested entity type, otherwise we may end up in situations where
        # we get "all experiments of all phenopackets containing WGS experiments", rather than our (potentially) desired
        # "all phenopackets with at least one WGS experiment, and only those WGS experiments included in the result-set"

        await lg.adebug(
            "adding filtered prefetches",
            nested_queried_entities=nested_queried_entities,
            already_fetched=already_fetched,
        )

        filtered_prefetches: list[Prefetch] = []

        for e in nested_queried_entities:
            filtered_prefetches.append(
                Prefetch(
                    resolve_filter_mapping_to_queryset_model(queryset_model_name, e, ()),
                    queryset=(await discovery_filter_queryset(
                        discovery_scope,
                        query,
                        e,
                        DISCOVERY_ENTITY_NAMES_TO_MODEL[e].get_model_scoped_queryset(discovery_scope),
                        dt_permissions,
                        lg,
                        nested_prefetch=True,  # For this recursive call, we shouldn't do any more recursive prefetching
                        already_fetched=already_fetched | {queryset_model_name},  # TODO: check this logic
                    ))[0],
                    to_attr=f"{e}_matches",
                )
            )

        f_queryset = f_queryset.prefetch_related(*filtered_prefetches)

    return f_queryset, frozenset(queried_entities)
