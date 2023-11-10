import datetime
import isodate
from decimal import Decimal, ROUND_HALF_EVEN

__all__ = [
    "parse_onset",
    "iso_duration_to_years",
    "time_element_to_years",
]


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


def _round_decimal_two_places(d: float) -> Decimal:
    return Decimal(d).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)


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
