from django.conf import settings
from django.core.exceptions import FieldError
from django.db.models import Field
from django.utils.functional import cached_property
from hashids import Hashids

from .exceptions import ConfigError


class HashidsField(Field):
    concrete = False
    allowed_lookups = ("exact", "iexact", "in", "gt", "gte", "lt", "lte", "isnull")
    # these should never change, even when Hashids updates
    ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    MIN_LENGTH = 0

    def __init__(
        self,
        real_field_name="id",
        *args,
        hashids_instance=None,
        salt=None,
        alphabet=None,
        min_length=None,
        **kwargs
    ):
        kwargs.pop("editable", None)
        super().__init__(*args, editable=False, **kwargs)
        self.real_field_name = real_field_name
        self.salt = salt
        self.min_length = min_length
        self.alphabet = alphabet
        self._explicit_hashids_instance = hashids_instance

        self.hashids_instance = None
        self.attached_to_model = None

    def contribute_to_class(self, cls, name):
        self.attname = name
        self.name = name

        if getattr(self, "model", None) is None and cls._meta.abstract is False:
            self.model = cls

        if self.attached_to_model is not None:  # pragma: no cover
            raise FieldError(
                "Field '%s' is already attached to another model(%s)."
                % (self.name, self.attached_to_model)
            )
        self.attached_to_model = cls

        self.column = None

        if self.verbose_name is None:
            self.verbose_name = self.name

        setattr(cls, name, self)

        cls._meta.add_field(self, private=True)

        self.hashids_instance = self.get_hashid_instance()

    def get_hashid_instance(self):
        if self._explicit_hashids_instance:
            if (
                self.salt is not None
                or self.alphabet is not None
                or self.min_length is not None
            ):
                raise ConfigError(
                    "if hashids_instance is set, salt, min_length and alphabet should not be set"
                )
            return self._explicit_hashids_instance
        salt = self.salt
        min_length = self.min_length
        alphabet = self.alphabet
        if salt is None:
            salt = getattr(settings, "DJANGO_HASHIDS_SALT")
        if min_length is None:
            min_length = (
                getattr(settings, "DJANGO_HASHIDS_MIN_LENGTH", None) or self.MIN_LENGTH
            )
        if alphabet is None:
            alphabet = (
                getattr(settings, "DJANGO_HASHIDS_ALPHABET", None) or self.ALPHABET
            )
        return Hashids(salt=salt, min_length=min_length, alphabet=alphabet)

    def get_prep_value(self, value):
        decoded_values = self.hashids_instance.decode(value)
        if not decoded_values:
            return None
        return decoded_values[0]

    def from_db_value(self, value, expression, connection, *args):
        return self.hashids_instance.encode(value)

    def get_col(self, alias, output_field=None):
        if output_field is None:
            output_field = self
        col = self.real_col.get_col(alias, output_field)
        return col

    @cached_property
    def real_col(self):
        return next(
            col
            for col in self.attached_to_model._meta.fields
            if col.name == self.real_field_name or col.attname == self.real_field_name
        )

    def __get__(self, instance, name=None):
        if not instance:
            return self
        real_value = getattr(instance, self.real_field_name, None)
        # the instance is not saved yet?
        if real_value is None:
            return ""
        assert isinstance(real_value, int)
        return self.hashids_instance.encode(real_value)

    def __set__(self, instance, value):
        pass

    def __deepcopy__(self, memo=None):
        new_instance = super().__deepcopy__(memo)
        for attr in ("hashids_instance", "attached_to_model"):
            if hasattr(new_instance, attr):
                setattr(new_instance, attr, None)
        # remove cached values from cached_property
        for key in ("real_col",):
            if key in new_instance.__dict__:
                del new_instance.__dict__[key]  # pragma: no cover
        return new_instance

    @classmethod
    def get_lookups(cls):
        all_lookups = super().get_lookups()
        return {k: all_lookups[k] for k in cls.allowed_lookups}


HashidField = HashidsField
