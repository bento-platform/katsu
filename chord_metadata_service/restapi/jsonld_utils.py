# utils to convert dataset json to json-ld

def dates_to_jsonld(dates) -> list:
    for date in dates:
        date['$schema'] = 'https://w3id.org/dats/schema/date_info_schema.json'
        date['@type'] = 'Date'
        # the date always will be only object in our mapping
        annotation_to_jsonld(date['type'])
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


def identifier_to_jsonld(identifier) -> dict:
    identifier['$schema'] = 'https://w3id.org/dats/schema/identifier_info_schema.json'
    identifier['@type'] = 'Identifier'
    return identifier


def annotation_to_jsonld(annotation) -> dict:
    annotation['$schema'] = 'https://w3id.org/dats/schema/annotation_schema.json'
    annotation['@type'] = 'Annotation'
    return annotation


def extra_properties_to_jsonld(extra_properties) -> list:
    for ep in extra_properties:
        ep['$schema'] = 'https://w3id.org/dats/schema/category_values_pair_schema.json'
        ep['@type'] = 'CategoryValuesPair'
        if ep['values']:
            for value in ep['values']:
                annotation_to_jsonld(value)
    return extra_properties


def dataset_to_jsonld(dataset):
    dataset['@context'] = {}
    dataset['@context']['$schema'] = 'https://w3id.org/dats/schema/dataset_schema.json'
    dataset['@context']['@type'] = 'Dataset'
    # dates
    if 'dates' in dataset.keys():
        dates_to_jsonld(dataset['dates'])
    # creators
    if 'creators' in dataset.keys():
        creators_to_jsonld(dataset['creators'])
    if 'stored_in' in dataset.keys():
        dataset['stored_in']['$schema'] = 'https://w3id.org/dats/schema/data_repository_schema.json'
        dataset['stored_in']['@type'] = 'DataRepository'
    if 'types' in dataset.keys():
        for t in dataset['types']:
            t['$schema'] = 'https://w3id.org/dats/schema/data_type_schema.json'
            t['@type'] = 'DataType'
            if 'information' in t.keys():
                annotation_to_jsonld(t['information'])
    if dataset['primary_publications']:
        for pp in dataset['primary_publications']:
            pp['$schema'] = 'https://w3id.org/dats/schema/publication_schema.json'
            pp['@type'] = 'Publication'
            if 'identifier' in pp.keys():
                identifier_to_jsonld(pp['identifier'])
            if 'authors' in pp.keys():
                creators_to_jsonld(pp['authors'])
            if 'dates' in pp.keys():
                dates_to_jsonld(pp['dates'])
    if dataset['licenses']:
        for license in dataset['licenses']:
            license['$schema'] = 'https://w3id.org/dats/schema/license_schema.json'
            license['@type'] = 'License'
    if dataset['extra_properties']:
        extra_properties_to_jsonld(dataset['extra_properties'])

    return dataset