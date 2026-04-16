from django.contrib import admin

from shared.models import Address

from .models import Patient


class AddressInline(admin.StackedInline):
    model = Address
    extra = 0


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "last_name",
        "first_name",
        "date_of_birth",
        "gender",
        "is_active",
    )
    list_filter = ("facility", "gender", "is_active", "created_at")
    search_fields = ("last_name", "first_name", "chart_number")

    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Basic Info",
            {"fields": (("first_name", "last_name"), "date_of_birth", "gender")},
        ),
        ("Clinic Data", {"fields": ("facility", "chart_number", "is_active")}),
    )
