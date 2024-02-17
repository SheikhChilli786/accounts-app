import dj_database_url
from .common import *
import os
DEBUG = False
ALLOWED_HOSTS = ['*']

SECRET_KEY = os.environ['SECRET_KEY']
DATABASES = {
    'default':dj_database_url.config()
    }