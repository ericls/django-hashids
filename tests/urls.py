from django.conf import settings
from django.urls import path, include

urlpatterns = []

if settings.DRF_INSTALLED:
    from rest_framework import routers
    from .test_app.drf import TestModelViewSet

    router = routers.DefaultRouter()
    router.register(r'testModels', TestModelViewSet)

    urlpatterns.append(
        path('api-drf/', include(router.urls)),
        # path('api-drf/', include('rest_framework.urls'))
    )
