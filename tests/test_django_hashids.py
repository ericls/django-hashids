import os

import pytest
from django import setup
from django.db.models import ExpressionWrapper, F, IntegerField
from django.test import override_settings
from hashids import Hashids

from django_hashids.exceptions import ConfigError, RealFieldDoesNotExistError

os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"
setup()

pytestmark = pytest.mark.django_db


def test_can_get_hashids():
    from django.conf import settings
    from tests.test_app.models import TestModel

    instance = TestModel.objects.create()
    hashid = instance.hashid
    hashids_instance = Hashids(salt=settings.DJANGO_HASHIDS_SALT)
    assert hashids_instance.decode(hashid)[0] == instance.pk


def test_can_get_field_from_model():
    from tests.test_app.models import TestModel

    TestModel.hashid


def test_can_use_per_field_config():
    from tests.test_app.models import TestModelWithDifferentConfig

    instance = TestModelWithDifferentConfig.objects.create()
    hashid = instance.hashid
    hashids_instance = Hashids(salt="AAA", min_length=5, alphabet="OPQRST1234567890")
    assert hashids_instance.decode(hashid)[0] == instance.pk


def test_can_use_per_field_instance():
    from tests.test_app.models import TestModelWithOwnInstance, this_hashids_instance

    instance = TestModelWithOwnInstance.objects.create()
    assert this_hashids_instance.decode(instance.hashid)[0] == instance.pk


def test_throws_when_setting_both_instance_and_config():
    from django.db.models import Model
    from tests.test_app.models import this_hashids_instance
    from django_hashids import HashidsField

    with pytest.raises(ConfigError):

        class Foo(Model):
            class Meta:
                app_label = "tests.test_app"

            hash_id = HashidsField(
                salt="Anotherone", hashids_instance=this_hashids_instance
            )


def test_updates_when_changing_real_column_value():
    from django.conf import settings
    from tests.test_app.models import TestModel

    instance = TestModel.objects.create()
    instance.id = 3
    # works before saving
    hashids_instance = Hashids(salt=settings.DJANGO_HASHIDS_SALT)
    assert hashids_instance.decode(instance.hashid)[0] == 3
    # works after saving
    instance.save()
    hashids_instance = Hashids(salt=settings.DJANGO_HASHIDS_SALT)
    assert hashids_instance.decode(instance.hashid)[0] == 3


def test_ignores_changes_to_value():
    from django.conf import settings
    from tests.test_app.models import TestModel

    instance = TestModel.objects.create()
    instance.id = 3
    instance.hashid = "FOO"

    hashids_instance = Hashids(salt=settings.DJANGO_HASHIDS_SALT)
    assert hashids_instance.decode(instance.hashid)[0] == 3
    # works after saving
    instance.save()

    instance.hashid = "FOO"
    hashids_instance = Hashids(salt=settings.DJANGO_HASHIDS_SALT)
    assert hashids_instance.decode(instance.hashid)[0] == 3


def test_can_use_exact_lookup():
    from tests.test_app.models import TestModel

    instance = TestModel.objects.create()
    got_instance = TestModel.objects.filter(hashid=instance.hashid).first()
    assert instance == got_instance
    # assert id field still works
    got_instance = TestModel.objects.filter(id=instance.id).first()
    assert instance == got_instance


def test_can_use_in_lookup():
    from tests.test_app.models import TestModel

    instance = TestModel.objects.create()
    instance2 = TestModel.objects.create()
    hashids = [instance.hashid, instance2.hashid]
    qs = TestModel.objects.filter(hashid__in=hashids)
    assert set([instance, instance2]) == set(qs)


def test_can_use_lookup_when_value_does_not_exists():
    # https://github.com/ericls/django-hashids/issues/4
    from tests.test_app.models import TestModel

    # exact lookup
    instance = TestModel.objects.create()
    hashid = instance.hashid + "A"
    qs = TestModel.objects.filter(hashid=hashid)
    assert list(qs) == []

    # lookup
    instance = TestModel.objects.create()
    instance2 = TestModel.objects.create()
    hashids = [instance.hashid + "A", instance2.hashid + "A"]
    qs = TestModel.objects.filter(hashid__in=hashids)
    assert list(qs) == []


def test_can_use_lt_gt_lte_gte_lookup():
    from tests.test_app.models import TestModel

    instance = TestModel.objects.create()
    instance2 = TestModel.objects.create()
    qs = TestModel.objects.filter(hashid__lt=instance2.hashid)
    assert set([instance]) == set(qs)
    qs = TestModel.objects.filter(hashid__lte=instance2.hashid)
    assert set([instance, instance2]) == set(qs)
    qs = TestModel.objects.filter(hashid__gt=instance.hashid)
    assert set([instance2]) == set(qs)
    qs = TestModel.objects.filter(hashid__gte=instance.hashid)
    assert set([instance, instance2]) == set(qs)


