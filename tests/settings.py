import os

SECRET_KEY = "1"
DEBUG = True
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "tests.test_app",
]
MIDDLEWARE = []
ROOT_URLCONF = "tests.urls"
DJANGO_HASHIDS_SALT = "???!"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:",}}
if os.environ.get("TEST_WITH_PG"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ["POSTGRES_DB"],
            "USER": os.environ["POSTGRES_USER"],
            "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        }
    }
