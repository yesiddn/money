from rest_framework import serializers
from .models import Account
from currencies.models import Currency


class AccountSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Account.

    - `user` es read-only (se toma de request.user en la vista).
    - `currency` se representa por su PK (codigo) y es opcional.
    """

    user = serializers.ReadOnlyField(source="user.username")
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())
    balance = serializers.DecimalField(
        max_digits=15, decimal_places=2, required=False, allow_null=True
    )

    class Meta:
        model = Account
        fields = [
            "id",
            "name",
            "description",
            "currency",
            "balance",
            "created_at",
            "updated_at",
            "user",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "user"]

    def get_fields(self):
        fields = super().get_fields()
        # Hacer currency read-only en actualizaciones (no en creación)
        if self.instance is not None:
            fields["currency"].read_only = True
        return fields
