from rest_framework import serializers
from .models import Record
from accounts.models import Account
from categories.models import Category
from currencies.models import Currency
from accounts.serializers import AccountSerializer


class RecordSerializer(serializers.ModelSerializer):
    """Serializer para Record.

    - `user` es read-only (se toma de request.user en la vista).
    - Valida que la `account` pertenezca al usuario autenticado.
    """

    user = serializers.ReadOnlyField(source="user.username")
    account = AccountSerializer(read_only=True) # Mostrar detalles de la cuenta
    account_id = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), write_only=True, source='account') # Asignar cuenta por su PK
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), allow_null=True, required=False
    )
    currency = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Record
        fields = [
            "id",
            "title",
            "description",
            "amount",
            "account",
            "account_id",
            "typeRecord",
            "category",
            "paymentType",
            "currency",
            "date_time",
            "created_at",
            "updated_at",
            "user",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "user"]

    def validate(self, data):
        """Ensure the account belongs to the authenticated user."""
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            account = data.get("account")
            # account may be provided on create/update
            if account and getattr(account, "user", None) != user:
                raise serializers.ValidationError(
                    {"account": "La cuenta debe pertenecer al usuario autenticado."}
                )
        return data
