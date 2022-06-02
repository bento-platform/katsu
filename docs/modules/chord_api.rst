CHORD API
=========

Data types endpoints
--------------------

**Projects**

:code:`api/projects` GET: list of Projects

:code:`api/projects/{id}` GET: single Project

**Datasets**

:code:`api/datasets` GET: list of Datasets

:code:`api/datasets/{id}` GET: single Dataset

**Table ownerships**

:code:`api/table_ownership` GET: list of Table ownerships

:code:`api/table_ownership/{id}` GET: single Table ownership

**Tables**

:code:`api/tables` GET: list of Tables

:code:`api/tables/{id}` GET: single Table

or

:code:`tables` GET: list of Tables

:code:`tables/{id}` GET: single Table

:code:`tables/{id}/summary` GET: summary about data in the table

:code:`tables/{id}/search` POST: query data in the table


Schemas for Data types
----------------------

:code:`data-types` GET: list of all data types available for ingestion

:code:`data-types/{data_type_name}` GET: single data type schema

For example: :code:`data-types/experiment`

:code:`data-types/{data_type_name}/schema` GET: same as above but just data type schema, without data type id


Private search endpoints
------------------------

:code:`private/search` POST: returns phenopackets that fit the conditions, works on all phenopackets in database

:code:`private/tables/{id}/search` POST: returns phenopackets from a specified table that fit the conditions

Example of POST request to search for all phenopackets that have disease Carcinoma

.. code-block:: json

    {
        "data_type": "phenopacket",
        "query": ["#ico", ["#resolve", "diseases", "[item]", "term", "label"], "Carcinoma"]
    }

Example of POST request to search for all experiments that have experiments results in VCF format

.. code-block:: json

    {
        "data_type": "experiment",
        "query": ["#eq", ["#resolve", "experiment_results", "[item]", "file_format"], "VCF"]
    }

Ingest endpoint
---------------

:code:`private/ingest` POST: ingests data  to database

Example of POST request to ingest phenopackets file

.. code-block:: json

    {
      "table_id": "{table_id}",
      "workflow_id": "phenopackets_json",
      "workflow_params": {
        "phenopacket_json.json_document": "path/phenopackets.json"
      },
      "workflow_outputs": {
        "json_document": "path/path.json"
      }
    }

Example of POST request to ingest experiments file

.. code-block:: json

    {
      "table_id": "{table_id}",
      "workflow_id": "experiments_json",
      "workflow_params": {
        "experiments_json.json_document": "path/experiments.json"
      },
      "workflow_outputs": {
        "json_document": "path/experiments.json"
      }
    }

Example of POST request to ingest mcodepackets file

.. code-block:: json

    {
      "table_id": "{table_id}",
      "workflow_id": "mcode_json",
      "workflow_params": {
        "mcode_json.json_document": "path/mcodepackets.json"
      },
      "workflow_outputs": {
        "json_document": "path/mcodepackets.json"
      }
    }

Export endpoint
---------------

:code:`private/export` POST: retrieves data from database

Example of POST request to retrieve data formatted in cbioportal format

.. code-block:: json

    {
      "format": "cbioportal",
      "object_type": "dataset",
      "object_id": "{dataset_id}",
      "output_path": "{path_to_local_directory_optional}"
    }

Workflows endpoints
-------------------

:code:`workflows` GET: list of all available workflows

:code:`workflows/{slug:workflow_id}` GET: single workflow schema

:code:`workflows/{slug:workflow_id}.wdl` GET: returns a wdl file for a given workflow
