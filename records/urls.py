from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import RecordViewSet

router = DefaultRouter()
router.register(r"", RecordViewSet, basename="record")

urlpatterns = [
    path("", include(router.urls)),
]
