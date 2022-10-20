from django.contrib.auth.models import AbstractUser
from django.db import models
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


class TestUserRelated(Model):
    hashid = HashidsField(real_field_name="id")

    user = models.ForeignKey("TestUser", related_name="related", on_delete=models.CASCADE)


class FirstSubClass(TestModel):
    pass


class SecondSubClass(FirstSubClass):
    pass


class TestAbstractModel(models.Model):
    hashid = HashidsField(real_field_name="id")

    class Meta:
        abstract = True


class ModelA(TestAbstractModel):
    pass


class ModelB(ModelA):
    pass
