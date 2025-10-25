from rest_framework import viewsets, permissions
from .models import Record
from .serializers import RecordSerializer


class RecordViewSet(viewsets.ModelViewSet):
    """ViewSet para Record.

    - Restringe queryset a los records del usuario autenticado.
    - Asigna `user` en create.
    """

    serializer_class = RecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Record.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
