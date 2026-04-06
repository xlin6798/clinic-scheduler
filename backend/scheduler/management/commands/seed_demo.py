from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from scheduler.models import Facility, FacilityMembership


class Command(BaseCommand):
    help = "Seed demo data"

    def handle(self, *args, **kwargs):
        user, _ = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@example.com"},
        )
        user.is_staff = True
        user.is_superuser = True
        user.set_password("Admin123!")
        user.save()

        facility, _ = Facility.objects.get_or_create(name="Demo Clinic")

        FacilityMembership.objects.get_or_create(
            user=user,
            facility=facility,
            role="admin",
        )

        doctor, _ = User.objects.get_or_create(
            username="dr_smith",
            defaults={"email": "drsmith@example.com"},
        )
        doctor.set_password("Doctor123!")
        doctor.save()

        FacilityMembership.objects.get_or_create(
            user=doctor,
            facility=facility,
            role="physician",
            title="md",
        )

        self.stdout.write(self.style.SUCCESS("Demo data created"))