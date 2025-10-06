from dataclasses import dataclass

from bento_lib.discovery import (
    StringFieldDefinition, NumberFieldDefinition, DateFieldDefinition, FieldDefinition, DiscoveryEntity
)
from bento_lib.discovery.models.fields import ManualBinsNumberFieldConfig, AutoBinsNumberFieldConfig
from typing import Any, Iterator, Type, TypeAlias
from django.db.models import Q, Func, BooleanField, F, Value, JSONField, QuerySet, ManyToManyField, ManyToOneRel

from .exceptions import DiscoveryFilterRewriteException
from .model_lookups import DISCOVERY_ENTITY_NAMES_TO_MODEL
from .scopeable_model import BaseScopeableModel

__all__ = [
    "MAPPING_SEPARATOR",
    "JSON_PATH_ACCESSOR",
    "get_jsonb_path_query",
    "resolve_filter_mapping_to_queryset_model",
    "normalize_field_path_true_model",
    "DiscoveryFieldSubquery",
    "get_field_django_mapping_and_queried_entity",
    "get_field_django_mapping",
    "parse_individual_age",
    "labelled_range_generator",
    "monthly_generator",
    "get_nested_json_condition",
    "get_json_range_condition",
]

MAPPING_SEPARATOR = "/"
JSON_PATH_ACCESSOR = "."

AnyFieldDefinition: TypeAlias = FieldDefinition | NumberFieldDefinition | StringFieldDefinition | DateFieldDefinition


class JSONBPathFilter(Func):
    function = "jsonb_path_exists"
    output_field = BooleanField()


class JSONBPathQuery(Func):
    function = "jsonb_path_query"
    output_field = JSONField()


# Function to rewrite a tuple of strings (field path) as a Django mapping string (delimited with "__"):
field_path_to_django_mapping = "__".join


def get_jsonb_path_query(field: str, json_path: str, is_array=True, is_mapping=True):
    field_operator = "$[*]" if is_array else "$"
    query_path = mapping_to_json_path(json_path) if is_mapping else json_path
    return JSONBPathQuery(F(field), Value(f"{field_operator}.{query_path}"))


