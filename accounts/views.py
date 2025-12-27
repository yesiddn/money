from django.db.models import Case, DecimalField, F, Sum, Value, When
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
            # annotate agrega este campo dinámico 'balance'
            .annotate(
                # coalesce devuelve el primer valor no nulo (en este caso, si no hay registros, devuelve 0)
                balance=Coalesce(
                    # Suma de amounts ajustando signo según typeRecord
                    Sum(
                        # lógica para ajustar el signo del amount
                        Case(
                            # gastos, transferencias e inversiones son negativas
                            When(
                                record__typeRecord__in=[
                                    "expense",
                                    "transfer",
                                    "investment",
                                ],
                                # F es para referirse al campo amount del modelo Record
                                then=F("record__amount") * Value(-1),
                            ),
                            # ingresos son positivas
                            When(
                                record__typeRecord="income", 
                                then=F("record__amount")
                            ),
                            default=Value(0),
                            output_field=DecimalField(max_digits=15, decimal_places=2),
                        )
                    ),
                    # si no hay registros, devuelve 0
                    Value(
                        0, output_field=DecimalField(max_digits=15, decimal_places=2)
                    ),
                )
            ).order_by("-created_at")
        )
        return accounts

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
