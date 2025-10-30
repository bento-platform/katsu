import datetime
import isodate
from decimal import Decimal, ROUND_HALF_EVEN

__all__ = [
    "time_element_to_str",
    "iso_duration_to_years",
    "time_element_to_years",
]


def time_element_to_str(time_interval: dict) -> str | None:
    """
    Fuction to stringify different TimeElements (returns None if the time interval doesn't match any valid form).
    """

    # age string
    if 'age' in time_interval:
        return time_interval['age']
    # OntologyClass
    elif 'id' in time_interval and 'label' in time_interval:
        return f"{time_interval['label']} ({time_interval['id']})"
    # AgeRange | TimeInterval
    elif 'start' in time_interval and 'end' in time_interval:
        if 'age' in time_interval['start'] and 'age' in time_interval['end']:  # AgeRange
            return f"{time_interval['start']['age']} - {time_interval['end']['age']}"
        else:  # TimeInterval
            return f"{time_interval['start']} - {time_interval['end']}"
    # GestationalAge
    elif "weeks" in time_interval:
        return (
            f"{time_interval['weeks']} weeks {time_interval['days']} days"
            if "days" in time_interval
            else f"{time_interval['weeks']} weeks"
        )
    # Timestamp
    elif "timestamp" in time_interval:
        return time_interval["timestamp"]
    else:
        return None


DAYS_IN_A_MONTH = 30.5  # 30.5 average days in a month (including leap year)
DAYS_IN_A_YEAR = 365.25  # 365.25 average days in a year (including leap year)


def _days_to_years(days: float) -> float:
    return days / DAYS_IN_A_YEAR   # 365.25 average days in a year (including leap year)


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
        days = (float(duration.months) * DAYS_IN_A_MONTH) + duration.days
        years = _days_to_years(days) + float(duration.years)
        return _round_decimal_two_places(years), unit

    # if duration string contains only days then the instance is of type datetime.timedelta
    if not isinstance(duration, isodate.Duration) and isinstance(duration, datetime.timedelta):
        if duration.days is not None:
            years = _days_to_years(duration.days)
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
