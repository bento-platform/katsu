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

    if isinstance(obj, dict):
        transformed_obj = {}
        for key, value in obj.items():
            if isinstance(value, dict):
                value = transform_keys(value)
            transformed_obj[camel_case_field_names(key)] = value
        return transformed_obj
