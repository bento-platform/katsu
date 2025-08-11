from bento_lib.discovery import (
    StringFieldDefinition, NumberFieldDefinition, DateFieldDefinition, FieldDefinition, DiscoveryEntity
)
from bento_lib.discovery.models.fields import ManualBinsNumberFieldConfig, AutoBinsNumberFieldConfig
from typing import Any, Iterator, Type, TypeAlias
from django.db.models import Q, Func, BooleanField, F, Value, Model, JSONField

from .exceptions import DiscoveryFilterRewriteException
from .model_lookups import DISCOVERY_ENTITY_NAMES_TO_MODEL
from .scopeable_model import BaseScopeableModel

MAPPING_SEPARATOR = "/"
JSON_PATH_ACCESSOR = "."

AnyFieldDefinition: TypeAlias = FieldDefinition | NumberFieldDefinition | StringFieldDefinition | DateFieldDefinition


class JSONBPathFilter(Func):
    function = "jsonb_path_exists"
    output_field = BooleanField()


class JSONBPathQuery(Func):
    function = "jsonb_path_query"
    output_field = JSONField()


def get_jsonb_path_query(field: str, json_path: str, is_array=True, is_mapping=True):
    field_operator = "$[*]" if is_array else "$"
    query_path = mapping_to_json_path(json_path) if is_mapping else json_path
    return JSONBPathQuery(F(field), Value(f"{field_operator}.{query_path}"))


# noinspection PyUnreachableCode
def _resolve_filter_mapping_to_queryset_model_inner(
    queryset_model_name: DiscoveryEntity, field_model_name: DiscoveryEntity, field_path: tuple[str, ...]
) -> tuple[str, ...]:
    """
    Given a goal (queryset) model name and a current (field) model name, rewrite a path to a field from the field model
    name to the goal queryset model name.
    Currently, this is used as an inner function for resolve_filter_mapping_to_queryset_model, but may have more broad
    use for rewriting field paths without converting them to Django form.
    """

    if queryset_model_name == field_model_name:
        return field_path

    exc = DiscoveryFilterRewriteException(
        f"cannot map field model {field_model_name} to filtering model {queryset_model_name}"
    )

    match (queryset_model_name, field_model_name):
        #  - Phenopackets <-> Individuals
        case ("individual", "phenopacket"):
            if field_path[:1] == ("subject",):  # also conveniently handles the falsey case of field_path == ()
                return field_path[1:]
            return "phenopackets", *field_path
        case ("phenopacket", "individual"):
            if field_path[:1] == ("phenopackets",):  # also conveniently handles the falsey case of field_path == ()
                return field_path[1:]
            return "subject", *field_path
        #  - Phenopackets -> nested
        case ("phenopacket", "biosample"):
            return "biosamples", *field_path
        case ("phenopacket", "experiment"):
            return "biosamples", "experiments", *field_path
        case ("phenopacket", "experiment_result"):
            return "biosamples", "experiments", "experiment_results", *field_path
        #  - Individuals -> nested
        case ("individual", "biosample"):
            return "phenopackets", "biosamples", *field_path
        case ("individual", "experiment"):
            return "phenopackets", "biosamples", "experiments", *field_path
        case ("individual", "experiment_result"):
            return "phenopackets", "biosamples", "experiments", "experiment_results", *field_path
        #  - Biosamples -> nested
        case ("biosample", "experiment"):
            return "experiments", *field_path
        case ("biosample", "experiment_result"):
            return "experiments", "experiment_results", *field_path
        #  - Experiments -> nested
        case ("experiment", "experiment_result"):
            return "experiment_results", *field_path
        # --------------------------------------------------------------------------------------------------------------
        case ("biosample", "phenopacket"):
            # If we are accessing a biosample field through a phenopacket path, we can remap it to a biosample queryset
            # model. Otherwise, we cannot and we raise the exception.
            if field_path[0] == "biosamples":
                return field_path[1:]
            raise exc
        case ("biosample", "individual"):
            if field_path[:2] == ("phenopackets", "biosamples"):
                return field_path[2:]
            raise exc
        case ("experiment", "biosample"):  # also handles (experiment, phenopacket) via recursion below
            # experiment: old path, prior to related_name; experiments: after
            if field_path[:1] in (("experiment",), ("experiments",)):  # use slice to handle field_path == ()
                return field_path[1:]
            raise exc
        case ("experiment", "phenopacket"):
            # biosamples__experiment: old path, prior to related_name; biosamples__experiments: after
            if field_path[:2] in {("biosamples", "experiment"), ("biosamples", "experiments")}:
                return field_path[2:]
            raise exc
        case ("experiment", "individual"):
            # biosamples__experiment: old path, prior to related_name; biosamples__experiments: after
            if field_path[:3] in {
                ("phenopackets", "biosamples", "experiment"),
                ("phenopackets", "biosamples", "experiments"),
            }:
                return field_path[3:]
            raise exc
        case ("experiment_result", "phenopacket"):
            if field_path[:3] == ("biosamples", "experiments", "experiment_results"):
                return field_path[3:]
            raise exc
        case ("experiment_result", "individual"):
            if field_path[:4] == ("phenopackets", "biosamples", "experiments", "experiment_results"):
                return field_path[4:]
            raise exc
        case ("experiment_result", "biosample"):
            if field_path[:2] == ("experiments", "experiment_result"):
                return field_path[2:]
            raise exc
        case ("experiment_result", "experiment"):
            if field_path[0] == "experiment_result":
                return field_path[1:]
            raise exc
        # --------------------------------------------------------------------------------------------------------------
        case _:
            raise exc


