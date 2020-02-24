Introduction
============

Metadata service is a service to store phenotypic and clinical metadata about the patient and/or biosample.
Data model is partly based on `GA4GH Phenopackets schema <https://github.com/phenopackets/phenopacket-schema>`_.

The simplified data model of the service is below.

.. image:: ../_static/simple_metadata_service_model_v0.3.0.png


Technical implementation
------------------------

The service is implemented in Python and Django and uses PostgreSQL database to store the data.
Besides PostgreSQL the data can be indexed and queried in Elasticsearch.


Architecture
------------

Metadata Service contains several services that share one API.
Services depend on each other and separated based on their scope.

**1. Patients service** handles anonymized individual’s data (e.g. individual id, sex, age or date of birth)

- Data model: aggregated profile from GA4GH Phenopackets Individual and FHIR Patient. It contains all fields of Phenopacket Individual and additional fields from FHIR Patient.

**2. Phenopackets service** handles phenotypic and clinical data

- Data model: GA4GH Phenopackets schema. Currently contains only two out of four Phenopackets top elements - Phenopacket and Interpretation.

**3. CHORD service** handles granular metadata about dataset (e.g. description, where the dataset is located, who are the creators of the dataset, licenses applied to the dataset,
authorization policy, terms of use).
The dataset in the current implementation is one or more phenopackets related to each other through their provenance.

- Data model:

  - DATS model used for dataset description;
  - GA4GH DUO is used to capture the terms of use applied to a dataset.


**4. Restapi service** handles all generic functionality shared among other services (e.g. renderers, common serializers, schemas, validators)


Metadata standards
------------------

`Phenopackets schema <https://github.com/phenopackets/phenopacket-schema>`_ is used for phenotypic description of patient and/or biosample.

`DATS standard <https://github.com/datatagsuite>`_ is used for dataset description.

`DUO ontology <https://github.com/EBISPOT/DUO>`_ is used for describing terms of use for a dataset.

`Phenopackets on FHIR Implementation Guide <https://aehrc.github.io/fhir-phenopackets-ig/>`_ is used to map Phenopackets elements to `FHIR <https://www.hl7.org/fhir/>`_ resources.


REST API highlights
-------------------

**Parsers and Renderers**

- Standard API serves data in snake_case style.

- To retrieve the data in camelCase append :code:`?format=phenopackets`.

- Data can be ingested in both snake_case or camelCase.

- Other available renderers:

  - Currently the following classes can be retirved in FHIR format by appending :code:`?format=fhir`: Phenopackets, Individual, Biosample, PhenotypicFeature, HtsFile, Gene, Variants, Disease, Procedure.

  - JSON-LD context to schema.org provided for Dataset class in order to allow for a Google dataset search for Open Access Data: append :code:`?format=json-ld` when querying dataset endpoint.

  - Dataset description can also be retrived in RDF format: append :code:`?format=rdf` when querying dataset endpoint.

**Data ingest**

Currently only the data that follow Phenopackets schema can be ingested.
Ingest endpoint is :code:`/private/ingest` .
Example of POST request body:

.. code-block::

    {
      "table_id": "table_unique_id",
      "workflow_id": "phenopackets_json",
      "workflow_metadata": {
        "inputs": [
          {
            "id": "json_document",
            "type": "file",
            "extensions": [
              ".json"
            ]
          }
        ],
        "outputs": [
          {
            "id": "json_document",
            "type": "file",
            "value": "{json_document}"
          }
        ]
      },
      "workflow_params": {
        "phenopackets_json.json_document": "/path/to/data.json"
      },
      "workflow_outputs": {
        "json_document": "/path/to/data.json"
      }
    }




Elasticsearch index (optional)
------------------------------

Data in FHIR format can be indexed in Elasticsearch - this is optional.
If an Elasticsearch instance is running on the server (so on :code:`localhost:9000`) these models will automatically be indexed on creation/update.
There are also two scripts provided to update these indexes all at once:

.. code-block::

    python manage.py patients_build_index
    python manage.py phenopackets_build_index

To query this information, here is an example request :

.. code-block::

    curl -X POST -H 'Content-Type: application/json' -d '{"data_type": "phenopacket", "query": {"query": {"match": {"gender": "FEMALE"}}}}' http://127.0.0.1:8000/private/fhir-search