def test_can_get_values():
    from tests.test_app.models import TestModel

    instance = TestModel.objects.create()
    instance2 = TestModel.objects.create()

    hashids = TestModel.objects.values("hashid")
    assert set([instance, instance2]) == set(
        TestModel.objects.filter(hashid__in=hashids)
    )
    hashids = list(TestModel.objects.values_list("hashid", flat=True))
    assert set([instance, instance2]) == set(
        TestModel.objects.filter(hashid__in=hashids)
    )
    # assert id field still works
    ids = list(TestModel.objects.values_list("id", flat=True))
    assert set([instance, instance2]) == set(TestModel.objects.filter(id__in=ids))


def test_can_select_as_integer():
    from tests.test_app.models import TestModel

    instance = TestModel.objects.create()
    instance2 = TestModel.objects.create()

    integer_ids = list(
        TestModel.objects.annotate(
            hid=ExpressionWrapper(F("hashid"), output_field=IntegerField())
        ).values_list("hid", flat=True)
    )
    assert set([instance.id, instance2.id]) == set(integer_ids)


@override_settings(DJANGO_HASHIDS_MIN_LENGTH=10)
def test_can_use_min_length_from_settings():
    from tests.test_app.models import TestModel

    TestModel.hashid.hashids_instance = None
    TestModel.hashid.hashids_instance = TestModel.hashid.get_hashid_instance()

    instance = TestModel.objects.create()
    assert len(instance.hashid) >= 10


def test_can_use_min_length_from_settings():
    with override_settings(DJANGO_HASHIDS_ALPHABET='!@#$%^&*(){}[]:"'):
        from tests.test_app.models import TestModel

        TestModel.hashid.hashids_instance = None
        TestModel.hashid.hashids_instance = TestModel.hashid.get_hashid_instance()

        instance = TestModel.objects.create()
    assert all(c in '!@#$%^&*(){}[]:"' for c in instance.hashid)

    TestModel.hashid.hashids_instance = None
    TestModel.hashid.hashids_instance = TestModel.hashid.get_hashid_instance()
    


def test_not_saved_instance():
    from tests.test_app.models import TestModel

    instance = TestModel()
    assert instance.hashid == ""


def test_create_user():
    # https://github.com/ericls/django-hashids/issues/2
    from tests.test_app.models import TestUser

    u = TestUser.objects.create_user("username", password="password")
    assert TestUser.hashid.hashids_instance.decode(u.hashid)[0] == u.id


def test_multiple_level_inheritance():
    # https://github.com/ericls/django-hashids/issues/25
    from tests.test_app.models import SecondSubClass, FirstSubClass

    instance = SecondSubClass.objects.create()
    SecondSubClass.objects.filter(id=1).first() == SecondSubClass.objects.filter(
        hashid=instance.hashid
    ).first()

    instance = FirstSubClass.objects.create()
    FirstSubClass.objects.filter(id=1).first() == FirstSubClass.objects.filter(
        hashid=instance.hashid
    ).first()


def test_multiple_level_inheritance_from_abstract_model():
    # https://github.com/ericls/django-hashids/issues/25
    from tests.test_app.models import ModelB, ModelA

    instance = ModelB.objects.create()
    ModelB.objects.filter(id=1).first() == ModelB.objects.filter(
        hashid=instance.hashid
    ).first()

    instance = ModelA.objects.create()
    ModelA.objects.filter(id=1).first() == ModelA.objects.filter(
        hashid=instance.hashid
    ).first()


def test_related_queries():

    from tests.test_app.models import TestUser, TestUserRelated

    u = TestUser.objects.create()
    r = TestUserRelated.objects.create(user=u)

    assert TestUserRelated.objects.filter(user__hashid=u.hashid).first() == r
    assert TestUser.objects.filter(related__hashid=r.hashid).first() == u


def test_using_pk_as_real_field_name():
    # https://github.com/ericls/django-hashids/issues/31
    from tests.test_app.models import ModelUsingPKAsRealFieldName

    a = ModelUsingPKAsRealFieldName.objects.create()
    assert a.hashid
    assert ModelUsingPKAsRealFieldName.objects.get(hashid=a.hashid) == a
    assert ModelUsingPKAsRealFieldName.objects.get(hashid__lte=a.hashid) == a
    assert (
        ModelUsingPKAsRealFieldName.objects.filter(hashid__lt=a.hashid).exists()
        is False
    )


def test_no_real_field_error_message():
    from django.db.models import Model
    from django_hashids import HashidsField

    class Foo(Model):
        class Meta:
            app_label = "tests.test_app"

        hash_id = HashidsField(real_field_name="does_not_exist")

    with pytest.raises(RealFieldDoesNotExistError):
        Foo.objects.filter(hash_id="foo")
