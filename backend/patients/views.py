from django.db import models
from rest_framework import generics, permissions

from facilities.views import get_request_user, get_active_staff_profile
from .models import Patient
from .serializers import PatientSerializer


class PatientListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = get_request_user(self.request)
        profile = get_active_staff_profile(user)

        if not profile:
            return Patient.objects.none()

        base_queryset = Patient.objects.filter(
            facility=profile.facility,
            is_active=True
        )

        quick_search = (self.request.query_params.get("search") or "").strip()
        name = (self.request.query_params.get("name") or "").strip()
        date_of_birth = (self.request.query_params.get("date_of_birth") or "").strip()
        chart_number = (self.request.query_params.get("chart_number") or "").strip()

        # QUICK SEARCH MODE
        if quick_search:
            queryset = base_queryset

            if "," in quick_search:
                last, first = [s.strip() for s in quick_search.split(",", 1)]
                queryset = queryset.filter(
                    last_name__icontains=last,
                    first_name__icontains=first,
                )
            else:
                queryset = queryset.filter(
                    last_name__icontains=quick_search
                )

            return queryset.order_by("last_name", "first_name")

        # DETAILED SEARCH MODE
        if not name and not date_of_birth and not chart_number:
            return Patient.objects.none()

        queryset = base_queryset

        if name:
            if "," in name:
                last, first = [s.strip() for s in name.split(",", 1)]
                queryset = queryset.filter(
                    last_name__icontains=last,
                    first_name__icontains=first,
                )
            else:
                queryset = queryset.filter(
                    last_name__icontains=name
                )

        if date_of_birth:
            queryset = queryset.filter(date_of_birth=date_of_birth)

        if chart_number:
            queryset = queryset.filter(chart_number__icontains=chart_number)

        return queryset.order_by("last_name", "first_name")

    def perform_create(self, serializer):
        user = get_request_user(self.request)
        profile = get_active_staff_profile(user)

        if profile:
            serializer.save(facility=profile.facility)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = get_request_user(self.request)
        profile = get_active_staff_profile(user)

        if not profile:
            return Patient.objects.none()

        return Patient.objects.filter(facility=profile.facility)