def _resolve_filter_mapping_to_queryset_model_inner_2(
    queryset_entity: DiscoveryEntity,
    field_entity: DiscoveryEntity,
    field_path: tuple[str, ...],
    force_through_phenopackets: bool,
) -> tuple[str, ...]:
    """
    Given a goal (queryset) model name and a current (field) model name, rewrite a path to a field from the field model
    name to the goal queryset model name.
    Currently, this is used as an inner function for resolve_filter_mapping_to_queryset_model, but may have more broad
    use for rewriting field paths without converting them to Django form.
    The force_through_phenopackets param forces relationships that have "shortcuts" (individuals<->biosamples, mostly)
    to be related THROUGH phenopackets.
    """

    if queryset_entity == field_entity:
        norm_entity, norm_path = normalize_field_path_true_model(field_entity, field_path)
        if norm_entity != field_entity:
            # We normalized to a different entity, so we need to do further resolving to get the simplest lookup
            # TODO: verify this cannot infinite loop with, e.g., force_through_phenopackets.
            return _resolve_filter_mapping_to_queryset_model_inner_2(
                queryset_entity, norm_entity, norm_path, force_through_phenopackets
            )
        return norm_path

    exc = DiscoveryFilterRewriteException(
        f"cannot map field model {field_entity} to filtering model {queryset_entity}"
    )

    match (queryset_entity, field_entity):
        #  - Phenopackets <-> Individuals
        case ("individual", "phenopacket"):  # re-writing the latter to the former
            if field_path[:1] == ("subject",):  # also conveniently handles the falsey case of field_path == ()
                return field_path[1:]
            if field_path[:1] == ("biosamples",) and not force_through_phenopackets:
                # we have biosamples related managers on both individuals and phenopackets
                # NOTE: this is a bit janky - we don't necessarily have individuals for all phenopackets, so this can
                # return something different. We're relying on a later join.
                return field_path
            return "phenopackets", *field_path
        case ("phenopacket", "individual"):
            if field_path[:1] == ("phenopackets",):  # also conveniently handles the falsey case of field_path == ()
                return field_path[1:]
            # If we have field_path[0] == biosamples, this one is subtle because not all phenopackets have individuals.
            # So we leave this as off of subject, although perhaps we could rely on joins to clear this up downstream...
            return "subject", *field_path
        #  - Phenopackets -> nested
        case ("phenopacket", "biosample"):  # re-writing the latter to the former
            return "biosamples", *field_path
        case ("phenopacket", "experiment"):
            return "biosamples", "experiments", *field_path
        case ("phenopacket", "experiment_result"):
            return "biosamples", "experiments", "experiment_results", *field_path
        #  - Individuals -> nested
        case ("individual", "biosample"):  # re-writing the latter to the former
            if force_through_phenopackets:
                return "phenopackets", "biosamples", *field_path
            return "biosamples", *field_path
        case ("individual", "experiment"):
            if force_through_phenopackets:
                return "phenopackets", "biosamples", "experiments", *field_path
            return "biosamples", "experiments", *field_path
        case ("individual", "experiment_result"):
            b = ("biosamples", "experiments", "experiment_results", *field_path)
            if force_through_phenopackets:
                return "phenopackets", *b
            return b
        #  - Biosamples -> nested
        case ("biosample", "experiment"):  # re-writing the latter to the former
            return "experiments", *field_path
        case ("biosample", "experiment_result"):
            return "experiments", "experiment_results", *field_path
        #  - Experiments -> nested
        case ("experiment", "experiment_result"):
            return "experiment_results", *field_path
        # --------------------------------------------------------------------------------------------------------------
        case ("biosample", "phenopacket"):  # re-writing the latter to the former
            # If we are accessing a biosample field through a phenopacket path, we can remap it to a biosample queryset
            # model. Otherwise, we go "backwards" out to phenopackets.
            if field_path[:1] == ("biosamples",):
                return field_path[1:]
            if field_path[:1] == ("subject",):
                if force_through_phenopackets:
                    return "phenopackets", *field_path
                else:
                    return "individual", *field_path[1:]
            return "phenopackets", *field_path
        case ("biosample", "individual"):  # re-writing the latter to the former
            if field_path[:2] == ("phenopackets", "biosamples"):
                return field_path[2:]
            elif field_path[:1] == ("biosamples",):
                return field_path[1:]
            if force_through_phenopackets:
                return "phenopackets", "subject", *field_path
            return "individual", *field_path
        case ("experiment", "biosample"):  # also handles (experiment, phenopacket) via recursion below
            # experiment: old path, prior to related_name; experiments: after
            if field_path[:1] in (
                ("experiment",),  # TODO: remove in future version
                ("experiments",),
            ):  # use slice to handle field_path == ()
                return field_path[1:]
            return "biosample", *field_path
        case ("experiment", "phenopacket"):
            # biosamples__experiment: old path, prior to related_name; biosamples__experiments: after
            if field_path[:2] in {
                ("biosamples", "experiment"),  # TODO: remove in future version
                ("biosamples", "experiments"),
            }:
                return field_path[2:]
            if (not force_through_phenopackets) and field_path[:1] == ("subject",):
                # We can skip a hop if:
                #   a) we're not forced through phenopackets, and
                #   b) we're mapping to experiment --> ... --> individual:
                return "biosample", "individual", *field_path[1:]
            if field_path[:1] == ("biosamples",):
                return "biosample", *field_path[1:]
            return "biosample", "phenopackets", *field_path
        case ("experiment", "individual"):  # re-writing the latter to the former
            # biosamples__experiment: old path, prior to related_name; biosamples__experiments: after
            if field_path[:3] in {
                ("phenopackets", "biosamples", "experiment"),  # TODO: remove in future version
                ("phenopackets", "biosamples", "experiments"),
            }:
                return field_path[3:]
            # Alternate path which skips phenopackets
            if field_path[:2] in {
                ("biosamples", "experiment"),  # TODO: remove in future version
                ("biosamples", "experiments"),
            }:
                return field_path[2:]
            if force_through_phenopackets:
                return "biosample", "phenopackets", "subject", *field_path
            # Shorter path than going through phenopackets, although this might lead to wacky results if not all
            # individuals are part of phenopackets.
            return "biosample", "individual", *field_path
        case ("experiment_result", "phenopacket"):
            # biosamples__experiment: old path, prior to related_name; biosamples__experiments: after
            if field_path[:3] in {
                ("biosamples", "experiment", "experiment_results"),  # TODO: remove in future version
                ("biosamples", "experiments", "experiment_results"),
            }:
                return field_path[3:]
            if (not force_through_phenopackets) and field_path[:1] == ("subject",):
                return "experiments", "biosample", "individual", *field_path[1:]
            return "experiments", "biosample", "phenopackets", *field_path
        case ("experiment_result", "individual"):
            # biosamples__experiment: old path, prior to related_name; biosamples__experiments: after
            if field_path[:4] in {
                ("phenopackets", "biosamples", "experiment", "experiment_results"),  # TODO: remove in future version
                ("phenopackets", "biosamples", "experiments", "experiment_results"),
            }:
                return field_path[4:]
            # Alternate path which skips phenopackets
            if not force_through_phenopackets and field_path[:3] in {
                ("biosamples", "experiment", "experiment_results"),  # TODO: remove in future version
                ("biosamples", "experiments", "experiment_results"),
            }:
                return field_path[3:]
            if force_through_phenopackets:
                return "experiments", "biosample", "phenopackets", "subject", *field_path
            return "experiments", "biosample", "individual", *field_path
        case ("experiment_result", "biosample"):
            # experiment: old path, prior to related_name; experiments: after
            if field_path[:2] in {
                ("experiment", "experiment_results"),  # TODO: remove in future version
                ("experiments", "experiment_results"),
            }:
                return field_path[2:]
            return "experiments", "biosample", *field_path
        case ("experiment_result", "experiment"):
            if field_path[:1] == ("experiment_results",):
                return field_path[1:]
            return "experiments", *field_path
        # --------------------------------------------------------------------------------------------------------------
        case _:
            raise exc


