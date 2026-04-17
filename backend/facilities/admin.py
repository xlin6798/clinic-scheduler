from django.contrib import admin

from patients.models import Patient
from shared.models import Address

from .models import (
    AppointmentStatus,
    AppointmentType,
    Facility,
    PatientGender,
    Staff,
    StaffRole,
    StaffTitle,
)


class PatientInline(admin.TabularInline):
    model = Patient
    extra = 1
    classes = ["collapse"]


class StaffInline(admin.TabularInline):
    model = Staff
    extra = 1
    classes = ["collapse"]


class StaffRoleInline(admin.TabularInline):
    model = StaffRole
    extra = 0
    classes = ["collapse"]


class StaffTitleInline(admin.TabularInline):
    model = StaffTitle
    extra = 0
    classes = ["collapse"]


class AppointmentStatusInline(admin.TabularInline):
    model = AppointmentStatus
    extra = 0
    classes = ["collapse"]


class AppointmentTypeInline(admin.TabularInline):
    model = AppointmentType
    extra = 0
    classes = ["collapse"]


class PatientGenderInline(admin.TabularInline):
    model = PatientGender
    extra = 0
    classes = ["collapse"]


class AddressInline(admin.StackedInline):
    model = Address
    extra = 0


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "timezone", "created_at")
    search_fields = ("name", "address")
    readonly_fields = ("created_at",)
    inlines = [
        PatientInline,
        StaffInline,
        StaffRoleInline,
        StaffTitleInline,
        AppointmentStatusInline,
        AppointmentTypeInline,
        PatientGenderInline,
    ]
