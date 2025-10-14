# categories/admin.py
from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "is_default", "user", "created_at")
    list_filter = ("is_default", "created_at")
    search_fields = ("user__username", "name")
