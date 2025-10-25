from rest_framework import viewsets, permissions
from .models import Account
from .serializers import AccountSerializer


class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet para Account.

    - Permite listar/recuperar/crear/actualizar/borrar cuentas.
    - El queryset está restringido al usuario autenticado.
    - Al crear, el campo `user` se establece desde request.user.
    """

    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Account.objects.filter(user=user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
