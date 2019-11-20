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
