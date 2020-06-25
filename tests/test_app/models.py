from django.db.models import Model
from hashids import Hashids

from django_hashids import HashidsField


class TestModel(Model):
    hashid = HashidsField(real_field_name="id")


class TestModelWithDifferentConfig(Model):
    hashid = HashidsField(salt="AAA", min_length=5, alphabet="OPQRST1234567890")


this_hashids_instance = Hashids(salt="FOO")


class TestModelWithOwnInstance(Model):
    hashid = HashidsField(hashids_instance=this_hashids_instance)
