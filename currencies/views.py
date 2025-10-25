from rest_framework import viewsets, permissions
from .serializers import CurrencySerializer
from .models import Currency

class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [permissions.IsAuthenticated]
