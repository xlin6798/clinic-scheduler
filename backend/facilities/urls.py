from django.urls import path

from .views import (
    AppointmentStatusListView,
    AppointmentTypeListView,
    PatientGendersView,
    PhysicianListView,
    StaffListView,
)

urlpatterns = [
    path("staffs/", StaffListView.as_view(), name="staff-list"),  # Renamed to staffs
    path("physicians/", PhysicianListView.as_view(), name="physician-list"),
    path(
        "appointment-statuses/",
        AppointmentStatusListView.as_view(),
        name="appointment-status-list",
    ),
    path(
        "appointment-types/",
        AppointmentTypeListView.as_view(),
        name="appointment-type-list",
    ),
    path("patient-genders/", PatientGendersView.as_view(), name="patient-gender-list"),
]
