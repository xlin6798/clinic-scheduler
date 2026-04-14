from django.urls import path

from .views import AppointmentDetailView, AppointmentListCreateView

urlpatterns = [
    path(
        "appointments/",
        AppointmentListCreateView.as_view(),
        name="appointment-list-create",
    ),
    path(
        "appointments/<int:pk>/",
        AppointmentDetailView.as_view(),
        name="appointment-detail",
    ),
]
