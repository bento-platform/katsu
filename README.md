# Katsu Metadata Service

![Test Status](https://github.com/bento-platform/katsu/workflows/Test/badge.svg)
![Lint Status](https://github.com/bento-platform/katsu/workflows/Lint/badge.svg)
[![codecov](https://codecov.io/gh/bento-platform/katsu/branch/master/graph/badge.svg)](https://codecov.io/gh/bento-platform/katsu)

<img src="docs/_static/katsu_logo_final.png" width="298" height="50" alt="Katsu logo" />

A Phenopackets-based clinical and phenotypic metadata service for the Bento platform.


## Table of Contents

- [Katsu Metadata Service](#katsu-metadata-service)
  - [Table of Contents](#table-of-contents)
  - [License](#license)
  - [Funding](#funding)
  - [Architecture](#architecture)
  - [REST API highlights](#rest-api-highlights)
  - [Install](#install)
    - [Install via Docker](#install-via-docker)
  - [Environment Variables](#environment-variables)
  - [Standalone PostGres db and AdMiner](#standalone-postgres-db-and-adminer)
  - [Authentication](#authentication)
    - [Note on Permissions](#note-on-permissions)
    - [Authorization inside CanDIG](#authorization-inside-candig)
  - [Developing](#developing)
    - [Branching](#branching)
    - [Tests](#tests)
    - [Terminal Commands](#terminal-commands)
      - [Project/Dataset/Table/Ingestion Commands](#projectdatasettableingestion-commands)
      - [Patient Commands](#patient-commands)
      - [Phenopacket Commands](#phenopacket-commands)
    - [Accessing the Django Shell from inside a Bento Container](#accessing-the-django-shell-from-inside-a-bento-container)
      - [When running Katsu with `bentoV2`:](#when-running-katsu-with-bentov2)
      - [When running Katsu with `chord_singularity` (DEPRECATED)](#when-running-katsu-with-chord_singularity-deprecated)
  - [Configuring public overview and public search fields](#configuring-public-overview-and-public-search-fields)

## License

The majority of the Katsu Metadata Service is licensed under the LGPLv3 license; copyright (c) 2019-2023 the Canadian
Centre for Computational Genomics.

Portions are copyright (c) 2019 Julius OB Jacobsen, Peter N Robinson, Christopher J Mungall (Phenopackets); licensed
under the BSD 3-clause license.

## Funding

CANARIE funded initial development of the Katsu Metadata service under the CHORD project.

## Architecture

Katsu Metadata Service is a service to store epigenomic metadata.

1. Patients service handles anonymized individual’s data (individual id, sex, age or date of birth)
    * Data model: aggregated profile from GA4GH Phenopackets Individual, and FHIR Patient.

2. Phenopackets service handles phenotypic and clinical data
    * Data model: [GA4GH Phenopackets schema](https://github.com/phenopackets/phenopacket-schema)

3. Experiments service handles experiment related data.
    * Data model: derived from 
      [IHEC Metadata Experiment](https://github.com/IHEC/ihec-ecosystems/blob/master/docs/metadata/2.0/Ihec_metadata_specification.md#experiments)

4. Resources service handles metadata about ontologies used for data annotation.
    * Data model: derived from Phenopackets Resource profile

5. CHORD service  handles metadata about dataset, has relation to phenopackets (one dataset can have many phenopackets)
    * Data model: [DATS](https://github.com/datatagsuite)  + [GA4GH DUO](https://github.com/EBISPOT/DUO)

6. Rest api service handles all generic functionality shared among other services


## REST API highlights

* Swagger schema docs can be found 
  [here](https://editor.swagger.io/?url=https://raw.githubusercontent.com/bento-platform/katsu/develop/swagger_schema.json).

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
* Install Poetry (for dependency management) in the virtual environment: `pip install poetry`
* Install dependencies with `poetry install`
* To configure the application (such as the DB credentials) we are using python-dotenv:
    - Take a look at the .env-sample file at the root of the project
    - You can export these in your virtualenv or simply `cp .env-sample .env`
    - `python-dotenv` can handle either (a local .env will override environment variables though)


* Run:

```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

* Development server runs at `localhost:8000`


### Install via Docker

Optionally, you may also install standalone Katsu with the Dockerfile provided. If you develop or deploy Katsu as 
part of the Bento platform, you should use Bento's Docker 
[image](https://github.com/bento-platform/katsu/pkgs/container/katsu) instead.



## Environment Variables

Katsu uses several environment variables to configure relevant settings. Below are some:

```bash
# Secret key for sessions; use a securely random value in production
SERVICE_SECRET_KEY=...

# true or false; debug mode enables certain error pages and logging but can leak secrets, DO NOT use in production!
KATSU_DEBUG=true  # or BENTO_DEBUG or CHORD_DEBUG

# Mandatory for accepting ingests; temporary directory 
KATSU_TEMP=  # or SERVICE_TEMP

# Configurable human-readable/translatable name for phenopacket data type (e.g. Clinical Data)
KATSU_PHENOPACKET_LABEL="Clinical Data"

# DRS URL for fetching ingested files
DRS_URL=

# Database configuration
POSTGRES_DATABASE=metadata
POSTGRES_USER=admin
#  - If set, will be used instead of POSTGRES_PASSWORD to get the database password.
POSTGRES_PASSWORD_FILE=
POSTGRES_PASSWORD=admin
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# CHORD/Bento-specific variables:
#  - If set, used for setting an allowed host & other API-calling purposes
CHORD_URL=
#  - If true, will enforce permissions. Do not run with this not set to true in production! 
#    Defaults to (not DEBUG)
CHORD_PERMISSIONS=

# CanDIG-specific variables:
CANDIG_AUTHORIZATION=
CANDIG_OPA_URL=
CANDIG_OPA_SECRET=
CANDIG_OPA_SITE_ADMIN_KEY=
INSIDE_CANDIG=
```

## Standalone Postgres db and Adminer

For local development, you can quickly deploy a local database server (Postgres) and management tool (Adminer) with 
`docker compose`. Make sure your Postgres env variables are set in `.env` before running:

```
# Start docker compose containers
docker compose -f docker-compose.dev.yaml up -d

# Stop and remove docker-compose containers
docker compose -f docker-compose.dev.yaml down
```

You can now use the katsu-db container (`localhost:5432`) as your database for standalone katsu development and 
explore the database tables with adminer (`localhost:8080`).
Login to adminer by specifying the following on the login page:

- **System:** `PostgreSQL`
- **Server:** `katsu-db` (host and port are resolved by Docker with the container name)
- **Username:** `POSTGRES_USER`
- **Password:** `POSTGRES_PASSWORD`
- **Database:** `POSTGRES_DATABASE`

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

### Developing and debugging inside a container with VS Code (*Bento*)

The development Docker image includes metadata for the 
[`devcontainer.json`](https://code.visualstudio.com/docs/devcontainers/attach-container)
specification. Using VS Code, you can attach to a running instance of a `*-dev` Katsu container
and launch the `Attach Debugger (Bento)` task to set breakpoints and step through code, as well
as interacting with and Git-committing inside the container via a remote terminal using the 
pre-configured `bento_user` user, if the `BENTO_GIT_NAME` and `BENTO_GIT_EMAIL` environment
variables are set.

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
The implementation of public APIs relies on a project customized configuration file `config.json` that must be placed in 
the base directory.  Currently, there is an `example.config.json` located  in `/katsu/chord_metadata_service` directory 
which is set to be the project base directory. The file can be copied, renamed to `config.json` and modified.

The `config.json` contains fields that data providers would like to make open for public access.
If the `config.json` is not set up/created it means there is no public data and no data will be available via 
these APIs.

Refer to the documentation for a detailed description of the config file and
public API endpoints.
