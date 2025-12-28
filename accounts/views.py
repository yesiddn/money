from decimal import Decimal

from django.db.models import DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce
from rest_framework import permissions, viewsets

from .models import Account
from .serializers import AccountSerializer


def annotate_balance(queryset):
    """Anota el balance calculado a un queryset de Account.

    Balance = Ingresos - (Gastos + Transferencias + Inversiones)
    """
    return queryset.annotate(
        balance=Coalesce(
            Sum("record__amount", filter=Q(record__typeRecord="income")),
            Value(0, output_field=DecimalField(max_digits=15, decimal_places=2)),
        )
        - Coalesce(
            Sum(
                "record__amount",
                filter=Q(record__typeRecord__in=["expense", "transfer", "investment"]),
            ),
            Value(0, output_field=DecimalField(max_digits=15, decimal_places=2)),
        )
    )


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
        return annotate_balance(Account.objects.filter(user=user))

    def perform_create(self, serializer):
        from records.models import Record

        # Extraer el balance de los datos validados
        balance = serializer.validated_data.pop("balance", None)

        # Crear la cuenta
        account = serializer.save(user=self.request.user)

        # Si se proporcionó un balance, crear un registro de ajuste
        if balance is not None and balance != Decimal("0"):
            if balance > 0:
                # Balance positivo: crear registro de income
                Record.objects.create(
                    user=self.request.user,
                    title="Ajuste de balance",
                    description="",
                    amount=abs(balance),
                    account=account,
                    typeRecord="income",
                    category=None,
                    paymentType="cash",
                    currency=account.currency,
                )
            else:
                # Balance negativo: crear registro de expense
                Record.objects.create(
                    user=self.request.user,
                    title="Ajuste de balance",
                    description="",
                    amount=abs(balance),
                    account=account,
                    typeRecord="expense",
                    category=None,
                    paymentType="cash",
                    currency=account.currency,
                )

        # Anotar el balance en la instancia para que se incluya en la respuesta
        account_with_balance = annotate_balance(
            Account.objects.filter(id=account.id)
        ).first()

        # Actualizar la instancia del serializer con el balance calculado
        if account_with_balance:
            account.balance = account_with_balance.balance
            serializer.instance = account

    def perform_update(self, serializer):
        from records.models import Record

        # Obtener el balance enviado por el usuario
        new_balance = serializer.validated_data.pop("balance", None)

        # Obtener la cuenta actual con su balance
        account = self.get_object()
        account_with_balance = annotate_balance(
            Account.objects.filter(id=account.id)
        ).first()
        current_balance = (
            account_with_balance.balance if account_with_balance else Decimal("0")
        )

        # Actualizar la cuenta
        account = serializer.save()

        # Si se proporcionó un balance y es diferente al actual, crear un registro de ajuste
        if new_balance is not None and new_balance != current_balance:
            difference = new_balance - current_balance

            if difference > 0:
                # Diferencia positiva: crear registro de income
                Record.objects.create(
                    user=self.request.user,
                    title="Ajuste de balance",
                    description="",
                    amount=abs(difference),
                    account=account,
                    typeRecord="income",
                    category=None,
                    paymentType="cash",
                    currency=account.currency,
                )
            else:
                # Diferencia negativa: crear registro de expense
                Record.objects.create(
                    user=self.request.user,
                    title="Ajuste de balance",
                    description="",
                    amount=abs(difference),
                    account=account,
                    typeRecord="expense",
                    category=None,
                    paymentType="cash",
                    currency=account.currency,
                )

        # Recalcular el balance para incluirlo en la respuesta
        account_with_balance = annotate_balance(
            Account.objects.filter(id=account.id)
        ).first()

        # Actualizar la instancia del serializer con el balance calculado
        if account_with_balance:
            account.balance = account_with_balance.balance
            serializer.instance = account
