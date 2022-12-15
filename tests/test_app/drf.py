from rest_framework import serializers, viewsets

from .models import TestModel

# Serializers define the API representation.
class TestModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TestModel
        fields = ['id', 'hashid']

# ViewSets define the view behavior.
class TestModelViewSet(viewsets.ModelViewSet):
    lookup_field = "hashid"
    queryset = TestModel.objects.all()
    serializer_class = TestModelSerializer