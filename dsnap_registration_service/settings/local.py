# flake8: noqa
import dj_database_url

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'Just a simple secret key for development'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

if not DATABASES['default']:
    DATABASES['default'] = dj_database_url.parse(
        'postgres:///dsnap_registration', conn_max_age=600)

WHITENOISE_AUTOREFRESH = True
