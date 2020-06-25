# Django Hashids

django-hashids is a simple and non-intrusive hashids library for Django. It acts as a model field, but it does not touch the database or change the model.

# Install

```bash
pip install django-hashids
```

# Usage

Add `HashidsField` to any model

```python
class TestModel(Model):
    hashid = HashidsField(real_field_name="id")
```

`TestModel.hashid` field will proxy `TestModel.id` field but all queries will return and receive hashids strings. `TestModel.id` will work as before.

## Examples

```python
instance = TestModel.objects.create()
instance2 = TestModel.objects.create()
instance.id  # 1
instance2.id  # 2

# Allows access to the field
instance.hashid  # '1Z'
instance2.hashid  # '4x'

# Allows querying by the field
TestModel.objects.get(hashid="1Z")
TestModel.objects.filter(hashid="1Z")
TestModel.objects.filter(hashid__in=["1Z", "4x"])
TestModel.objects.filter(hashid__gt="1Z")  # same as id__gt=1, would return instance 2

# Allows usage in queryset.values
TestModel.objects.values_list("hashid", flat=True) # ["1Z", "4x"]
TestModel.objects.filter(hashid__in=TestModel.objects.values("hashids"))

```

## Config

`DJANGO_HASHIDS_SALT` can be set in Django's settinigs to be used as the default salt.

`HashidsField` does not reqiure any arguments but the followinig arguments can be supplied to modify its behavior

| Name               |                        Description                        |
| ------------------ | :-------------------------------------------------------: |
| `real_field_name`  |                  The proxied field name                   |
| `hashids_instance` | The hashids instance used to encode/decode for this field |
| `salt`             |     The salt used for this field to generate hashids      |
| `min_length`       |  The minimum length of hashids generated for this field   |
| `alphabet`         |    The alphabet used by this field to generate hashids    |

The argument `hashids_instance` is mutually exclusive to `salt`, `min_length` and `alphabet`. See [hashids-python](https://github.com/davidaurelio/hashids-python) for more info about the arguments.
