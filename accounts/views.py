from decimal import Decimal

from django.db.models import DecimalField, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from rest_framework import permissions, viewsets

from .models import Account
from .serializers import AccountSerializer

# Constantes para el cálculo de balance
ZERO_DECIMAL = Value(0, output_field=DecimalField(max_digits=15, decimal_places=2))


def _subquery_income():
    """Subquery para sumar ingresos de una cuenta."""
    from records.models import Record

    return Subquery(
        Record.objects.filter(
            account=OuterRef("pk"),
            typeRecord="income",
        )
        .values("account")
        .annotate(total=Sum("amount"))
        .values("total")[:1]
    )


def _subquery_expenses_and_investments():
    """Subquery para sumar gastos e inversiones de una cuenta."""
    from records.models import Record

    return Subquery(
        Record.objects.filter(
            account=OuterRef("pk"),
            typeRecord__in=["expense", "investment"],
        )
        .values("account")
        .annotate(total=Sum("amount"))
        .values("total")[:1]
    )


def _subquery_transfers_received():
    """Subquery para sumar transferencias recibidas (to_account)."""
    from records.models import Record

    return Subquery(
        Record.objects.filter(
            to_account=OuterRef("pk"),
            typeRecord="transfer",
        )
        .values("to_account")
        .annotate(total=Sum("amount"))
        .values("total")[:1]
    )


def _subquery_transfers_sent():
    """Subquery para sumar transferencias enviadas (from_account)."""
    from records.models import Record

    return Subquery(
        Record.objects.filter(
            from_account=OuterRef("pk"),
            typeRecord="transfer",
        )
        .values("from_account")
        .annotate(total=Sum("amount"))
        .values("total")[:1]
    )


def annotate_balance(queryset):
    """Anota el balance calculado a un queryset de Account.

    Balance = Ingresos - (Gastos + Inversiones) + Transferencias recibidas - Transferencias enviadas

    Para transferencias:
    - Las transferencias salientes (from_account) reducen el balance
    - Las transferencias entrantes (to_account) aumentan el balance

    Nota:
    - Los registros de tipo income, expense, investment usan el campo 'account'
    - Los registros de tipo transfer usan 'from_account' y 'to_account'
    """
    income = Coalesce(_subquery_income(), ZERO_DECIMAL)
    expenses = Coalesce(_subquery_expenses_and_investments(), ZERO_DECIMAL)
    transfers_in = Coalesce(_subquery_transfers_received(), ZERO_DECIMAL)
    transfers_out = Coalesce(_subquery_transfers_sent(), ZERO_DECIMAL)

    result = queryset.annotate(balance=income - expenses + transfers_in - transfers_out).order_by("created_at")
    return result


def create_balance_adjustment_record(user, account, amount):
    """Crea un registro de ajuste de balance.

    Args:
        user: Usuario propietario del registro
        account: Cuenta a la que se asocia el ajuste
        amount: Monto del ajuste (positivo para income, negativo para expense)
    """
    from records.models import Record

    if amount == Decimal("0"):
        return

    type_record = "income" if amount > 0 else "expense"
    Record.objects.create(
        user=user,
        title="Ajuste de balance",
        description="",
        amount=abs(amount),
        account=account,
        typeRecord=type_record,
        category=None,
        paymentType="cash",
        currency=account.currency,
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
        # Extraer el balance de los datos validados
        balance = serializer.validated_data.pop("balance", None)

        # Crear la cuenta
        account = serializer.save(user=self.request.user)

        # Si se proporcionó un balance, crear un registro de ajuste
        if balance is not None:
            create_balance_adjustment_record(self.request.user, account, balance)

        # Anotar el balance en la instancia para que se incluya en la respuesta
        account_with_balance = annotate_balance(
            Account.objects.filter(id=account.id)
        ).first()

        # Actualizar la instancia del serializer con el balance calculado
        if account_with_balance:
            account.balance = account_with_balance.balance
            serializer.instance = account

    def perform_update(self, serializer):
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
            create_balance_adjustment_record(self.request.user, account, difference)

        # Recalcular el balance para incluirlo en la respuesta
        account_with_balance = annotate_balance(
            Account.objects.filter(id=account.id)
        ).first()

        # Actualizar la instancia del serializer con el balance calculado
        if account_with_balance:
            account.balance = account_with_balance.balance
            serializer.instance = account
