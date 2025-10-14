from django.contrib import admin
from .models import Record


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "amount",
        "account",
        "typeRecord",
        "category",
        "paymentType",
        "currency",
        "created_at",
    )
    list_filter = ("typeRecord", "paymentType", "currency", "created_at")
    search_fields = ("user__username", "title", "description")
    readonly_fields = ("created_at", "updated_at")
