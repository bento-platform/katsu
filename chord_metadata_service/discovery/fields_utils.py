from bento_lib.discovery import DateFieldDefinition, NumberFieldDefinition, DiscoveryEntity
from bento_lib.discovery.models.fields import ManualBinsNumberFieldConfig, AutoBinsNumberFieldConfig
from typing import Any, Iterator, Literal
from django.db.models import Q, Func, BooleanField, F, Value, JSONField

from .field_paths.django_field_query import get_field_django_mapping
from .types import AnyFieldDefinition

__all__ = [
    "MAPPING_SEPARATOR",
    "JSON_PATH_ACCESSOR",
    "JSONBPathFilter",
    "get_jsonb_path_query",
    "parse_individual_age",
    "labelled_number_range_generator",
    "labelled_date_range_generator_by_month",
    "labelled_date_range_generator_by_year",
    "labelled_date_range_generator",
    "get_nested_json_condition",
    "get_json_op_condition",
    "get_json_range_condition",
    "str_to_numeric",
]

MAPPING_SEPARATOR = "/"
JSON_PATH_ACCESSOR = "."

OP_GTE: Literal[">="] = ">="
OP_GT: Literal[">"] = ">"
OP_EQ: Literal["="] = "="
OP_LT: Literal["<"] = "<"
OP_LTE: Literal["<="] = "<="


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


def parse_duration(duration: str | dict):
    """Returns years integer."""
    if isinstance(duration, dict) and "iso8601duration" in duration:
        duration = duration["iso8601duration"]
    string = duration.split("P")[-1]
    return int(float(string.split("Y")[0]))


def parse_individual_age(age_obj: dict) -> int:
    """Parses two possible age representations and returns average age or age as integer."""

    if "age_range" in age_obj:
        age_obj = age_obj["age_range"]
        start_age = parse_duration(age_obj["start"]["age"]["iso8601duration"])
        end_age = parse_duration(age_obj["end"]["age"]["iso8601duration"])
        # for the duration calculate the average age
        return (start_age + end_age) // 2

    if "age" in age_obj:
        return parse_duration(age_obj["age"]["iso8601duration"])

    raise ValueError(f"Error: {age_obj} format not supported")


def labelled_number_range_generator(
    field_props: NumberFieldDefinition,
) -> Iterator[tuple[int | float | None, int | float | None, str]]:
    """
    Returns a generator yielding floor, ceil and label value for each bin from a numeric field configuration.
    """

    cfg = field_props.config

    if isinstance(cfg, ManualBinsNumberFieldConfig):
        return custom_binning_generator(cfg)

    return auto_binning_generator(cfg)


