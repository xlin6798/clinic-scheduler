from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    AppointmentStatus,
    AppointmentType,
    Staff,
    StaffRole,
    StaffTitle,
)
from .serializers import (
    AppointmentStatusSerializer,
    AppointmentTypeSerializer,
    StaffRoleSerializer,
    StaffSerializer,
    StaffTitleSerializer,
)


def get_request_user(request):
    if request.user.is_authenticated:
        return request.user

    if getattr(settings, "DEMO_MODE", False):
        User = get_user_model()
        return User.objects.filter(username="admin").first()

    return None


def get_active_staff_profile(user):
    if not user:
        return None

    return (
        Staff.objects.filter(user=user, is_active=True)
        .select_related("facility", "role", "title")
        .first()
    )


class StaffListView(generics.ListAPIView):
    serializer_class = StaffSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = get_request_user(self.request)
        profile = get_active_staff_profile(user)

        if not profile:
            return Staff.objects.none()

        return (
            Staff.objects.filter(facility=profile.facility)
            .select_related("user", "role", "title")
            .order_by("user__last_name")
        )


class PhysicianListView(generics.ListAPIView):
    serializer_class = StaffSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = get_request_user(self.request)
        profile = get_active_staff_profile(user)

        if not profile:
            return Staff.objects.none()

        return Staff.objects.filter(
            facility=profile.facility,
            role__code="physician",
            is_active=True,
        ).select_related("user", "title")


class AppointmentStatusListView(generics.ListAPIView):
    serializer_class = AppointmentStatusSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = get_request_user(self.request)
        profile = get_active_staff_profile(user)

        if not profile:
            return AppointmentStatus.objects.none()

        return AppointmentStatus.objects.filter(
            facility=profile.facility,
            is_active=True,
        ).order_by("id")


class AppointmentTypeListView(generics.ListAPIView):
    serializer_class = AppointmentTypeSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = get_request_user(self.request)
        profile = get_active_staff_profile(user)

        if not profile:
            return AppointmentType.objects.none()

        return AppointmentType.objects.filter(
            facility=profile.facility,
            is_active=True,
        ).order_by("id")


class StaffRoleListView(generics.ListAPIView):
    serializer_class = StaffRoleSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = get_request_user(self.request)
        profile = get_active_staff_profile(user)

        if not profile:
            return StaffRole.objects.none()

        return StaffRole.objects.filter(
            facility=profile.facility,
            is_active=True,
        ).order_by("id")


class StaffTitleListView(generics.ListAPIView):
    serializer_class = StaffTitleSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = get_request_user(self.request)
        profile = get_active_staff_profile(user)

        if not profile:
            return StaffTitle.objects.none()

        return StaffTitle.objects.filter(
            facility=profile.facility,
            is_active=True,
        ).order_by("id")


class PatientGendersView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = get_request_user(request)
        profile = get_active_staff_profile(user)

        if not profile:
            raise PermissionDenied("Authentication required.")

        genders = profile.facility.patient_genders.filter(is_active=True)

        return Response(
            [
                {
                    "id": gender.id,
                    "code": gender.code,
                    "name": gender.name,
                }
                for gender in genders
            ]
        )
