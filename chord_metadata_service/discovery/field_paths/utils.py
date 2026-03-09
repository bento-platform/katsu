__all__ = ["field_path_to_django_mapping"]

# Function to rewrite a tuple of strings (field path) as a Django mapping string (delimited with "__"):
field_path_to_django_mapping = "__".join