def resolve_filter_mapping_to_queryset_model(
    queryset_model_name: DiscoveryEntity, field_model_name: DiscoveryEntity, field_path: tuple[str, ...]
) -> str:
    """
    Given a goal (queryset) model name and a current (field) model name, rewrite a path to a field from the field model
    name to the goal queryset model name and convert it to a Django-query-form field path.
    IMPORTANT NOTE: This hard-codes model relationships, e.g., experiments inside biosamples inside phenopackets.
                    The "hard-coded" data model here is equivalent of the old "linked field set" concept, which was very
                    over-generalized.
    """
    return "__".join(_resolve_filter_mapping_to_queryset_model_inner(queryset_model_name, field_model_name, field_path))


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
        case ("phenopacket", ("subject", *rest)):
            return normalize_field_path_true_model("individual", tuple(rest))
        case ("phenopacket", ("biosamples", *rest)):
            return normalize_field_path_true_model("biosample", tuple(rest))
        case ("biosample", ("experiments", *rest)):
            return normalize_field_path_true_model("experiment", tuple(rest))
        case ("experiment", ("experiment_results", *rest)):
            return normalize_field_path_true_model("experiment_result", tuple(rest))
        case _:  # base case; nothing to do
            return entity_name, field_path


def get_field_django_mapping_and_queried_entity(
    queryset_model_name: DiscoveryEntity, field_props: AnyFieldDefinition
) -> tuple[str, DiscoveryEntity]:
    """
    Parses a path-like string representing an ORM such as "individual/extra_properties/date_of_consent"
    where the first crumb represents the object in the DB model, and the next ones
    are the field with their possible joins through tables relations.
    Returns a tuple of (
        the Django string representation of the field for this object relative to the queryset entity,
        the queried entity name,
    )
    """

    entity_name, field_path = normalize_field_path_true_model(*field_props.get_entity_and_field_path())

    model: Type[BaseScopeableModel] | None = DISCOVERY_ENTITY_NAMES_TO_MODEL.get(entity_name)
    if model is None:
        msg = f"Accessing field on model {entity_name} not implemented"
        raise NotImplementedError(msg)

    return resolve_filter_mapping_to_queryset_model(queryset_model_name, entity_name, field_path), entity_name


def get_field_django_mapping(queryset_model_name: DiscoveryEntity, field_props: AnyFieldDefinition) -> str:
    """
    Parses a path-like string representing an ORM such as "individual/extra_properties/date_of_consent"
    where the first crumb represents the object in the DB model, and the next ones
    are the field with their possible joins through tables relations.
    Returns the Django string representation of the field for this object.
    """
    return get_field_django_mapping_and_queried_entity(queryset_model_name, field_props)[0]


def get_public_model_name(model: Type[Model]) -> DiscoveryEntity:
    model_name = [key for key, m in DISCOVERY_ENTITY_NAMES_TO_MODEL.items() if m == model]
    if len(model_name) != 1:
        raise NotImplementedError(f"Provided model {model} is not available for public.")
    return model_name[0]


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
    filtering_model_name: DiscoveryEntity, field_props: AnyFieldDefinition, min: int = None, max: int = None
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
        field = get_field_django_mapping(filtering_model_name, field_props)
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
