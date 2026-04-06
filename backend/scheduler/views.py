from datetime import datetime

from django.contrib.auth.models import User
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Appointment,
    FacilityMembership,
    AppointmentStatus,
    AppointmentType,
)
from .serializers import (
    AppointmentSerializer,
    CurrentUserSerializer,
    PhysicianSerializer,
    AppointmentStatusSerializer,
    AppointmentTypeSerializer,
)


def get_request_user(request):
    if request.user.is_authenticated:
        return request.user

    if getattr(settings, "DEMO_MODE", False):
        return User.objects.filter(username="admin").first()

    return None


def get_active_membership_for_user(user):
    if not user:
        return None

    return FacilityMembership.objects.filter(
        user=user,
        is_active=True
    ).select_related("facility").first()


@method_decorator(ensure_csrf_cookie, name="dispatch")
class AppointmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = get_request_user(self.request)
        if not user:
            return Appointment.objects.none()

        memberships = FacilityMembership.objects.filter(
            user=user,
            is_active=True
        ).values_list("facility_id", flat=True)

        queryset = Appointment.objects.filter(
            facility_id__in=memberships
        ).select_related(
            "status",
            "appointment_type",
            "facility",
        ).order_by("appointment_time")

        date_str = self.request.query_params.get("date")

        if date_str:
            try:
                selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                queryset = queryset.filter(appointment_time__date=selected_date)
            except ValueError:
                pass

        return queryset

    def perform_create(self, serializer):
        user = get_request_user(self.request)
        if not user:
            raise PermissionDenied("Authentication required.")

        facility = serializer.validated_data.get("facility")
        status = serializer.validated_data.get("status")
        appointment_type = serializer.validated_data.get("appointment_type")

        membership = get_active_membership_for_user(user)

        if not membership or membership.facility_id != facility.id:
            raise PermissionDenied("You do not have access to this facility.")

        if status.facility_id != facility.id:
            raise PermissionDenied("Selected status does not belong to this facility.")

        if appointment_type.facility_id != facility.id:
            raise PermissionDenied("Selected appointment type does not belong to this facility.")

        serializer.save(created_by=user)


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = get_request_user(self.request)
        if not user:
            return Appointment.objects.none()

        memberships = FacilityMembership.objects.filter(
            user=user,
            is_active=True
        ).values_list("facility_id", flat=True)

        return Appointment.objects.filter(
            facility_id__in=memberships
        ).select_related(
            "status",
            "appointment_type",
            "facility",
        )

    def perform_update(self, serializer):
        user = get_request_user(self.request)
        if not user:
            raise PermissionDenied("Authentication required.")

        facility = serializer.validated_data.get("facility", serializer.instance.facility)
        status = serializer.validated_data.get("status", serializer.instance.status)
        appointment_type = serializer.validated_data.get("appointment_type", serializer.instance.appointment_type)

        membership = get_active_membership_for_user(user)

        if not membership or membership.facility_id != facility.id:
            raise PermissionDenied("You do not have access to this facility.")

        if status.facility_id != facility.id:
            raise PermissionDenied("Selected status does not belong to this facility.")

        if appointment_type.facility_id != facility.id:
            raise PermissionDenied("Selected appointment type does not belong to this facility.")

        serializer.save()


class CurrentUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = get_request_user(request)
        if not user:
            return Response({"detail": "Authentication credentials were not provided."}, status=403)

        membership = get_active_membership_for_user(user)

        data = {
            "id": user.id,
            "username": user.username,
            "role": membership.role if membership else None,
            "facility": {
                "id": membership.facility.id,
                "name": membership.facility.name,
            } if membership else None,
        }

        serializer = CurrentUserSerializer(data)
        return Response(serializer.data)


class AppointmentStatusListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = get_request_user(request)
        membership = get_active_membership_for_user(user)

        if not membership:
            return Response([])

        statuses = AppointmentStatus.objects.filter(
            facility=membership.facility,
            is_active=True
        ).order_by("id")

        serializer = AppointmentStatusSerializer(statuses, many=True)
        return Response(serializer.data)


class AppointmentTypeListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = get_request_user(request)
        membership = get_active_membership_for_user(user)

        if not membership:
            return Response([])

        types = AppointmentType.objects.filter(
            facility=membership.facility,
            is_active=True
        ).order_by("id")

        serializer = AppointmentTypeSerializer(types, many=True)
        return Response(serializer.data)


class PhysicianListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = get_request_user(request)
        membership = get_active_membership_for_user(user)

        if not membership:
            return Response([])

        physicians = FacilityMembership.objects.filter(
            facility=membership.facility,
            role="physician",
            is_active=True
        ).select_related("user").order_by(
            "user__last_name",
            "user__first_name",
            "user__username"
        )

        data = [
            {
                "id": physician.user.id,
                "name": physician.user.get_full_name() or physician.user.username,
                "title": physician.title,
            }
            for physician in physicians
        ]

        serializer = PhysicianSerializer(data, many=True)
        return Response(serializer.data)