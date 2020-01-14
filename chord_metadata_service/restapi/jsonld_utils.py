# utils to convert dataset json to json-ld

def dataset_to_jsonld(dataset):
    dataset['@context'] = {}
    dataset['@context']['$schema'] = 'https://w3id.org/dats/schema/dataset_schema.json'
    dataset['@context']['@type'] = 'Dataset'
    # dates
    if 'dates' in dataset.keys():
        for date in dataset['dates']:
            date['$schema'] = 'https://w3id.org/dats/schema/date_info_schema.json'
            date['@type'] = 'Date'
            # the date always will be only object in our mapping
            date['type']['$schema'] = 'https://w3id.org/dats/schema/annotation_schema.json'
            date['type']['@type'] = 'Annotation'
    # creators
    if 'creators' in dataset.keys():
        for creator in dataset['creators']:
            if 'name' in creator.keys():
                creator['$schema'] = 'https://w3id.org/dats/schema/organization_schema.json'
                creator['@type'] = 'Organization'
            else:
                creator['$schema'] = 'https://w3id.org/dats/schema/person_schema.json'
                creator['@type'] = 'Person'
    if 'stored_in' in dataset.keys():
        dataset['stored_in']['$schema'] = 'https://w3id.org/dats/schema/data_repository_schema.json'
        dataset['stored_in']['@type'] = 'DataRepository'


    return dataset