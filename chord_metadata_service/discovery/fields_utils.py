from typing import Iterator


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