def _resolve_filter_mapping_to_queryset_model_inner(
    queryset_entity: DiscoveryEntity,
    field_entity: DiscoveryEntity,
    field_path: tuple[str, ...],
    force_through_phenopackets: bool,
) -> tuple[str, ...]:
    """
    Small wrapper around _resolve_filter_mapping_to_queryset_model_inner_2, to basically repeatedly simplify the
    resolved path until we have the smallest form we can achieve (useful only for edge cases where we might go, e.g.,
    from phenopackets -> biosamples -> phenopackets -> biosamples -> sampled_tissue
    to phenopackets -> biosamples -> sampled_tissue.)
    """
    res = _resolve_filter_mapping_to_queryset_model_inner_2(
        queryset_entity, field_entity, field_path, force_through_phenopackets
    )

    # While our resolved path is still getting shorter, keep running the inner function to simplify it. This should
    # usually just run 0-1 times.
    while (
        len(res) >
        len(res2 := _resolve_filter_mapping_to_queryset_model_inner_2(
            queryset_entity, queryset_entity, res, force_through_phenopackets
        ))
    ):
        res = res2

    return res


def resolve_filter_mapping_to_queryset_model(
    queryset_entity: DiscoveryEntity,
    field_entity: DiscoveryEntity,
    field_path: tuple[str, ...],
    force_through_phenopackets: bool = False,
) -> str:
    """
    Given a goal (queryset) model name and a current (field) model name, rewrite a path to a field from the field model
    name to the goal queryset model name and convert it to a Django-query-form field path.
    IMPORTANT NOTE: This hard-codes model relationships, e.g., experiments inside biosamples inside phenopackets.
                    The "hard-coded" data model here is equivalent of the old "linked field set" concept, which was very
                    over-generalized.
    """
    return field_path_to_django_mapping(
        _resolve_filter_mapping_to_queryset_model_inner(
            queryset_entity, field_entity, field_path, force_through_phenopackets
        )
    )


