from __future__ import annotations

import isodate
import datetime

from collections import defaultdict, Counter
from calendar import month_abbr
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Any, Optional, Type, TypedDict, Mapping, Generator

from django.db.models import Count, F, Func, IntegerField, CharField, Case, Model, When, Value
from django.db.models.functions import Cast
from django.conf import settings

from chord_metadata_service.phenopackets import models as pheno_models
from chord_metadata_service.experiments import models as experiments_models
from chord_metadata_service.logger import logger


LENGTH_Y_M = 4 + 1 + 2  # dates stored as yyyy-mm-dd

MODEL_NAMES_TO_MODEL: dict[str, Type[Model]] = {
    "individual": pheno_models.Individual,
    "experiment": experiments_models.Experiment,
    "biosample": pheno_models.Biosample,
}

COMPUTED_PROPERTY_PREFIX = "__"


class BinWithValue(TypedDict):
    label: str
    value: int


def get_threshold() -> int:
    """
    Gets the maximum count threshold for hiding censored data (i.e., rounding to 0).
    This is a function to prevent settings errors if not running/importing this file in a Django context.
    """
    return settings.CONFIG_PUBLIC["rules"]["count_threshold"]


def camel_case_field_names(string) -> str:
    """ Function to convert snake_case field names to camelCase """
    # Capitalize every part except the first
    return "".join(
        part.title() if i > 0 else part
        for i, part in enumerate(string.split("_"))
    )


# TODO: Typing: generics
def transform_keys(obj: Any) -> Any:
    """
    The function validates against DATS schemas that use camelCase.
    It iterates over a dict and changes all keys in nested objects to camelCase.
    """

    if isinstance(obj, list):
        return [transform_keys(i) for i in obj]

    if isinstance(obj, dict):
        return {
            camel_case_field_names(key): transform_keys(value)
            for key, value in obj.items()
        }

    return obj


def parse_onset(onset):
    """ Fuction to parse different age schemas in disease onset. """

    # age string
    if 'age' in onset:
        return onset['age']
    # age ontology
    elif 'id' in onset and 'label' in onset:
        return f"{onset['label']} {onset['id']}"
    # age range
    elif 'start' in onset and 'end' in onset:
        if 'age' in onset['start'] and 'age' in onset['end']:
            return f"{onset['start']['age']} - {onset['end']['age']}"
    else:
        return None


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


def _round_decimal_two_places(d: float) -> Decimal:
    return Decimal(d).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)


def time_element_to_years(time_element: dict, unit: str = "years") -> tuple[Optional[Decimal], Optional[str]]:
    time_value: Optional[Decimal] = None
    time_unit: Optional[str] = None
    if "age" in time_element:
        return iso_duration_to_years(time_element["age"], unit=unit)
    elif "age_range" in time_element:
        start_value, start_unit = iso_duration_to_years(time_element["age_range"]["start"]["age"], unit=unit)
        end_value, end_unit = iso_duration_to_years(time_element["age_range"]["end"]["age"], unit=unit)
        time_value = (start_value + end_value) / 2
        time_unit = start_unit
    return time_value, time_unit


def iso_duration_to_years(iso_age_duration: str | dict, unit: str = "years") -> tuple[Optional[Decimal], Optional[str]]:
    """
    This function takes ISO8601 Duration string in the format e.g 'P20Y6M4D' and converts it to years.
    """
    if isinstance(iso_age_duration, dict):
        iso_age_duration = iso_age_duration.get("iso8601duration")
    duration = isodate.parse_duration(iso_age_duration)

    # if duration string includes Y and M then the instance is of both types of Duration and datetime.timedelta
    if isinstance(duration, isodate.Duration):
        # 30.5 average days in a month (including leap year)
        days = (float(duration.months) * 30.5) + duration.days
        # 24 hours 60 minutes 60 seconds
        days_to_seconds = days * 24 * 60 * 60
        # 365.25 average days in a year (including leap year)
        years = (days_to_seconds / 60 / 60 / 24 / 365.25) + float(duration.years)
        return _round_decimal_two_places(years), unit

    # if duration string contains only days then the instance is of type datetime.timedelta
    if not isinstance(duration, isodate.Duration) and isinstance(duration, datetime.timedelta):
        if duration.days is not None:
            days_to_seconds = duration.days * 24 * 60 * 60
            years = days_to_seconds / 60 / 60 / 24 / 365.25
            return _round_decimal_two_places(years), unit

    return None, None


