import datetime
import isodate
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Generator


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


def time_element_to_years(time_element: dict, unit: str = "years") -> tuple[Decimal | None, str | None]:
    time_value: Decimal | None = None
    time_unit: str | None = None
    if "age" in time_element:
        return iso_duration_to_years(time_element["age"], unit=unit)
    elif "age_range" in time_element:
        start_value, start_unit = iso_duration_to_years(time_element["age_range"]["start"]["age"], unit=unit)
        end_value, end_unit = iso_duration_to_years(time_element["age_range"]["end"]["age"], unit=unit)
        time_value = (start_value + end_value) / 2
        time_unit = start_unit
    return time_value, time_unit


def iso_duration_to_years(iso_age_duration: str | dict, unit: str = "years") -> tuple[Decimal | None, str | None]:
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


def monthly_generator(start: str, end: str) -> Generator[tuple[int, int], None, None]:
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