def custom_binning_generator(
    c: ManualBinsNumberFieldConfig,
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


def auto_binning_generator(c: AutoBinsNumberFieldConfig) -> Iterator[tuple[int | None, int | None, str]]:
    """
    Note: limited to operations on integer values for simplicity.
    A word of caution: when implementing handling of floating point values,
    be aware of lack of support for ranges.
    """

    # Error checking / validation is handled by Pydantic in bento_lib.
    # We have the following guarantees:
    #  * c.minimum <= c.maximum where both exist
    #  * none of the following: c.taper_right < c.taper_left or c.minimum > c.taper_left or c.taper_right > c.maximum
    #  * (c.taper_right - c.taper_left) % c.bin_size == 0

    if c.minimum is None or c.minimum != c.taper_left:
        yield c.minimum, c.taper_left, f"< {c.taper_left}"

    for v in range(c.taper_left, c.taper_right, c.bin_size):
        yield v, v + c.bin_size, f"[{v}, {v + c.bin_size})"

    if c.maximum is None or c.maximum != c.taper_right:
        yield c.taper_right, c.maximum, f"≥ {c.taper_right}"


def _year_month_from_month_offset(start_year: int, month_offset: int) -> tuple[int, int]:
    """
    Given a starting year and a 0-indexed month offset from the starting year, return a year and a (1-indexed) month.
    """
    return start_year + month_offset // 12, (month_offset + 1) % 12 or 12


def labelled_date_range_generator_by_month(start: str | None, end: str | None) -> Iterator[tuple[str, str, str]]:
    """
    Returns a generator yielding floor, ceil and label value for each bin from a date field configuration,
    binning by month given starting/ending months. The label is the machine-readable "yyyy-mm" value of the bin
    (equal to the floor) - it is up to the API consumer to format it for display (e.g., as "Jan 2021").
    """

    if start is None or end is None:
        yield from ()
        return

    [start_year, start_month] = [int(k) for k in start.split("-")][:2]
    [end_year, end_month] = [int(k) for k in end.split("-")][:2]
    last_month_nb = (end_year - start_year) * 12 + end_month
    for month_offset in range(start_month - 1, last_month_nb):
        gte_year, gte_month = _year_month_from_month_offset(start_year, month_offset)
        lt_year, lt_month = _year_month_from_month_offset(start_year, month_offset + 1)
        floor = f"{gte_year}-{gte_month:02d}"
        ceil = f"{lt_year}-{lt_month:02d}"
        yield floor, ceil, floor


def labelled_date_range_generator_by_year(start: str | None, end: str | None) -> Iterator[tuple[str, str, str]]:
    """
    Returns a generator yielding floor, ceil and label value for each bin from a date field configuration,
    binning by year given starting/ending years.
    """

    if start is None or end is None:
        yield from ()
        return

    start_year = int(start)
    end_year = int(end)

    for year in range(start_year, end_year + 1):
        yield f"{year}", f"{year + 1}", f"{year}"


def labelled_date_range_generator(
    field_props: DateFieldDefinition, start: str | None, end: str | None
) -> Iterator[tuple[str, str, str]]:
    """
    Returns a generator yielding floor, ceil and label value for each bin from a date field configuration.
    """

    match field_props.config.bin_by:
        case "month":
            return labelled_date_range_generator_by_month(start, end)
        case "year":
            return labelled_date_range_generator_by_year(start, end)
        case _:  # pragma: no cover
            raise NotImplementedError()


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


def get_json_op_condition(
    filtering_entity: DiscoveryEntity,
    field_props: AnyFieldDefinition,
    op: Literal["<=", "<", "=", ">", ">="],
    value: str | int | float,
) -> Q:
    """
    Takes field props for a field contained in a JSONField array, and returns a query expression for the provided
    comparison operator and value.

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

    if not group_by or not group_by_value or not value_mapping:
        return Q()

    field = get_field_django_mapping(filtering_entity, field_props)
    group_by_json_path = mapping_to_json_path(group_by)
    value_json_path = mapping_to_json_path(value_mapping)

    return Q(
        JSONBPathFilter(
            # Points to the JSONField
            F(field),
            # JSON path expression with operator on field we're interested in and group_by_value condition
            Value(f'$[*] ? (@.{value_json_path} {op} {value} && @.{group_by_json_path} == "{group_by_value}")'),
        )
    )


def get_json_range_condition(
    filtering_entity: DiscoveryEntity,
    field_props: AnyFieldDefinition,
    *,
    min_value: int | float | str | None = None,
    min_inclusive: bool = True,
    max_value: int | float | str | None = None,
    max_inclusive: bool = True,
) -> Q:
    """
    Takes field props for a 'number' or 'date' data type contained in a JSONField array,
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
        if min_value is not None:
            range_condition &= get_json_op_condition(
                filtering_entity, field_props, op=OP_GTE if min_inclusive else OP_GT, value=min_value
            )
        if max_value is not None:
            range_condition &= get_json_op_condition(
                filtering_entity, field_props, op=OP_LTE if max_inclusive else OP_LT, value=max_value
            )

    return range_condition


def str_to_numeric(value: str) -> int | float:
    return float(value) if "." in value else int(value)
