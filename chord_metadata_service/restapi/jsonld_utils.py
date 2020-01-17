# utils to convert dataset json to json-ld

CONTEXT_SCHEMAS = {
    'dataset': {
        'schema': 'https://w3id.org/dats/schema/dataset_schema.json',
        'type': 'Dataset'
    },
    'licenses': {
        'schema': 'https://w3id.org/dats/schema/license_schema.json',
        'type': 'License'
    },
    'distributions': {
        'schema': 'https://w3id.org/dats/schema/dataset_distribution_schema.json',
        'type': 'DatasetDistribution'
    },
    'types': {
        'schema': 'https://w3id.org/dats/schema/data_type_schema.json',
        'type': 'DataType'
    },
    'stored_in': {
        'schema': 'https://w3id.org/dats/schema/data_repository_schema.json',
        'type': 'DataRepository'
    },
    'identifier': {
        'schema': 'https://w3id.org/dats/schema/identifier_info_schema.json',
        'type': 'Identifier'
    },
    'primary_publications': {
        'schema': 'https://w3id.org/dats/schema/publication_schema.json',
        'type': 'Publication'
    },
    'alternate_identifiers': {
        'schema': 'https://w3id.org/dats/schema/alternate_identifier_info_schema.json',
        'type': 'AlternateIdentifier'
    },
    'related_identifiers': {
        'schema': 'https://w3id.org/dats/schema/related_identifier_info_schema.json',
        'type': 'RelatedIdentifier'
    },
    'annotation': {
        'schema': 'https://w3id.org/dats/schema/annotation_schema.json',
        'type': 'Annotation'
    },
    'extra_properties': {
        'schema': 'https://w3id.org/dats/schema/category_values_pair_schema.json',
        'type': 'CategoryValuesPair'
    }
}


def obj_to_jsonld(obj, mapping) -> dict:
    obj['$schema'] = CONTEXT_SCHEMAS[mapping]['schema']
    obj['@type'] = CONTEXT_SCHEMAS[mapping]['type']
    return obj


def dates_to_jsonld(dates) -> list:
    for date in dates:
        date['$schema'] = 'https://w3id.org/dats/schema/date_info_schema.json'
        date['@type'] = 'Date'
        # the date always will be only object in our mapping
        obj_to_jsonld(date['type'], 'annotation')
    return dates


def creators_to_jsonld(creators) -> list:
    for creator in creators:
        if 'name' in creator.keys():
            creator['$schema'] = 'https://w3id.org/dats/schema/organization_schema.json'
            creator['@type'] = 'Organization'
        else:
            creator['$schema'] = 'https://w3id.org/dats/schema/person_schema.json'
            creator['@type'] = 'Person'
    return creators


def extra_properties_to_jsonld(extra_properties) -> list:
    for ep in extra_properties:
        obj_to_jsonld(ep, 'extra_properties')
        if ep['values']:
            for value in ep['values']:
                obj_to_jsonld(value, 'annotation')
    return extra_properties


def spatial_coverage_to_jsonld(spatial_coverage) -> list:
    for sc in spatial_coverage:
        sc['$schema'] = 'https://w3id.org/dats/schema/place_schema.json'
        sc['@type'] = 'Place'
        if 'identifier' in sc.keys():
            obj_to_jsonld(sc['identifier'], 'identifier')
        if 'alternate_identifiers' in sc.keys():
            for alt_id in sc['alternate_identifiers']:
                obj_to_jsonld(alt_id, 'alternate_identifiers')
        if 'related_identifiers' in sc.keys():
            for rel_id in sc['related_identifiers']:
                obj_to_jsonld(rel_id, 'related_identifiers')
    return spatial_coverage


def distributions_to_jsonld(distributions) -> list:
    for distribution in distributions:
        obj_to_jsonld(distribution, 'distributions')
        if 'identifier' in distribution.keys():
            obj_to_jsonld(distribution['identifier'], 'identifier')
        if 'alternate_identifiers' in distribution.keys():
            for alt_id in distribution['alternate_identifiers']:
                obj_to_jsonld(alt_id, 'alternate_identifiers')
        if 'related_identifiers' in distribution.keys():
            for rel_id in distribution['related_identifiers']:
                obj_to_jsonld(rel_id, 'related_identifiers')
        if 'stored_in' in distribution.keys():
            obj_to_jsonld(distribution['stored_in'], 'stored_in')
        if 'dates' in distribution.keys():
            dates_to_jsonld(distribution['dates'])
        if 'licenses' in distribution.keys():
            for license in distribution['liceses']:
                obj_to_jsonld(license, 'licenses')
        # access
    return distributions


def dataset_to_jsonld(dataset):
    """
    The function adds semantic context to json elements
    :param dataset: json serialization of dataset
    :return: enriched json with linked data context
    """
    dataset['@context'] = {}
    dataset['@context']['$schema'] = CONTEXT_SCHEMAS['dataset']['schema']
    dataset['@context']['@type'] = CONTEXT_SCHEMAS['dataset']['type']
    # dates
    identifier_str = dataset['identifier']
    dataset['identifier'] = {}
    dataset['identifier']['identifier'] = identifier_str
    obj_to_jsonld(dataset['identifier'], 'identifier')
    if 'dates' in dataset.keys():
        dates_to_jsonld(dataset['dates'])
    # creators
    if 'creators' in dataset.keys():
        creators_to_jsonld(dataset['creators'])
    if 'stored_in' in dataset.keys():
        obj_to_jsonld(dataset['stored_in'], 'stored_in')
    if 'types' in dataset.keys():
        for t in dataset['types']:
            obj_to_jsonld(t, 'types')
            if 'information' in t.keys():
                obj_to_jsonld(t['information'], 'annotation')
    if 'primary_publications' in dataset.keys():
        for pp in dataset['primary_publications']:
            obj_to_jsonld(pp, 'primary_publications')
            if 'identifier' in pp.keys():
                obj_to_jsonld(pp['identifier'], 'identifier')
            if 'authors' in pp.keys():
                creators_to_jsonld(pp['authors'])
            if 'dates' in pp.keys():
                dates_to_jsonld(pp['dates'])
    if 'licenses' in dataset.keys():
        for license in dataset['licenses']:
            obj_to_jsonld(license, 'licenses')
    if 'extra_properties' in dataset.keys():
        extra_properties_to_jsonld(dataset['extra_properties'])
    if 'alternate_identifiers' in dataset.keys():
        for identifier in dataset['alternate_identifiers']:
            obj_to_jsonld(identifier, 'alternate_identifiers')
    if 'related_identifiers' in dataset.keys():
        for rel_id in dataset['related_identifiers']:
            obj_to_jsonld(rel_id, 'related_identifiers')
    if 'spatial_coverage' in dataset.keys():
        spatial_coverage_to_jsonld(dataset['spatial_coverage'])
    if 'distributions' in dataset.keys():
        distributions_to_jsonld(dataset['distributions'])
    # TODO the rest
    return dataset
