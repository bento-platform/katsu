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
