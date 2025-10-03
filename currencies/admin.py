from django.contrib import admin
from .models import Currency

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "numeric_code", "minor_unit", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    ordering = ("code",)
    readonly_fields = ("code",)