def labelled_range_generator(field_props: dict) -> Generator[tuple[int, int, str], None, None]:
    """
    Returns a generator yielding floor, ceil and label value for each bin from
    a numeric field configuration
    """

    if "bins" in field_props["config"]:
        return custom_binning_generator(field_props)

    return auto_binning_generator(field_props)


def custom_binning_generator(field_props: dict) -> Generator[tuple[int, int, str], None, None]:
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
    minimum: Optional[int] = int(c["minimum"]) if "minimum" in c else None
    maximum: Optional[int] = int(c["maximum"]) if "maximum" in c else None
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


def auto_binning_generator(field_props) -> Generator[tuple[int, int, str], None, None]:
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


def monthly_generator(start: str, end: str) -> tuple[int, int]:
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


def get_model_and_field(field_id: str) -> tuple[any, str]:
    """
    Parses a path-like string representing an ORM such as "individual/extra_properties/date_of_consent"
    where the first crumb represents the object in the DB model, and the next ones
    are the field with their possible joins through tables relations.
    Returns a tuple of the model object and the Django string representation of the
    field for this object.
    """

    model_name, *field_path = field_id.split("/")

    model: Optional[Type[Model]] = MODEL_NAMES_TO_MODEL.get(model_name)
    if model is None:
        msg = f"Accessing field on model {model_name} not implemented"
        raise NotImplementedError(msg)

    field_name = "__".join(field_path)
    return model, field_name


def stats_for_field(model, field: str, add_missing=False) -> Mapping[str, int]:
    """
    Computes counts of distinct values for a given field. Mainly applicable to
    char fields representing categories
    """
    queryset = model.objects.all()
    return queryset_stats_for_field(queryset, field, add_missing)


def queryset_stats_for_field(queryset, field: str, add_missing=False) -> Mapping[str, int]:
    """
    Computes counts of distinct values for a queryset.
    """

    # values() restrict the table of results to this COLUMN
    # annotate() creates a `total` column for the aggregation
    # Count("*") aggregates results including nulls

    annotated_queryset = queryset.values(field).annotate(total=Count("*"))
    num_missing = 0

    stats: dict[str, int] = {}

    for item in annotated_queryset:
        key = item[field]
        if key is None:
            num_missing = item["total"]
            continue

        key = str(key) if not isinstance(key, str) else key.strip()
        if key == "":
            continue
        stats[key] = item["total"]

    if add_missing:
        stats["missing"] = num_missing

    return stats


def get_field_bins(query_set, field, bin_size):
    # computes a new column "binned" by substracting the modulo by bin size to
    # the value which requires binning (e.g. 28 => 28 - 28 % 10 = 20)
    # cast to integer to avoid numbers such as 60.00 if that was a decimal,
    # and aggregate over this value.
    query_set = query_set.annotate(
        binned=Cast(
            F(field) - Func(F(field), bin_size, function="MOD"),
            IntegerField()
        )
    ).values("binned").annotate(total=Count("binned"))
    stats = {item["binned"]: item["total"] for item in query_set}
    return stats


