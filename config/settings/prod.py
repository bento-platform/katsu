#####################################################################
#                   PRODUCTION SETTINGS                             #
# Inherit from setting base.py. Contain only necessary settings to  #
# make the project run. Following:                                  #
# https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/ #
#####################################################################

from .dev import *

DEBUG = False

SECRET_KEY = os.environ.get("DJANGO_SECRET")

SECURE_HSTS_SECONDS = 3600  # Once confirm that all assets are served securely(i.e. HSTS didn’t break anything), increase this value

SECURE_SSL_REDIRECT = True

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True

SECURE_HSTS_PRELOAD = True
