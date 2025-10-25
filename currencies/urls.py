from django.urls import path, include
from rest_framework.routers import DefaultRouter
from currencies.views import CurrencyViewSet

router = DefaultRouter()
router.register(r"", CurrencyViewSet, basename="currency")

urlpatterns = [
    path("", include(router.urls)),
]