from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from facilities.models import (
    AppointmentStatus,
    AppointmentType,
    Facility,
    PatientGender,
    Staff,
    StaffRole,
    StaffTitle,
)
from patients.models import Patient, PatientPhone
from scheduler.models import Appointment
from shared.models import Address

User = get_user_model()

DEMO_PATIENTS = [
    {
        "last_name": "Smith",
        "first_name": "John",
        "date_of_birth": "1985-06-15",
        "gender_code": "male",
        "chart_number": "P1001",
    },
    {
        "last_name": "Smith",
        "first_name": "Jane",
        "date_of_birth": "1990-09-22",
        "gender_code": "female",
        "chart_number": "P1002",
    },
    {
        "last_name": "Johnson",
        "first_name": "Michael",
        "date_of_birth": "1978-03-10",
        "gender_code": "male",
        "chart_number": "P1003",
    },
    {
        "last_name": "Davis",
        "first_name": "Emily",
        "date_of_birth": "2001-10-12",
        "gender_code": "female",
        "chart_number": "P1004",
    },
    {
        "last_name": "Brown",
        "first_name": "Daniel",
        "date_of_birth": "1968-11-03",
        "gender_code": "male",
        "chart_number": "P1005",
    },
    {
        "last_name": "Wilson",
        "first_name": "Olivia",
        "date_of_birth": "1995-04-17",
        "gender_code": "female",
        "chart_number": "P1006",
    },
    {
        "last_name": "Martinez",
        "first_name": "Ethan",
        "date_of_birth": "1988-08-29",
        "gender_code": "male",
        "chart_number": "P1007",
    },
    {
        "last_name": "Anderson",
        "first_name": "Sophia",
        "date_of_birth": "1999-01-05",
        "gender_code": "female",
        "chart_number": "P1008",
    },
    {
        "last_name": "Thomas",
        "first_name": "William",
        "date_of_birth": "1973-07-19",
        "gender_code": "male",
        "chart_number": "P1009",
    },
    {
        "last_name": "Jackson",
        "first_name": "Ava",
        "date_of_birth": "2004-02-27",
        "gender_code": "female",
        "chart_number": "P1010",
    },
    {
        "last_name": "White",
        "first_name": "Lucas",
        "date_of_birth": "1982-12-08",
        "gender_code": "male",
        "chart_number": "P1011",
    },
    {
        "last_name": "Harris",
        "first_name": "Mia",
        "date_of_birth": "1997-05-30",
        "gender_code": "female",
        "chart_number": "P1012",
    },
]


class Command(BaseCommand):
    help = "Seed demo data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-appointments",
            action="store_true",
            help="Delete existing appointments for the demo facility before reseeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        facility = self._seed_users_and_facility()
        self._ensure_patient_genders(facility)
        patients = self._seed_patients(facility)
        self._seed_appointments(
            facility,
            patients,
            reset_appointments=options["reset_appointments"],
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded Demo Clinic data"))

    def _seed_users_and_facility(self):
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "first_name": "System",
                "last_name": "Admin",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin_user.set_password("Admin123!")
            admin_user.save()

        facility_address, _ = Address.objects.get_or_create(
            line_1="123 Main St",
            city="New York",
            state="NY",
            zip_code="10001",
            defaults={"line_2": ""},
        )

        facility, _ = Facility.objects.get_or_create(
            name="Demo Clinic",
            defaults={"address": facility_address},
        )

        physician_role = StaffRole.objects.get(facility=facility, code="physician")
        md_title = StaffTitle.objects.get(facility=facility, code="md")

        demo_doctors = [
            ("dr_smith", "John", "Smith"),
            ("dr_lee", "Sarah", "Lee"),
        ]

        for username, first_name, last_name in demo_doctors:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": f"{username}@example.com",
                },
            )
            if created:
                user.set_password("Admin123!")
                user.save()

            Staff.objects.get_or_create(
                user=user,
                facility=facility,
                defaults={
                    "role": physician_role,
                    "title": md_title,
                    "is_active": True,
                },
            )

        return facility

    def _ensure_patient_genders(self, facility):
        required_genders = [
            ("male", "Male", 1),
            ("female", "Female", 2),
            ("other", "Other", 3),
            ("unknown", "Unknown", 4),
        ]

        for code, name, sort_order in required_genders:
            PatientGender.objects.get_or_create(
                facility=facility,
                code=code,
                defaults={
                    "name": name,
                    "sort_order": sort_order,
                    "is_active": True,
                },
            )

    def _build_gender_value(self, facility, gender_code):
        return PatientGender.objects.get(facility=facility, code=gender_code)

    def _seed_patients(self, facility):
        patients_by_chart = {}

        for item in DEMO_PATIENTS:
            patient_address, _ = Address.objects.get_or_create(
                line_1=f"{item['chart_number']} Wellness Way",
                city="Queens",
                state="NY",
                zip_code="11427",
                defaults={"line_2": ""},
            )

            patient, created = Patient.objects.get_or_create(
                facility=facility,
                first_name=item["first_name"],
                last_name=item["last_name"],
                date_of_birth=item["date_of_birth"],
                defaults={
                    "gender": self._build_gender_value(facility, item["gender_code"]),
                    "chart_number": item["chart_number"],
                    "address": patient_address,
                    "is_active": True,
                },
            )

            if not created:
                updated = False

                expected_gender = self._build_gender_value(
                    facility, item["gender_code"]
                )
                if patient.gender_id != expected_gender.id:
                    patient.gender = expected_gender
                    updated = True

                if patient.chart_number != item["chart_number"]:
                    patient.chart_number = item["chart_number"]
                    updated = True

                if patient.address_id != patient_address.id:
                    patient.address = patient_address
                    updated = True

                if not patient.is_active:
                    patient.is_active = True
                    updated = True

                if updated:
                    patient.save()

            PatientPhone.objects.get_or_create(
                patient=patient,
                number="718-555-0199",
                label="cell",
                defaults={"is_primary": True},
            )

            patients_by_chart[item["chart_number"]] = patient

        return patients_by_chart

    def _seed_appointments(self, facility, patients, reset_appointments=False):
        if reset_appointments:
            Appointment.objects.filter(facility=facility).delete()

        physicians = list(
            Staff.objects.filter(
                facility=facility,
                role__code="physician",
                is_active=True,
            ).select_related("user")
        )
        if not physicians:
            raise RuntimeError("No physician staff members found for demo seeding.")

        doctor_names = [
            f"{staff.user.last_name}, {staff.user.first_name}" for staff in physicians
        ]

        status = AppointmentStatus.objects.get(
            facility=facility,
            code="pending",
        )
        appointment_type = AppointmentType.objects.get(
            facility=facility,
            code="annual",
        )

        today = timezone.localdate()
        start_of_day = timezone.make_aware(datetime.combine(today, datetime.min.time()))

        for index, (chart_number, patient) in enumerate(list(patients.items())[:5]):
            Appointment.objects.get_or_create(
                facility=facility,
                patient=patient,
                appointment_time=start_of_day + timedelta(hours=9 + index),
                defaults={
                    "doctor_name": doctor_names[index % len(doctor_names)],
                    "reason": "Routine checkup",
                    "status": status,
                    "appointment_type": appointment_type,
                },
            )
