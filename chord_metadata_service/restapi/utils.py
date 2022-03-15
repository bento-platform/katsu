import isodate
import datetime


def camel_case_field_names(string):
    """ Function to convert snake_case field names to camelCase """
    # Capitalize every part except the first
    return "".join(
        part.title() if i > 0 else part
        for i, part in enumerate(string.split("_"))
    )


def transform_keys(obj):
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
    elif 'id' and 'label' in onset:
        return f"{onset['label']} {onset['id']}"
    # age range
    elif 'start' and 'end' in onset:
        if 'age' in onset['start'] and 'age' in onset['end']:
            return f"{onset['start']['age']} - {onset['end']['age']}"
    else:
        return None


def parse_duration(string):
    """ Returns years integer. """
    string = string.split('P')[-1]
    return int(float(string.split('Y')[0]))


def parse_individual_age(age_obj):
    """ Parses two possible age representations and returns average age or age as integer. """
    # AGE OPTIONS
    # "age": {
    #     "age": "P96Y"
    # }
    # AND
    # "age": {
    #     "start": {
    #         "age": "P45Y"
    #     },
    #     "end": {
    #         "age": "P49Y"
    #     }
    # }
    if 'start' in age_obj:
        start_age = parse_duration(age_obj['start']['age'])
        end_age = parse_duration(age_obj['end']['age'])
        # for the duration calculate the average age
        age = (start_age + end_age) // 2
    elif 'age' in age_obj:
        age = parse_duration(age_obj['age'])
    else:
        raise ValueError(f"Error: {age_obj} format not supported")
    return age


def iso_duration_to_years(iso_age_duration: str, unit="years"):
    """
    This function takes ISO8601 Duration string in the format e.g 'P20Y6M4D' and converts it to years.
    """
    duration = isodate.parse_duration(iso_age_duration)
    # if duration string includes Y and M then the instance is of both types of Duration and datetime.timedelta
    if isinstance(duration, isodate.Duration):
        # 30.5 average days in a month (including leap year)
        days = (float(duration.months) * 30.5) + duration.days
        # 24 hours 60 minutes 60 seconds
        days_to_seconds = days * 24 * 60 * 60
        # 365.25 average days in a year (including leap year)
        years = (days_to_seconds / 60 / 60 / 24 / 365.25) + float(duration.years)
        return (round(years, 2)), unit
    # if duration string contains only days then the instance is of type datetime.timedelta
    elif not isinstance(duration, isodate.Duration) and isinstance(duration, datetime.timedelta):
        if duration.days:
            days_to_seconds = duration.days * 24 * 60 * 60
            years = days_to_seconds / 60 / 60 / 24 / 365.25
            return (round(years, 2)), unit
    return None, None
