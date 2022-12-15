import pytest


pytestmark = pytest.mark.django_db

def test_drf_serialize(client):
    from .test_app.models import TestModel
    instance = TestModel.objects.create()
    result = client.get(f"/api-drf/testModels/{instance.hashid}/")
    assert result.status_code == 200
    assert result.json()["hashid"] == instance.hashid