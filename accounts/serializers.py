from rest_framework import serializers
from .models import Account
from currencies.models import Currency


class AccountSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Account.

    - `user` es read-only (se toma de request.user en la vista).
    - `currency` se representa por su PK (codigo) y es opcional.
    """

    user = serializers.ReadOnlyField(source="user.username")
    currency = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Account
        fields = [
            "id",
            "name",
            "description",
            "currency",
            "created_at",
            "updated_at",
            "user",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "user"]