def normalize_field_path_true_model(
    entity_name: DiscoveryEntity, field_path: tuple[str, ...]
) -> tuple[DiscoveryEntity, tuple[str, ...]]:
    """
    Normalizes a discovery entity/field access to its simplest form, letting us know which discovery entity is truly
    being filtered. This also lets us correctly check any permissions for data types later...
    (which itself is quite a janky system).
    """

    match (entity_name, field_path):
        # We employ some recursion to progressively further normalize to a simpler form until we cannot anymore.
        case ("individual", ("phenopackets", *rest)):
            return normalize_field_path_true_model("phenopacket", tuple(rest))
        case ("individual", ("biosamples", *rest)):
            # NOTE: this is a non-standard access pattern, but still works as of the time of writing (2025-09-03)
            # because of the way the Django relationships are set up.
            return normalize_field_path_true_model("biosample", tuple(rest))
        case ("phenopacket", ("subject", *rest)):
            return normalize_field_path_true_model("individual", tuple(rest))
        case ("phenopacket", ("biosamples", *rest)):
            return normalize_field_path_true_model("biosample", tuple(rest))
        case ("biosample", ("phenopackets", *rest)):
            return normalize_field_path_true_model("phenopacket", tuple(rest))
        case ("biosample", ("individual", *rest)):
            return normalize_field_path_true_model("individual", tuple(rest))
        # TODO: remove old experiment path in a future version:
        case ("biosample", ("experiment" | "experiments", *rest)):  # "experiment" is old name, "experiments" is new
            return normalize_field_path_true_model("experiment", tuple(rest))
        case ("experiment", ("biosamples", *rest)):
            return normalize_field_path_true_model("biosample", tuple(rest))
        case ("experiment", ("experiment_results", *rest)):
            return normalize_field_path_true_model("experiment_result", tuple(rest))
        case ("experiment_result", ("experiments", *rest)):
            return normalize_field_path_true_model("experiment", tuple(rest))
        case _:  # base case; nothing to do
            return entity_name, field_path


@dataclass
class DiscoveryFieldSubquery:
    """
    Data class representing a spec for executing an Exists(...) subquery across a many-to-many or many-to-one Django
    relation boundary.
    """
    queryset: QuerySet  # queryset for inner Exists
    inner_field: str  # queried field, rewritten for the inner queryset
    related_field: str


def get_field_django_mapping_and_queried_entity(
    queryset_entity: DiscoveryEntity, field_props: AnyFieldDefinition, force_through_phenopackets: bool = False
) -> tuple[str, DiscoveryFieldSubquery | None, DiscoveryEntity]:
    """
    Parses a path-like string representing an ORM such as "individual/extra_properties/date_of_consent"
    where the first crumb represents the object in the DB model, and the next ones
    are the field with their possible joins through tables relations.
    Returns a tuple of (
        the Django string representation of the field for this object relative to the queryset entity,
        a specification for executing an Exists(...) subqueyr IF crossing a many-to-many or many-to-one boundary,
        the queried entity name,
    )
    Can raise django.core.exceptions.FieldDoesNotExist if the field mapping does not correspond to a real model field.
    """

    entity_name, field_path = normalize_field_path_true_model(*field_props.get_entity_and_field_path())

    model: Type[BaseScopeableModel] | None = DISCOVERY_ENTITY_NAMES_TO_MODEL.get(entity_name)
    if model is None:
        msg = f"Accessing field on model {entity_name} not implemented"
        raise NotImplementedError(msg)

    resolved_field_path = _resolve_filter_mapping_to_queryset_model_inner(
        queryset_entity, entity_name, field_path, force_through_phenopackets
    )

    subquery: DiscoveryFieldSubquery | None = None

    if field_path:
        field_obj = DISCOVERY_ENTITY_NAMES_TO_MODEL[queryset_entity]._meta.get_field(resolved_field_path[0])
        # If we have a many-to-many field or a many-to-one (from a foreign key) relationship, we need to do filtering
        # based on an Exists subquery rather than an inner join, since the latter prevents us from getting correct
        # counts/stats (Django executes an inner join even when we don't want one, basically).
        # For example, instead of getting the counts for ALL diseases with phenopackets that have "breast cancer" as a
        # disease (i.e., a distribution with the *other* diseases breast cancer patients may have as well), we ONLY get
        # inner-joined records for matching Disease models if we do this naively, when instead we want what was
        # described: all disease counts for phenopackets with breast cancer.
        # To solve this, we do an Exists subquery to check if we have at least one matching object from the other side
        # of the m2m/many-to-one relation which matches the field query (which as been rewritten to be valid for
        # the model referred to in the relation rather than the queryset model.)
        if isinstance(field_obj, ManyToManyField | ManyToOneRel):
            if isinstance(field_obj, ManyToManyField):
                rel = field_obj.remote_field.accessor_name
            else:  # isinstance(field_obj, ManyToOneRel)
                rel = field_obj.field.name
            subquery = DiscoveryFieldSubquery(
                queryset=field_obj.related_model.objects.all(),
                inner_field=field_path_to_django_mapping(resolved_field_path[1:]),
                related_field=rel,
            )

    return field_path_to_django_mapping(resolved_field_path), subquery, entity_name


