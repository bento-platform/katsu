# Katsu Metadata Service

![Test Status](https://github.com/bento-platform/katsu/workflows/Test/badge.svg)
![Lint Status](https://github.com/bento-platform/katsu/workflows/Lint/badge.svg)
[![codecov](https://codecov.io/gh/bento-platform/katsu/branch/master/graph/badge.svg)](https://codecov.io/gh/bento-platform/katsu)

## Table of Contents

  * [License](#license)
  * [Funding](#funding)
  * [Architecture](#architecture)
  * [REST API Highlights](#rest-api-highlights)
  * [Install](#install)
  * [Authentication](#authentication)
     * [Note on Permissions](#note-on-permissions)
     * [Authorization inside CanDIG](#authorization-inside-candig)
  * [Developing](#developing)
     * [Branching](#branching)
     * [Tests](#tests)
     * [Terminal Commands](#terminal-commands)
        * [Project/Dataset/Table/Ingestion Commands](#projectdatasettableingestion-commands)
        * [Patient Commands](#patient-commands)
        * [Phenopacket Commands](#phenopacket-commands)
     * [Accessing the Django Shell from inside a Bento Container](#accessing-the-django-shell-from-inside-a-bento-container)
  * [Configuring Public overview and public search fields](#configuring-public-overview-and-public-search-fields)
     * [Config file specification](#config-file-specification)
     * [Public APIs](#public-apis)

## License

The majority of the Katsu Metadata Service is licensed under the LGPLv3 license; copyright (c) 2019-2020 the Canadian
Centre for Computational Genomics.

Portions are copyright (c) 2019 Julius OB Jacobsen, Peter N Robinson, Christopher J Mungall (Phenopackets); licensed
under the BSD 3-clause license.

## Funding

CANARIE funded initial development of the Katsu Metadata service under the CHORD project.

## Architecture

Katsu Metadata Service is a service to store epigenomic metadata.

1. Patients service handles anonymized individual’s data (individual id, sex, age or date of birth)
    * Data model: aggregated profile from GA4GH Phenopackets Individual, FHIR Patient and mCODE Patient.

2. Phenopackets service handles phenotypic and clinical data
    * Data model: [GA4GH Phenopackets schema](https://github.com/phenopackets/phenopacket-schema)

3. mCode service handles patient's oncology related data.
    * Data model: [mCODE data elements](https://mcodeinitiative.org/)

4. Experiments service handles experiment related data.
    * Data model: derived from [IHEC Metadata Experiment](https://github.com/IHEC/ihec-ecosystems/blob/master/docs/metadata/2.0/Ihec_metadata_specification.md#experiments)

5. Resources service handles metadata about ontologies used for data annotation.
    * Data model: derived from Phenopackets Resource profile

6. CHORD service  handles metadata about dataset, has relation to phenopackets (one dataset can have many phenopackets)
    * Data model: [DATS](https://github.com/datatagsuite)  + [GA4GH DUO](https://github.com/EBISPOT/DUO)

7. Rest api service handles all generic functionality shared among other services


## REST API highlights

* Standard api delivers data in snake_case.
To retrieved data in json compliant with phenopackets that uses camelCase append `?format=phenopackets` .

* Data can be ingested and retrieved in snake_case or camelCase.

* Other available renderers:
Phenopackets model is mapped to [FHIR](https://www.hl7.org/fhir/) using
[Phenopackets on FHIR](https://aehrc.github.io/fhir-phenopackets-ig/) implementation guide.
To retrieve data in fhir append `?format=fhir` .

* Ingest endpoint: `/private/ingest`.


## Install

Install the git submodule for DATS JSON schemas (if you did not clone recursively):

```
git submodule update --init
```

The service uses PostgreSQL database for data storage.

* Create and activate virtual environment
* Run: `pip install -r requirements.txt`
* To configure the application (such as the DB credentials) we are using python-dotenv:
    - Take a look at the .env-sample file at the root of the project
    - You can export these in your virtualenv or simply `cp .env-sample .env`
    - python-dotenv can handle either (a local .env will override env vars though)


* Run:

```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

* Development server runs at `localhost:8000`


### Install via Docker

Optionally, you may also install standalone Katsu with the Dockerfile provided. If you develop or
deploy Katsu as part of the Bento platform, you should use Bento's Docker image instead.


## Authentication

Default authentication can be set globally in `settings.py`

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
    	'rest_framework.authentication.BasicAuthentication',
    	'rest_framework.authentication.SessionAuthentication',
    ]
}
# ...
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]
```

By default, the service ships with a custom remote user middleware and backend
compatible with the CHORD project. This middleware isn't particularly useful
for a standalone instance of this server, so it can be swapped out.

### Note on Permissions

By default, `katsu` uses the CHORD permission system, which
functions as follows:

  * The service assumes that an **out-of-band** mechanism (such as a 
    properly-configured reverse proxy) protects URLs under the `/private` 
    namespace.
  * Requests with the headers `X-User` and `X-User-Role` can be authenticated
    via a Django Remote User-type system, with `X-User-Role: owner` giving
    access to restricted endpoints and `X-User-Role: user` giving less trusted,
    but authenticated, access.

This can be turned off with the `CHORD_PERMISSIONS` environment variable and/or
Django setting, or with the `AUTH_OVERRIDE` Django setting.

### Authorization inside CanDIG

When ran inside the CanDIG context, to properly implement authorization you'll
have to do the following:

1. Make sure the CHORD_PERMISSIONS is set to "false".
2. Set CANDIG_AUTHORIZATION to "OPA".
3. Configure CANDIG_OPA_URL and CANDIG_OPA_SECRET.


## Developing

### Branching

All new feature requests and non-critical bug fixes should be merged into the
`develop` branch. `develop` is treated as a "nightly" version. Releases are
created from `develop`-to-`master` merges; patch-release work can be branched
out and tagged from the tagged major/minor release in `master`.

### Tests

Each individual Django app folder within the project contains relevant tests
(if applicable) in the `tests` directory.

Run all tests and linting checks for the whole project:

```bash
tox
```

Run all tests for the whole project:

```bash
python manage.py test
```

Run tests for an individual app, e.g.:

```bash
python manage.py test chord_metadata_service.phenopackets.tests.test_api
```

Test and create `coverage` HTML report:

```bash
tox
coverage html
```

### Terminal Commands

Katsu ships with a variety of command-line helpers to facilitate common actions
that one might perform. 

To run them, the Django `manage.py` script is used.

#### Project/Dataset/Table/Ingestion Commands

```
$ ./manage.py create_project "project title" "project description"
Project created: test (ID: 756a4530-59b7-4d47-a04a-c6ee5aa52565)
```

Creates a new project with the specified title and description text. Returns
output including the new ID for the project, which is needed when creating
datasets under the project.

```
$ ./manage.py list_projects
identifier         title  description       created                           updated
-----------------  -----  ----------------  --------------------------------  --------------------------------
756a4530-59b7-...  test   test description  2021-01-07 22:36:05.460537+00:00  2021-01-07 22:36:05.460570+00:00
```

Lists all projects currently in the system.

```
$ ./manage.py create_dataset \
  "dataset title" \
  "dataset description" \
  "David Lougheed <david.lougheed@example.org>" \
  "756a4530-59b7-4d47-a04a-c6ee5aa52565"  \
  ./examples/data_use.json
Dataset created: dataset title (ID: 2a8f8e68-a34f-4d31-952a-22f362ebee9e)
```

* `David Lougheed <david.lougheed@example.org>`: Dataset use contact information
* `756a4530-59b7-4d47-a04a-c6ee5aa52565`: Project ID to put the dataset under
* `./examples/data_use.json`: Path to data use JSON

Creates a new dataset under the project specified (with its ID), with 
corresponding title, description, contact information, and data use conditions.

```
$ ./manage.py list_project_datasets 756a4530-59b7-4d47-a04a-c6ee5aa52565
identifier                            title          description
------------------------------------  -------------  -------------------
2a8f8e68-a34f-4d31-952a-22f362ebee9e  dataset title  dataset description
```

Lists all datasets under a specified project.

```
$ ./manage.py create_table \
  "table name" \
  phenopacket \
  "2a8f8e68-a34f-4d31-952a-22f362ebee9e"
Table ownership created: dataset title (ID: 2a8f8e68-a34f-4d31-952a-22f362ebee9e) -> 0d63bafe-5d76-46be-82e6-3a07994bac2e
Table created: table name (ID: 0d63bafe-5d76-46be-82e6-3a07994bac2e, Type: phenopacket)
```

* `table name`: Name of the new table created
* `phenopacket`: Table data type (either `phenopacket` or `experiment`)
* `2a8f8e68-a34f-4d31-952a-22f362ebee9e`: Dataset ID to put the table under

Creates a new data table under the dataset specified (with its ID), with a 
corresponding name and data type (either `phenopacket` or `experiment`.)

```
$ ./manage.py list_dataset_tables 2a8f8e68-a34f-4d31-952a-22f362ebee9e
ownership_record__table_id  name        data_type    created                           updated
--------------------------  ----------  -----------  --------------------------------  --------------------------------
0d63bafe-5d76-46be-82e6...  table name  phenopacket  2021-01-08 15:09:52.346934+00:00  2021-01-08 15:09:52.346966+00:00
```

Lists all tables under a specified dataset.

```"
$ ./manage.py ingest \
  "0d63bafe-5d76-46be-82e6-3a07994bac2e" \
  ./examples/1000g_phenopackets_1_of_3.json
...
Ingested data successfully.
```

* `0d63bafe-5d76-46be-82e6-3a07994bac2e`: ID of table to ingest into
* `./examples/1000g_phenopackets_1_of_3.json`: Data to ingest (in the format 
  accepted by the Phenopackets workflow or the Experiments workflow, depending
  on the data type of the table)
  
#### Patient Commands

```
$ ./manage.py patients_build_index
...
```

Builds an ElasticSearch index for patients in the database.
  
#### Phenopacket Commands

```
$ ./manage.py phenopackets_build_index
...
```

Builds an ElasticSearch index for Phenopackets in the database.

### Accessing the Django Shell from inside a Bento Container

#### When running Katsu with `bentoV2`:

- Enter Katsu container
```
docker exec -it bentov2-katsu sh
```

- Activate django shell
```
python manage.py shell
```

From there, you can import models and query the database from the REPL.

```
from chord_metadata_service.patients.models import *
from chord_metadata_service.phenopackets.models import *
from chord_metadata_service.resources.models import *
from chord_metadata_service.experiments.models import *

# e.g.
Individual.objects.all().count()
Phenopacket.objects.all().count()
Resource.objects.all().count()
Experiment.objects.all().count()
```
#### When running Katsu with `chord_singularity` (DEPRECATED)

Assuming `chord_singularity` is being used, the following commands can be used
to bootstrap your way to a `katsu` environment within a Bento
container:

```bash
./dev_utils.py --node x shell
source /chord/services/metadata/env/bin/activate
source /chord/data/metadata/.environment
export $(cut -d= -f1 /chord/data/metadata/.environment)
DJANGO_SETTINGS_MODULE=chord_metadata_service.metadata.settings django-admin shell
```

## Configuring public overview and public search fields

There are several public APIs to return data overview and perform a search that returns only objects count.
The implementation of public APIs relies on a project customized configuration file `config.json` that must be placed in the base directory.
Currently, there is an `example.config.json` located  in `/katsu/chord_metadata_service` directory which is set to be the project base directory.
The file can be copied, renamed to `config.json` and modified.

The `config.json` contains fields that data providers would like to make open for public access.
If the `config.json` is not set up/created it means there is no public data and no data will be available via these APIs.

### Config file specification

The `config.json` follows jsonschema specifications: it includes fields from Katsu data model, defines their type and other attributes that determine how the data from these fields will be presented in the public response.

Jsonschema properties:

- `"type"` - defines a data type for this field, e.g. "number" or "string" (Katsu's config accepts only number and string types)
- `"format"` - defines a string format, e.g. "date" to record date in the format of "2021-12-31"
- `"enum"` - defines a list of options for this field
- `"title"` - field's user-friendly name
- `"description"` - field's description

Custom properties:

- `"bin_size"` (number) - defines a bin size for numeric fields (where "type" is set to "number"), by default bin size is set to 10
- `"queryable"` (true/false) - defines if the field should be included in search, if set to false the field will only be shown as a chart
- `"is_range"` (true/false) - defines if this field can  be searched using range search (e.g.min value and max value)
- `"chart"` (options: pie, bar)-  defines a type of the chart to be used to visualize the data
- `"taper_left"` and `"taper_right"` (number) - defines the cut-offs for the data to be shown in charts
- `"units"` (string) - defines unit value for numeric fields (e.g. "years", "mg/L")
- `"minimum"` (number) - defines the minimum value in this field
- `"maximum"` (number) - defines the maximum value in this field

Example of the `config.json`

```

    {
      "age": {
        "type": "number",
        "title": "Age",
        "bin_size": 10,
        "is_range": true,
        "queryable": true,
        "taper_left": 40,
        "taper_right": 60,
        "units": "years",
        "minimum": 0,
        "description": "Age at arrival"
      },
      "sex": {
        "type": "string",
        "enum": [
          "Male",
          "Female"
        ],
        "title": "Sex",
        "queryable": true,
        "description": "Sex at birth"
      },
      "extra_properties": {
        "date_of_consent": {
          "type": "string",
          "format": "date",
          "title": "Verbal consent date",
          "chart": "bar",
          "queryable": true,
          "description": "Date of initial verbal consent (participant, legal representative or tutor), yyyy-mm-dd"
        }
      }
    }
```


### Public APIs

The public APIs include the following endpoints:

 - `/api/public_search_fields` GET: returns `config.json` contents in a form of jsonschema.

   The response when public fields are not configured and config file is not provided: `{"message": "No public fields configured."}`


 - `/api/public_overview` GET: returns an overview that contains counts for each field of interest.

   The response when there is no public data available and config file is not provided: `{"message": "No public data available."}`


 - `/api/public`  GET: returns a count of all individuals in database.

   The response when there is no public data available and config file is not provided: `{"message": "No public data available."}`

   The response when there is no enough data that passes the project-custom threshold: `{"message": "Insufficient data available."}`
   When count is less or equal to a project's custom threshold returns message that insufficient data available.
   Accepts search filters on the fields that are specified in the :code:`config.json` file and set to "queryable".
   Currently, the following filters are written for the Individual model:

   - sex: e.g. `/api/public?sex=female`

   - age: search by age ranges e.g. `/api/public?age_range_min=20&age_range_max=30`

   - extra_properties: e.g. `/api/public?extra_properties=[{"smoking": "Non-smoker"},{"covidstatus": "positive"}]`
   
   The `extra_properties` is a JSONField without a schema.
   To allow searching content in this field the nested fields have to be added to the `config.json` file (see the config file example above).
   The query string must contain a list of objects where each object has a key-value pair representing a nested field name and a search value.
 
   ##### _Examples of extra properties searches_

    Search for items that have a type of string:

   ```
    /api/public?extra_properties=[{"smoking": "Non-smoker"},{"death_dc": "deceased"},{"covidstatus": "positive"}]
   ```
   Search for items that contain date ranges:

   ```
    /api/public?extra_properties=[{"date_of_consent": {"after": "2020-03-01", "before": "2021-05-01"}}]
   ```
   Search for items that contain numeric ranges:

   ```
    /api/public?extra_properties=[{"lab_test_result_value": {"rangeMin": 5, "rangeMax": 900}}]
   ```
   Examples of combining extra properties search with other fields:

   ```
    /api/public?sex=female&extra_properties=[{"covidstatus": "positive"}]
   ```
 