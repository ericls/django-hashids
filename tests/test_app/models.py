from django.contrib.auth.models import AbstractUser
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


class TestUser(AbstractUser):
    hashid = HashidsField(real_field_name="id")


class TestBase(Model):
    class Meta:
        abstract = True

    hashid = HashidsField()


class InheritanceModel(TestBase):
    hashid = HashidsField(min_length=20)


class InheritanceModel2(TestBase):
    pass


from .polymorphic_models import *