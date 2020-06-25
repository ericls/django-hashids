SECRET_KEY = "1"
DEBUG = True
INSTALLED_APPS = [
    "tests.test_app",
]
MIDDLEWARE = []
ROOT_URLCONF = "tests.urls"
DJANGO_HASHIDS_SALT = "???!"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:",}}
