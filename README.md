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

The service doesn't set any authentication now.
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