def get_field_django_mapping(queryset_entity: DiscoveryEntity, field_props: AnyFieldDefinition) -> str:
    """
    Parses a path-like string representing an ORM such as "individual/extra_properties/date_of_consent"
    where the first crumb represents the object in the DB model, and the next ones
    are the field with their possible joins through tables relations.
    Returns the Django string representation of the field for this object.
    """
    return get_field_django_mapping_and_queried_entity(queryset_entity, field_props)[0]


def parse_duration(duration: str | dict):
    """ Returns years integer. """
    if isinstance(duration, dict) and "iso8601duration" in duration:
        duration = duration["iso8601duration"]
    string = duration.split('P')[-1]
    return int(float(string.split('Y')[0]))


def parse_individual_age(age_obj: dict) -> int:
    """ Parses two possible age representations and returns average age or age as integer. """

    if "age_range" in age_obj:
        age_obj = age_obj["age_range"]
        start_age = parse_duration(age_obj["start"]["age"]["iso8601duration"])
        end_age = parse_duration(age_obj["end"]["age"]["iso8601duration"])
        # for the duration calculate the average age
        return (start_age + end_age) // 2

    if "age" in age_obj:
        return parse_duration(age_obj["age"]["iso8601duration"])

    raise ValueError(f"Error: {age_obj} format not supported")


def labelled_range_generator(
    field_props: NumberFieldDefinition
) -> Iterator[tuple[int | float | None, int | float | None, str]]:
    """
    Returns a generator yielding floor, ceil and label value for each bin from
    a numeric field configuration
    """

    cfg = field_props.config

    if isinstance(cfg, ManualBinsNumberFieldConfig):
        return custom_binning_generator(cfg)

    return auto_binning_generator(cfg)


def custom_binning_generator(
    c: ManualBinsNumberFieldConfig
) -> Iterator[tuple[int | float | None, int | float | None, str]]:
    """
    Generator for custom bins. It expects an array of bin boundaries (`bins` property)
    `minimum` and `maximum` properties are optional. When absent, there is no lower/upper
    bound and the corresponding bin limit is open-ended (as in "< 5").
    If present but equal to the closest bin boundary, there is no open-ended bin.
    If present but different from the closest bin, an extra bin is added to collect
    all values down/up to the min/max value that is set (open-ended without limit)
    For example, given the following configuration:
    {
        minimum: 0,
        bins: [2, 4, 8]
    }
    the first bin will be labelled "<2" and contain only values between 0-2
    while the last bin will be labelled "≥ 8" and contain any value greater than
    or equal to 8.
    """

    # Minimum/maximum/bins are validated with a function in the definition for ManualBinsNumberFieldConfig

    # Start of generator: bin of [minimum, bins[0]) or [-infinity, bins[0])
    if c.minimum is None or c.minimum != c.bins[0]:
        yield c.minimum, c.bins[0], f"< {c.bins[0]}"

    # Generate interstitial bins for the range.
    # range() is semi-open: [1, len(bins))
    # – so in terms of indices, we skip the first bin (we access it via i-1 for lhs)
    #   and generate [lhs, rhs) pairs for each pair of bins until the end.
    # Values beyond the last bin gets handled separately.
    for i in range(1, len(c.bins)):
        lhs = c.bins[i - 1]
        rhs = c.bins[i]
        yield lhs, rhs, f"[{lhs}, {rhs})"

    # Then, handle values beyond the value of the last bin: [bins[-1], maximum) or [bins[-1], infinity)
    if c.maximum is None or c.maximum != c.bins[-1]:
        yield c.bins[-1], c.maximum, f"≥ {c.bins[-1]}"