def compute_binned_ages(individual_queryset, bin_size: int) -> list[int]:
    """
    When age_numeric field is not available, use this function to process
    the age field in its various formats.
    Params:
        - individual_queryset: a queryset made on the individual model, containing
            the age and age_numeric fields
        - bin_size: how many years there is per bin
    Returns a list of values floored to the closest decade (e.g. 25 --> 20)
    """

    a = individual_queryset.filter(age_numeric__isnull=True).values('time_at_last_encounter')
    binned_ages = []
    for r in a.iterator():  # reduce memory footprint (no caching)
        if r["time_at_last_encounter"] is None:
            continue
        age = parse_individual_age(r["time_at_last_encounter"])
        binned_ages.append(age - age % bin_size)

    return binned_ages


def get_age_numeric_binned(individual_queryset, bin_size: int) -> dict:
    """
    age_numeric is computed at ingestion time of phenopackets. On some instances
    it might be unavailable and as a fallback must be computed from the age JSON field which
    has two alternate formats (hence more complex and slower to process)
    """
    individuals_age = get_field_bins(individual_queryset, "age_numeric", bin_size)
    if None not in individuals_age:
        return individuals_age

    del individuals_age[None]
    individuals_age = Counter(individuals_age)
    individuals_age.update(
        compute_binned_ages(individual_queryset, bin_size)   # single update instead of creating iterables in a loop
    )
    return individuals_age


def get_categorical_stats(field_props: dict) -> list[BinWithValue]:
    """
    Fetches statistics for a given categorical field and apply privacy policies
    """
    model, field_name = get_model_and_field(field_props["mapping"])
    stats = stats_for_field(model, field_name, add_missing=True)

    # Enforce values order from config and apply policies
    labels: Optional[list[str]] = field_props["config"].get("enum")
    derived_labels: bool = labels is None

    # Special case: for some fields, values are based on what's present in the
    # dataset (enum is null in the public JSON).
    # - Here, apply lexical sort, and exclude the "missing" value which will
    #   be appended at the end if it is set.
    # - Note that in this situation, we explictly MUST remove rounded-down 0-counts
    #   (below the threshold) below, otherwise we LEAK that there is 1 <= x <= threshold
    #   matching entries in the DB.
    if derived_labels:
        labels = sorted(
            [k for k in stats.keys() if k != "missing"],
            key=lambda x: x.lower()
        )

    threshold = get_threshold()
    bins: list[BinWithValue] = []

    for category in labels:
        v: int = stats.get(category, 0)

        # Censor small counts by rounding them to 0
        if v <= threshold:
            # We cannot append 0-counts for derived labels, since that indicates
            # there is a non-0 count for this label in the database - i.e., if the label is pulled
            # from the values in the database, someone could otherwise learn 1 <= this field <= threshold
            # given it being present at all.
            if derived_labels:
                continue
            v = 0  # Otherwise (pre-made labels, so we aren't leaking anything), censor the small count

        bins.append({"label": category, "value": v})

    if stats["missing"]:
        bins.append({"label": "missing", "value": stats["missing"]})

    return bins


def get_date_stats(field_props: dict) -> list[BinWithValue]:
    """
    Fetches statistics for a given date field, fill the gaps in the date range
    and apply privacy policies.
    Note that dates within a JSON are stored as strings, not instances of datetime.
    TODO: for now, only dates in extra_properties are handled. Handle dates as
    regular fields when needed.
    TODO: for now only dates binned by month are handled
    """

    if (bin_by := field_props["config"]["bin_by"]) != "month":
        msg = f"Binning dates by `{bin_by}` method not implemented"
        raise NotImplementedError(msg)

    model, field_name = get_model_and_field(field_props["mapping"])

    if "extra_properties" not in field_name:
        msg = "Binning date-like fields that are not in extra-properties is not implemented"
        raise NotImplementedError(msg)

    # Note: lexical sort works on ISO dates
    query_set = (
        model.objects.all()
        .values(field_name)
        .order_by(field_name)
        .annotate(total=Count(field_name))
    )

    stats = defaultdict(int)
    start: Optional[str] = None
    end: Optional[str] = None
    # Key the counts on yyyy-mm combination (aggregate same month counts)
    for item in query_set:
        key = "missing" if item[field_name] is None else item[field_name][:LENGTH_Y_M]
        stats[key] += item["total"]

        if key == "missing":
            continue

        # start is set to the first non-missing key processed; end is set to the last one.
        if start:
            end = key
        else:
            start = key

    # All the bins between start and end date must be represented
    threshold = get_threshold()
    bins: list[BinWithValue] = []
    if start:   # at least one month
        for year, month in monthly_generator(start, end or start):
            key = f"{year}-{month:02d}"
            label = f"{month_abbr[month].capitalize()} {year}"    # convert key as yyyy-mm to `abbreviated month yyyy`
            v = stats.get(key, 0)
            bins.append({
                "label": label,
                "value": 0 if v <= threshold else v
            })

    # Append missing items at the end if any
    if "missing" in stats:
        bins.append({"label": "missing", "value": stats["missing"]})

    return bins


