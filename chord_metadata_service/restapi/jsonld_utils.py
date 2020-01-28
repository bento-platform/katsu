# utils to convert dataset json to json-ld
# context to schema.org provided here https://github.com/datatagsuite/context


CONTEXT = [
    {
      "sdo": "https://schema.org/",
      "Dataset": "sdo:Dataset",
      "title": {
        "@id": "sdo:name",
        "@type": "sdo:Text"
      },
      "description": {
        "@id": "sdo:description",
        "@type": "sdo:Text"
      },
      "distributions": {
        "@id": "sdo:distribution",
        "@type": "sdo:DataDownload"
      },
      "formats": "sdo:fileFormat",
      "unit": "sdo:unitCode",
      "access": {
        "@id": "sdo:accessMode",
        "@type": "sdo:EntryPoint"
      },
      "landingPage": {
        "@id": "sdo:url",
        "@type": "sdo:URL"
      },
      "size": {
        "@id": "sdo:contentSize",
        "@type": "sdo:Text"
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
      "keywords": "sdo:keywords",
      "dates": "sdo:temporalCoverage",
      "storedIn": {
        "@id": "sdo:includedInDataCatalog",
        "@type": "sdo:DataCatalog"
      },
      "version": "sdo:version",
      "identifier": {
        "@id": "sdo:identifier",
        "@type": "sdo:Text"
      },
      "DataType": "sdo:Thing",
      "information": {
        "@id": "sdo:Property"
      },
      "Annotation": "sdo:Thing",
      "TaxonomicInformation": "sdo:Thing",
      "Identifier": "sdo:Thing",
      "identifierSource": {
        "@id": "sdo:Property",
        "@type": "sdo:Text"
      },
      "CategoryValuesPair": "sdo:PropertyValue",
      "category": {
        "@id": "sdo:value",
        "@type": "sdo:Text"
      },
      "categoryIRI": {
        "@id": "sdo:url",
        "@type": "sdo:URL"
      },
      "Organization": "sdo:Organization",
      "value": {
        "@id": "sdo:value",
        "@type": "sdo:DataType"
      },
      "valueIRI": {
        "@id": "sdo:url",
        "@type": "sdo:URL"
      },
      "name": {
        "@id": "sdo:name",
        "@type": "sdo:Text"
      },
      "Date": "sdo:DateTime",
      "date": {
        "@id": "sdo:Property"
      },
      "type": {
        "@id": "sdo:Property"
      },
      "Disease": "sdo:MedicalCondition",
      "MolecularEntity": "sdo:Thing",
      "characteristics": {
        "@id": "sdo:additionalProperty",
        "@type": "sdo:Thing"
      },
      "diseaseStatus": "sdo:status",
      "Material": "sdo:Thing",
      "derivesFrom": "sdo:relatedTo",
      "License": "sdo:CreativeWork",
      "DataRepository": "sdo:DataCatalog",
      "DataAcquisition": "sdo:CreateAction",
      "uses": "sdo:relatedTo",
      "Software": "sdo:SoftwareApplication",
      "values": "sdo:value",
      "extraProperties": "sdo:additionalProperty"
    }
  ]


def obj_to_jsonld(obj, mapping) -> dict:
    # obj['@id'] = CONTEXT_SCHEMAS[mapping]['id']
    # obj['@type'] = CONTEXT_SCHEMAS[mapping]['type']
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
    dataset['@context'] = CONTEXT
    return dataset
