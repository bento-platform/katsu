# map from katsu discovery output to beacon filtering terms


# discovery response looks like this, code is probably similar: 

    # {
    #     "id": "sex",
    #     "definition": {
    #         "mapping": "individual/sex",
    #         "title": "Sex",
    #         "description": "Sex at birth",
    #         "datatype": "string",
    #         "minimum_permissions": "counts",
    #         "mapping_for_search_filter": null,
    #         "group_by": null,
    #         "group_by_value": null,
    #         "value_mapping": null,
    #         "config": {"enum": null},
    #     },
    #     "options": ["FEMALE", "MALE"],
    # }


# should map to: 

    # { 
    #     "description": "Sex at birth",
    #     "id": "sex",
    #     "label": "Sex",
    #     "type": "alphanumeric",
    #     "values": ["FEMALE", "MALE"]
    # }

# ... discovery will also have some data that is missing here, 
# including a category for sex (typically "General" or "Demographics")
# This will have to be handled somewhere 
# currently in beacon we handle it by adding an extra field: 
    # "bento": {
    #     "mapping": "individual/sex",
    #     "section": "General"
    # },


# Ontologies
# not yet handled, but should be a priority


# Free-text search
# no accommodations for this in beacon, but can be handled as a custom filter
# all we need is a field for the search type (plain, phrase, trigram, websearch) and a field for the text
# not clear how to handle this as a part of /filtering_terms response
# but this is a weakness of the spec, not of our implementation 