def get_month_date_range(field_props: dict) -> tuple[Optional[str], Optional[str]]:
    """
    Get start date and end date from the database
    Note that dates within a JSON are stored as strings, not instances of datetime.
    TODO: for now, only dates in extra_properties are handled. Aggregate functions
    are not available for data in JSON fields.
    Implement handling dates as regular fields when needed.
    TODO: for now only dates binned by month are handled.
    """

    if (bin_by := field_props["config"]["bin_by"]) != "month":
        raise NotImplementedError(f"Binning dates by `{bin_by}` method not implemented")

    model, field_name = get_model_and_field(field_props["mapping"])

    if "extra_properties" not in field_name:
        raise NotImplementedError("Binning date-like fields that are not in extra_properties is not implemented")

    is_not_null_filter = {f"{field_name}__isnull": False}   # property may be missing: avoid handling "None"

    # Note: lexicographic sort is correct with date strings like `2021-03-09`
    query_set = (
        model.objects
        .filter(**is_not_null_filter)
        .values(field_name)
        .distinct()
        .order_by(field_name)
    )

    if query_set.count() == 0:
        return None, None

    start = query_set.first()[field_name][:LENGTH_Y_M]
    end = query_set.last()[field_name][:LENGTH_Y_M]

    return start, end


def get_range_stats(field_props: dict) -> list[BinWithValue]:
    model, field = get_model_and_field(field_props["mapping"])

    # Generate a list of When conditions that return a label for the given bin.
    # This is equivalent to an SQL CASE statement.
    whens = [When(
        **{f"{field}__gte": floor} if floor is not None else {},
        **{f"{field}__lt": ceil} if ceil is not None else {},
        then=Value(label)
    ) for floor, ceil, label in labelled_range_generator(field_props)]

    query_set = (
        model.objects
        .values(label=Case(*whens, default=Value("missing"), output_field=CharField()))
        .annotate(total=Count("label"))
    )

    threshold = get_threshold()  # Maximum number of entries needed to round a count down to 0 (censored discovery)
    stats: dict[str, int] = dict()
    for item in query_set:
        key = item["label"]
        stats[key] = item["total"] if item["total"] > threshold else 0

    # All the bins between start and end must be represented and ordered
    bins: list[BinWithValue] = []
    for floor, ceil, label in labelled_range_generator(field_props):
        bins.append({"label": label, "value": stats.get(label, 0)})

    if "missing" in stats:
        bins.append({"label": "missing", "value": stats["missing"]})

    return bins


def get_field_options(field_props: dict) -> list[Any]:
    """
    Given properties for a public field, return the list of authorized options for
    querying this field.
    """
    if field_props["datatype"] == "string":
        options = field_props["config"].get("enum")
        # Special case: no list of values specified
        if options is None:
            # We must be careful here not to leak 'small cell' values as options
            # - e.g., if there are three individuals with sex=UNKNOWN_SEX, this
            #   should be treated as if the field isn't in the database at all.
            options = get_distinct_field_values(field_props)
    elif field_props["datatype"] == "number":
        options = [label for floor, ceil, label in labelled_range_generator(field_props)]
    elif field_props["datatype"] == "date":
        # Assumes the field is in extra_properties, thus can not be aggregated
        # using SQL MIN/MAX functions
        start, end = get_month_date_range(field_props)
        options = [f"{month_abbr[m].capitalize()} {y}" for y, m in monthly_generator(start, end)] if start else []
    else:
        raise NotImplementedError()

    return options