def auto_binning_generator(c: AutoBinsNumberFieldConfig) -> Iterator[tuple[int, int, str]]:
    """
    Note: limited to operations on integer values for simplicity.
    A word of caution: when implementing handling of floating point values,
    be aware of lack of support for ranges.
    """

    # Error checking / validation is handled by Pydantic in bento_lib.
    # We have the following guarantees:
    #  * c.minimum <= c.maximum
    #  * none of the following: c.taper_right < c.taper_left or c.minimum > c.taper_left or c.taper_right > c.maximum
    #  * (c.taper_right - c.taper_left) % c.bin_size == 0

    if c.minimum != c.taper_left:
        yield c.minimum, c.taper_left, f"< {c.taper_left}"

    for v in range(c.taper_left, c.taper_right, c.bin_size):
        yield v, v + c.bin_size, f"[{v}, {v + c.bin_size})"

    if c.maximum != c.taper_right:
        yield c.taper_right, c.maximum, f"≥ {c.taper_right}"


def monthly_generator(start: str, end: str) -> Iterator[tuple[int, int]]:
    """
    generator of tuples (year nb, month nb) from a start date to an end date
    as ISO formated strings `yyyy-mm`
    """
    [start_year, start_month] = [int(k) for k in start.split("-")]
    [end_year, end_month] = [int(k) for k in end.split("-")]
    last_month_nb = (end_year - start_year) * 12 + end_month
    for month_nb in range(start_month, last_month_nb + 1):
        year = start_year + (month_nb - 1) // 12
        month = month_nb % 12 or 12
        yield year, month


def mapping_to_json_path(mapping: str) -> str:
    return JSON_PATH_ACCESSOR.join(mapping.split(MAPPING_SEPARATOR))


def get_nested_json_condition(path: str, value: Any) -> dict[str, Any]:
    """
    Takes a '/' delimited path and creates an array filter condition for JSONFields.
    e.g. with:
    path="assay/label" and value="something"
    returns {
        "assay": {
            "label": "something"
        }
    }
    """
    elements = path.split(MAPPING_SEPARATOR)
    condition = value
    for field in reversed(elements):
        condition = {field: condition}
    return condition


def get_json_range_condition(
    filtering_entity: DiscoveryEntity, field_props: AnyFieldDefinition, min: int = None, max: int = None
) -> Q:
    """
    Takes field props for a 'number' data type contained in a JSONField array,
    and returns a query expression for the provided 'min' and 'max' values.

    Note: since Django doesn't support index-agnostic lookups for JSONField array elements,
    we rely on the 'jsonb_path_exists' PostgreSQL function to perform element-wise filtering
    on array elements that satisfy the range and 'group_by_value' field prop condition.

    e.g. To get measurements where assay.id == "NCIT:C16358" AND value.quantity.value < 20 (BMIs bellow 20),
    the JSON path with conditions would be:
        '$[*] ? (@.value.quantity.value < 20 && @.assay.id == "NCIT:C16358")'
    """

    group_by = field_props.group_by
    group_by_value = field_props.group_by_value
    value_mapping = field_props.value_mapping

    range_condition = Q()

    if group_by and group_by_value and value_mapping:
        field = get_field_django_mapping(filtering_entity, field_props)
        group_by_json_path = mapping_to_json_path(group_by)
        value_json_path = mapping_to_json_path(value_mapping)
        if min is not None:
            min_condition = Q(JSONBPathFilter(
                # Points to the JSONField
                F(field),
                # JSON path expression with GTE and group_by_value condition
                Value(f'$[*] ? (@.{value_json_path} >= {min} && @.{group_by_json_path} == "{group_by_value}")')
            ))
            range_condition.add(min_condition, conn_type=Q.AND)
        if max is not None:
            max_condition = Q(JSONBPathFilter(
                # Points to the JSONField
                F(field),
                # JSON path expression with LT and group_by_value condition
                Value(f'$[*] ? (@.{value_json_path} < {max} && @.{group_by_json_path} == "{group_by_value}")')
            ))
            range_condition.add(max_condition, Q.AND)

    return range_condition
