def camel_case_field_names(string):
    """ Function to convert snake_case field names to camelCase """

    if '_' in string:
        splitted = string.split('_')
        capitilized = []
        capitilized.append(splitted[0])
        for each in splitted[1:]:
            capitilized.append(each.title())
        return ''.join(capitilized)
    return string


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
