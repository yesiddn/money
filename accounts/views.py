from django.db.models import DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce
from rest_framework import permissions, viewsets
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

        accounts = (
            Account.objects.filter(user=user)
            .annotate(
                # de esta forma se evita usar cases when para mejor legibilidad
                # ingresos - (gastos + transferencias + inversiones)
                balance=Coalesce(
                    # Suma de ingresos
                    Sum("record__amount", filter=Q(record__typeRecord="income")),
                    Value(
                        0, output_field=DecimalField(max_digits=15, decimal_places=2)
                    ),
                )
                - Coalesce(
                    # Suma de gastos, transferencias e inversiones
                    Sum(
                        "record__amount",
                        filter=Q(
                            record__typeRecord__in=["expense", "transfer", "investment"]
                        ),
                    ),
                    Value(
                        0, output_field=DecimalField(max_digits=15, decimal_places=2)
                    ),
                )
            )
            .order_by("-created_at")
        )
        return accounts

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
