import datetime
import isodate
from decimal import Decimal, ROUND_HALF_EVEN

__all__ = [
    "time_element_to_str",
    "iso_duration_to_years",
    "time_element_to_years",
]


def time_element_to_str(time_element: dict) -> str | None:
    """
    Fuction to stringify different TimeElements (returns None if the time interval doesn't match any valid form).
    See https://phenopacket-schema.readthedocs.io/en/latest/time-element.html for more information on TimeElement.
    """

    # Age: https://phenopacket-schema.readthedocs.io/en/latest/age.html
    if "age" in time_element:
        return time_element["age"]["iso8601duration"]
    # OntologyClass: https://phenopacket-schema.readthedocs.io/en/latest/ontologyclass.html
    elif "ontology_class" in time_element:
        return f"{time_element['ontology_class']['label']} ({time_element['ontology_class']['id']})"
    # AgeRange: https://phenopacket-schema.readthedocs.io/en/latest/age.html#rstagerange
    elif "age_range" in time_element:
        ar = time_element["age_range"]
        return f"{ar['start']['iso8601duration']} - {ar['end']['iso8601duration']}"
    # TimeInterval: https://phenopacket-schema.readthedocs.io/en/latest/time-interval.html
    elif "interval" in time_element:
        return f"{time_element['interval']['start']} - {time_element['interval']['end']}"
    # GestationalAge: https://phenopacket-schema.readthedocs.io/en/latest/gestational-age.html
    elif "gestational_age" in time_element:
        return (
            f"{time_element['gestational_age']['weeks']} weeks {time_element['gestational_age']['days']} days"
            if "days" in time_element["gestational_age"]
            else f"{time_element['gestational_age']['weeks']} weeks"
        )
    # Timestamp: https://phenopacket-schema.readthedocs.io/en/latest/timestamp.html
    elif "timestamp" in time_element:
        return time_element["timestamp"]
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
