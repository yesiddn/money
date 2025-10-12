from django.contrib import admin
from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "currency",
        "user",
        "created_at",
        "updated_at",
    )
    list_filter = ("currency", "created_at")
    search_fields = ("user__username", "name", "description")
