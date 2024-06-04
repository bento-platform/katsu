from typing import Any, Iterator, Type
from django.db.models import Q, Func, BooleanField, F, Value, Model, JSONField

from chord_metadata_service.discovery.model_lookups import PUBLIC_MODEL_NAMES_TO_MODEL, PublicModelNames

MAPPING_SEPARATOR = "/"
JSON_PATH_ACCESSOR = "."


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


def get_public_model_name_and_field_path(field_id: str) -> tuple[str, tuple[str, ...]]:
    model_name, *field_path = field_id.split("/")
    return model_name, tuple(field_path)


def get_model_and_field(field_id: str) -> tuple[Type[Model], str]:
    """
    Parses a path-like string representing an ORM such as "individual/extra_properties/date_of_consent"
    where the first crumb represents the object in the DB model, and the next ones
    are the field with their possible joins through tables relations.
    Returns a tuple of the model object and the Django string representation of the
    field for this object.
    """

    model_name, field_path = get_public_model_name_and_field_path(field_id)

    model: Type[Model] | None = PUBLIC_MODEL_NAMES_TO_MODEL.get(model_name)
    if model is None:
        msg = f"Accessing field on model {model_name} not implemented"
        raise NotImplementedError(msg)

    field_name = "__".join(field_path)
    return model, field_name


def get_public_model_name(model: Type[Model]) -> PublicModelNames:
    model_name = [key for key, m in PUBLIC_MODEL_NAMES_TO_MODEL.items() if m == model]
    if len(model_name) != 1:
        raise ValueError(f"Provided model {model} is not available for public.")
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


def labelled_range_generator(field_props: dict) -> Iterator[tuple[int, int, str]]:
    """
    Returns a generator yielding floor, ceil and label value for each bin from
    a numeric field configuration
    """

    if "bins" in field_props["config"]:
        return custom_binning_generator(field_props)

    return auto_binning_generator(field_props)


def custom_binning_generator(field_props: dict) -> Iterator[tuple[int, int, str]]:
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

    c = field_props["config"]
    minimum: int | None = int(c["minimum"]) if "minimum" in c else None
    maximum: int | None = int(c["maximum"]) if "maximum" in c else None
    bins: list[int] = [int(value) for value in c["bins"]]

    # check prerequisites
    # Note: it raises an error as it reflects an error in the config file
    if maximum is not None and minimum is not None and maximum < minimum:
        raise ValueError(f"Wrong min/max values in config: {field_props}")

    if minimum is not None and minimum > bins[0]:
        raise ValueError(f"Min value in config is greater than first bin: {field_props}")

    if maximum is not None and maximum < bins[-1]:
        raise ValueError(f"Max value in config is lower than last bin: {field_props}")

    if len(bins) < 2:
        raise ValueError(f"Error in bins value. At least 2 values required for defining a single bin: {field_props}")

    # Start of generator: bin of [minimum, bins[0]) or [-infinity, bins[0])
    if minimum is None or minimum != bins[0]:
        yield minimum, bins[0], f"< {bins[0]}"

    # Generate interstitial bins for the range.
    # range() is semi-open: [1, len(bins))
    # – so in terms of indices, we skip the first bin (we access it via i-1 for lhs)
    #   and generate [lhs, rhs) pairs for each pair of bins until the end.
    # Values beyond the last bin gets handled separately.
    for i in range(1, len(bins)):
        lhs = bins[i - 1]
        rhs = bins[i]
        yield lhs, rhs, f"[{lhs}, {rhs})"

    # Then, handle values beyond the value of the last bin: [bins[-1], maximum) or [bins[-1], infinity)
    if maximum is None or maximum != bins[-1]:
        yield bins[-1], maximum, f"≥ {bins[-1]}"


def auto_binning_generator(field_props) -> Iterator[tuple[int, int, str]]:
    """
    Note: limited to operations on integer values for simplicity
    A word of caution: when implementing handling of floating point values,
    be aware of string format (might need to add precision to config?) computations
    of modulo and lack of support for ranges.
    """

    c = field_props["config"]

    minimum = int(c["minimum"])
    maximum = int(c["maximum"])
    taper_left = int(c["taper_left"])
    taper_right = int(c["taper_right"])
    bin_size = int(c["bin_size"])

    # check prerequisites
    # Note: it raises an error as it reflects an error in the config file
    if maximum < minimum:
        raise ValueError(f"Wrong min/max values in config: {field_props}")

    if (taper_right < taper_left
            or minimum > taper_left
            or taper_right > maximum):
        raise ValueError(f"Wrong taper values in config: {field_props}")

    if (taper_right - taper_left) % bin_size:
        raise ValueError(f"Range between taper values is not a multiple of bin_size: {field_props}")

    # start generator
    if minimum != taper_left:
        yield minimum, taper_left, f"< {taper_left}"

    for v in range(taper_left, taper_right, bin_size):
        yield v, v + bin_size, f"[{v}, {v + bin_size})"

    if maximum != taper_right:
        yield taper_right, maximum, f"≥ {taper_right}"


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


def get_json_range_condition(field_props: dict, min: int = None, max: int = None) -> Q:
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
    group_by = field_props.get("group_by")
    group_by_value = field_props.get("group_by_value")
    value_mapping = field_props.get("value_mapping")
    range_condition = Q()
    if group_by and group_by_value and value_mapping:
        _, field = get_model_and_field(field_props["mapping"])
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
