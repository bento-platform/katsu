# utils to convert dataset json to json-ld
# context to schema.org provided here https://github.com/datatagsuite/context
CONTEXT_SDO = {
    "sdo": "https://schema.org/",
    "Dataset": "sdo:Dataset",
    "identifier": {
      "@id": "sdo:identifier",
      "@type": "sdo:Text"
    },
    "alternateIdentifier": "sdo:alternateName",
    "relatedIdentifier": "sdo:mentions",
    "title": {
      "@id": "sdo:name",
      "@type": "sdo:Text"
    },
    "description": {
      "@id": "sdo:description",
      "@type": "sdo:Text"
    },
    "dates": "sdo:temporalCoverage",
    "spatialCoverage": "sdo:spatialCoverage",
    "storedIn": {
        "@id": "sdo:includedInDataCatalog",
        "@type": "sdo:DataCatalog"
    },
    "distributions": {
      "@id": "sdo:distribution",
      "@type": "sdo:DataDownload"
    },
    "primaryPublications": "sdo:citation",
    "citations": "sdo:citation",
    "producedBy": "sdo:producer",
    "creators": {
        "@id": "sdo:creator",
        "@type": "sdo:Thing"
    },
    "licenses": "sdo:license",
    "isAbout": "sdo:about",
    "hasPart": {
        "@id": "sdo:hasPart",
        "@type": "sdo:Dataset"
    },
    "acknowledges": "sdo:funder",
    "dimensions": "sdo:variableMeasured",
    "dates": "sdo:DateTime",
        "date": {
            "@id": "sdo:Property"
        },
        "type":{
            "@id": "sdo:Property"
        }
  }


def obj_to_jsonld(obj, mapping) -> dict:
    obj['@id'] = CONTEXT_SCHEMAS[mapping]['id']
    obj['@type'] = CONTEXT_SCHEMAS[mapping]['type']
    return obj


def dates_to_jsonld(dates) -> list:
    for date in dates:
        obj_to_jsonld(date, 'dates')
        # the date always will be only object in our mapping
        obj_to_jsonld(date['type'], 'annotation')
    return dates


def creators_to_jsonld(creators) -> list:
    for creator in creators:
        if 'name' in creator.keys():
            obj_to_jsonld(creator, 'organization')
        else:
            obj_to_jsonld(creator, 'person')
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
        obj_to_jsonld(sc, 'spatial_coverage')
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
    dataset['@context'] = CONTEXT_SDO
    return dataset
