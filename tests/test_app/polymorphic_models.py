from django.db import models
from polymorphic.models import PolymorphicModel

from django_hashids.field import HashidField


class Project(PolymorphicModel):
    # hashid = HashidField()
    topic = models.CharField(max_length=30)


class ArtProject(Project):
    hashid = HashidField(min_length=6)
    artist = models.CharField(max_length=30)


class ResearchProject(Project):
    hashid = HashidField(min_length=6)
    supervisor = models.CharField(max_length=30)