def get_distinct_field_values(field_props: dict) -> list[Any]:
    # We must be careful here not to leak 'small cell' values as options
    # - e.g., if there are three individuals with sex=UNKNOWN_SEX, this
    #   should be treated as if the field isn't in the database at all.

    model, field = get_model_and_field(field_props["mapping"])
    threshold = get_threshold()

    values_with_counts = model.objects.values_list(field).annotate(count=Count(field))
    return [val for val, count in values_with_counts if count > threshold]


def filter_queryset_field_value(qs, field_props, value: str):
    """
    Further filter a queryset using the field defined by field_props and the
    given value.
    It is a prerequisite that the field mapping defined in field_props is represented
    in the queryset object.
    `mapping_for_search_filter` is an optional property that gets precedence over `mapping`
    for the necessity of filtering. It is not necessary to specify this when
    the `mapping` value is based on the same model as the queryset.
    """

    model, field = get_model_and_field(
        field_props["mapping_for_search_filter"] if "mapping_for_search_filter" in field_props
        else field_props["mapping"]
    )

    if field_props["datatype"] == "string":
        condition = {f"{field}__iexact": value}
    elif field_props["datatype"] == "number":
        # values are of the form "[50, 150)", "< 50" or "≥ 800"

        if value.startswith("["):
            [start, end] = [int(v) for v in value.lstrip("[").rstrip(")").split(", ")]
            condition = {
                f"{field}__gte": start,
                f"{field}__lt": end
            }
        else:
            [sym, val] = value.split(" ")
            if sym == "≥":
                condition = {f"{field}__gte": int(val)}
            elif sym == "<":
                condition = {f"{field}__lt": int(val)}
            else:
                raise NotImplementedError()
    elif field_props["datatype"] == "date":
        # For now, limited to date expressed as month/year such as "May 2022"
        d = datetime.datetime.strptime(value, "%b %Y")
        val = d.strftime("%Y-%m")   # convert to "yyyy-mm" format to search for dates as "2022-05-03"
        condition = {f"{field}__startswith": val}
    else:
        raise NotImplementedError()

    logger.debug(f"Filtering {model}.{field} with {condition}")

    return qs.filter(**condition)


def experiment_type_stats(queryset):
    """
    returns count and bento_public format list of stats for experiment type
    note that queryset_stats_for_field() does not count "missing" correctly when the field has multiple foreign keys
    """
    e_types = queryset.values(label=F("phenopackets__biosamples__experiment__experiment_type")).annotate(
        value=Count("phenopackets__biosamples__experiment", distinct=True))
    return bento_public_format_count_and_stats_list(e_types)


def biosample_tissue_stats(queryset):
    """
    returns count and bento_public format list of stats for biosample sampled_tissue
    """
    b_tissue = queryset.values(label=F("phenopackets__biosamples__sampled_tissue__label")).annotate(
        value=Count("phenopackets__biosamples", distinct=True))
    return bento_public_format_count_and_stats_list(b_tissue)


def bento_public_format_count_and_stats_list(annotated_queryset) -> tuple[int, list[BinWithValue]]:
    stats_list: list[BinWithValue] = []
    total = 0
    for q in annotated_queryset:
        label = q["label"]
        value = int(q["value"])
        total += value
        if label is not None:
            stats_list.append({"label": label, "value": value})

    return total, stats_list


def computed_property(name: str):
    """
    Takes a name and returns it prefixed with "__"
    """
    return COMPUTED_PROPERTY_PREFIX + name
