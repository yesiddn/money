from rest_framework import serializers
from categories.serializers import CategorySerializer
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
    account = AccountSerializer(read_only=True)  # Show account details
    account_id = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(),
        write_only=True,
        source="account",
        allow_null=True,
        required=False,
    )  # Assign account by its PK

    # For transfer records
    from_account = AccountSerializer(read_only=True)
    from_account_id = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(),
        write_only=True,
        source="from_account",
        allow_null=True,
        required=False,
    )
    to_account = AccountSerializer(read_only=True)
    to_account_id = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(),
        write_only=True,
        source="to_account",
        allow_null=True,
        required=False,
    )

    category = CategorySerializer(read_only=True)  # Show category details
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source="category",
        allow_null=True,
        required=False,
    )
    currency = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(), required=True
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
            "from_account",
            "from_account_id",
            "to_account",
            "to_account_id",
            "typeRecord",
            "category",
            "category_id",
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
            from_account = data.get("from_account")
            to_account = data.get("to_account")
            type_record = data.get("typeRecord")

            # For transfer records, require from_account and to_account
            if type_record == "transfer":
                if not from_account or not to_account:
                    raise serializers.ValidationError(
                        {
                            "typeRecord": "Para transferencias, se requieren from_account_id y to_account_id."
                        }
                    )
                if from_account == to_account:
                    raise serializers.ValidationError(
                        {
                            "to_account": "La cuenta de origen y destino no pueden ser la misma."
                        }
                    )
                # Validate both accounts belong to the user
                if getattr(from_account, "user", None) != user:
                    raise serializers.ValidationError(
                        {
                            "from_account": "La cuenta de origen debe pertenecer al usuario autenticado."
                        }
                    )
                if getattr(to_account, "user", None) != user:
                    raise serializers.ValidationError(
                        {
                            "to_account": "La cuenta de destino debe pertenecer al usuario autenticado."
                        }
                    )
                
                # In transfer records, assign account to None
                if account is not None:
                    data["account"] = None
                    
            else:
                # For non-transfer records, require account
                if not account:
                    raise serializers.ValidationError(
                        {
                            "account": "Se requiere account_id para registros que no son transferencias."
                        }
                    )
                # account may be provided on create/update
                if getattr(account, "user", None) != user:
                    raise serializers.ValidationError(
                        {"account": "La cuenta debe pertenecer al usuario autenticado."}
                    )
        return data
