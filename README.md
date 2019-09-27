# Metadata service

## Install

The service uses PostgreSQL database for data storage.

1. Create and activate virtual environment
2. Run: `pip install -r requirements.txt`
3. Configure database connection in settings.py

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

4. Run:

`python manage.py makemigrations`

`python manage.py migrate`

`python manage.py runserver`

5. Development server runs at http://127.0.0.1:8000/