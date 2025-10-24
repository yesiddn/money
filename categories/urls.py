from django.urls import path, include
from rest_framework.routers import DefaultRouter
from categories.views import CategoryViewSet

router = DefaultRouter()
router.register(r"", CategoryViewSet, basename="category")

urlpatterns = [
    path("", include(router.urls)),
]