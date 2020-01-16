# CHORD Metadata Service

![Build Status](https://api.travis-ci.com/c3g/chord_metadata_service.svg?branch=master)
[![codecov](https://codecov.io/gh/c3g/chord_metadata_service/branch/master/graph/badge.svg)](https://codecov.io/gh/c3g/chord_metadata_service)

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

### Note On Permissions

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

## Developing

### Branching

All new feature requests and non-critical bug fixes should be merged into the
`develop` branch. `develop` is treated as a "nightly" version. Releases are
created from `develop`-to-`master` merges; patch-release work can be branched
out and tagged from the tagged major/minor release in `master`.

### Tests

Tests are located in tests directory in an individual app folder.

Run all tests for the whole project:

`python manage.py test`

Run tests for an individual app, e.g.:

`python manage.py test chord_metadata_service.phenopackets.tests.test_api`

Create coverage html report:

`coverage run manage.py test`

`coverage html`

### Accessing the Django Shell from inside a CHORD Container

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
