# CHORD Metadata Service

![Build Status](https://api.travis-ci.com/c3g/chord_metadata_service.svg?branch=master)
[![codecov](https://codecov.io/gh/c3g/chord_metadata_service/branch/master/graph/badge.svg)](https://codecov.io/gh/c3g/chord_metadata_service)


## Architecture

CHORD Metadata Service is a service to store epigenomic metadata.

1. Patients service handles anonymized individual’s data (individual id, sex, age or date of birth)
* Data model: aggregated profile from GA4GH Phenopackets Individual and FHIR Patient

2. Phenopackets service handles phenotypic and clinical data
* Data model: [GA4GH Phenopackets schema](https://github.com/phenopackets/phenopacket-schema)

3. CHORD service  handles metadata about dataset, has relation to phenopackets (one dataset can have many phenopackets)
* Data model: [DATS](https://github.com/datatagsuite)  + [GA4GH DUO](https://github.com/EBISPOT/DUO)

4. Rest api service handles all generic functionality shared among other services


## REST API highlights

* Standard api delivers data in snake_case
To retrieved data in json compliant with phenopackets that uses camelCase append `?format=phenopackets`

* Data can be ingested and retrieved in snake_case or camelCase

* Other available renderers:
phenopackets model is mapped to [FHIR](https://www.hl7.org/fhir/) using [Phenopackets on FHIR](https://aehrc.github.io/fhir-phenopackets-ig/) implementation guide.
To retrieve data in fhir append `?format=fhir`

* Ingest endpoint: `/ingest`
Example of POST body is in chord/views_ingest.py (METADATA_WORKFLOWS)


## Install

The service uses PostgreSQL database for data storage.

* Create and activate virtual environment
* Run: `pip install -r requirements.txt`
* Configure database connection in settings.py

e.g. settings if running database on localhost, default port for PostgreSQL is 5432:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'database_name',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

* Run:

`python manage.py makemigrations`

`python manage.py migrate`

`python manage.py runserver`

* Development server runs at `localhost:8000`

## Authentication

Default authentication can be set globally in `settings.py`

```
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
    	'rest_framework.authentication.BasicAuthentication',
    	'rest_framework.authentication.SessionAuthentication',
    ]

}
```

## Tests

Tests are located in tests directory in an individual app folder.

Run all tests for the whole project:

`python manage.py test`

Run tests for an individual app, e.g.:

`python manage.py test chord_metadata_service.phenopackets.tests.test_api`

Create coverage html report:

`coverage run manage.py test`

`coverage html`

## Note On Permissions

By default, `chord_metadata_service` uses the CHORD permission system, which
functions as follows:

  * URLs under the `/private` namespace are assumed to be protected by an
    **out-of-band** mechanism such as a properly-configured reverse proxy.
  * Requests with the headers `X-User` and `X-User-Role` can be authenticated
    via a Django Remote User-type system, with `X-User-Role: owner` giving
    access to restricted endpoints and `X-User-Role: user` giving less trusted,
    but authenticated, access.

This can be turned off with the `CHORD_PERMISSIONS` environment variable and/or
Django setting, or with the `AUTH_OVERRIDE` Django setting.

## Accessing the Django Shell from inside a CHORD Container

Assuming `chord_singularity` is being used, the following commands can be used
to bootstrap your way to a `chord_metadata_service` environment within a CHORD
container:

```bash
./dev_utils.py --node x shell
source /chord/services/metadata/env/bin/activate
source /chord/data/metadata/.environment
export $(cut -d= -f1 /chord/data/metadata/.environment)
DJANGO_SETTINGS_MODULE=chord_metadata_service.metadata.settings django-admin shell
```

From there, you can import models and query the database from the REPL.
