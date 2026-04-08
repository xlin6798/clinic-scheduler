from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "patient_display",
        "doctor_name",
        "appointment_time",
        "facility",
        "status",
        "appointment_type",
    )

    list_filter = (
        "status",
        "appointment_type",
        "facility",
        "appointment_time",
    )

    search_fields = (
        "patient__first_name",
        "patient__last_name",
        "doctor_name",
        "reason",
    )

    readonly_fields = ("created_at", "created_by_name")

    fieldsets = (
        ("Primary Information", {
            "fields": (("patient", "doctor_name"), "facility")
        }),
        ("Schedule & Logistics", {
            "fields": ("appointment_time", "appointment_type", "status", "reason")
        }),
        ("System Logs", {
            "classes": ("collapse",),
            "fields": ("created_by", "created_by_name", "created_at")
        }),
    )

    def patient_display(self, obj):
        return f"{obj.patient.last_name}, {obj.patient.first_name}"

    patient_display.short_description = "Patient"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)