from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from facilities.models import (
    AppointmentStatus,
    AppointmentType,
    Facility,
    Staff,
    StaffRole,
    StaffTitle,
)
from patients.models import Patient
from scheduler.models import Appointment

try:
    from facilities.models import PatientGender
except ImportError:
    PatientGender = None


User = get_user_model()


DEMO_PATIENTS = [
    {
        "first_name": "John",
        "last_name": "Smith",
        "date_of_birth": "1985-06-15",
        "gender_code": "M",
        "chart_number": "P1001",
    },
    {
        "first_name": "Jane",
        "last_name": "Smith",
        "date_of_birth": "1990-09-22",
        "gender_code": "F",
        "chart_number": "P1002",
    },
    {
        "first_name": "Michael",
        "last_name": "Johnson",
        "date_of_birth": "1978-03-10",
        "gender_code": "M",
        "chart_number": "P1003",
    },
    {
        "first_name": "Emily",
        "last_name": "Davis",
        "date_of_birth": "2001-10-12",
        "gender_code": "F",
        "chart_number": "P1004",
    },
    {
        "first_name": "Daniel",
        "last_name": "Brown",
        "date_of_birth": "1968-11-03",
        "gender_code": "M",
        "chart_number": "P1005",
    },
    {
        "first_name": "Olivia",
        "last_name": "Wilson",
        "date_of_birth": "1995-04-17",
        "gender_code": "F",
        "chart_number": "P1006",
    },
    {
        "first_name": "Ethan",
        "last_name": "Martinez",
        "date_of_birth": "1988-08-29",
        "gender_code": "M",
        "chart_number": "P1007",
    },
    {
        "first_name": "Sophia",
        "last_name": "Anderson",
        "date_of_birth": "1999-01-05",
        "gender_code": "F",
        "chart_number": "P1008",
    },
    {
        "first_name": "William",
        "last_name": "Thomas",
        "date_of_birth": "1973-07-19",
        "gender_code": "M",
        "chart_number": "P1009",
    },
    {
        "first_name": "Ava",
        "last_name": "Jackson",
        "date_of_birth": "2004-02-27",
        "gender_code": "F",
        "chart_number": "P1010",
    },
    {
        "first_name": "Lucas",
        "last_name": "White",
        "date_of_birth": "1982-12-08",
        "gender_code": "M",
        "chart_number": "P1011",
    },
    {
        "first_name": "Mia",
        "last_name": "Harris",
        "date_of_birth": "1997-05-30",
        "gender_code": "F",
        "chart_number": "P1012",
    },
]


class Command(BaseCommand):
    help = "Seed demo data for the clinic scheduler"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-appointments",
            action="store_true",
            help="Delete existing appointments in the demo facility before reseeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")

        facility = self._seed_users_and_facility()
        self._ensure_patient_genders(facility)
        patients = self._seed_patients(facility)
        self._seed_appointments(facility, patients, reset_appointments=options["reset_appointments"])

        self.stdout.write(self.style.SUCCESS("Successfully seeded Demo Clinic data"))

    def _seed_users_and_facility(self):
        # 1. Admin user
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "first_name": "System",
                "last_name": "Admin",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        admin_user.set_password("Admin123!")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        # 2. Facility
        facility, _ = Facility.objects.get_or_create(
            name="Demo Clinic",
            defaults={"address": "123 Main St, New York, NY"},
        )
        facility.save()

        # 3. Roles / titles seeded by facility logic
        admin_role = StaffRole.objects.filter(facility=facility, code="admin").first()
        physician_role = StaffRole.objects.filter(facility=facility, code="physician").first()
        md_title = StaffTitle.objects.filter(facility=facility, code="md").first()

        if not admin_role or not physician_role:
            raise RuntimeError("Required demo roles were not found.")

        admin_role.is_active = True
        admin_role.save()

        physician_role.is_active = True
        physician_role.save()

        if md_title:
            md_title.is_active = True
            md_title.save()

        # 4. Admin staff link
        Staff.objects.get_or_create(
            user=admin_user,
            facility=facility,
            defaults={"role": admin_role},
        )

        # 5. Physician 1
        doctor_user, _ = User.objects.get_or_create(
            username="dr_smith",
            defaults={
                "email": "drsmith@example.com",
                "first_name": "John",
                "last_name": "Smith",
            },
        )
        doctor_user.set_password("Doctor123!")
        doctor_user.save()

        Staff.objects.get_or_create(
            user=doctor_user,
            facility=facility,
            defaults={
                "role": physician_role,
                "title": md_title,
            },
        )

        # 6. Physician 2
        doctor_user_2, _ = User.objects.get_or_create(
            username="dr_lee",
            defaults={
                "email": "drlee@example.com",
                "first_name": "Sarah",
                "last_name": "Lee",
            },
        )
        doctor_user_2.set_password("Doctor123!")
        doctor_user_2.save()

        Staff.objects.get_or_create(
            user=doctor_user_2,
            facility=facility,
            defaults={
                "role": physician_role,
                "title": md_title,
            },
        )

        return facility

    def _ensure_patient_genders(self, facility):
        if PatientGender is None:
            return

        defaults = [
            {"code": "M", "name": "Male", "sort_order": 1},
            {"code": "F", "name": "Female", "sort_order": 2},
            {"code": "O", "name": "Other", "sort_order": 3},
            {"code": "U", "name": "Unknown", "sort_order": 4},
        ]

        for item in defaults:
            gender_obj, created = PatientGender.objects.get_or_create(
                facility=facility,
                code=item["code"],
                defaults={
                    "name": item["name"],
                    "sort_order": item["sort_order"],
                    "is_active": True,
                },
            )
            if not created:
                updated = False
                if hasattr(gender_obj, "name") and gender_obj.name != item["name"]:
                    gender_obj.name = item["name"]
                    updated = True
                if hasattr(gender_obj, "sort_order") and gender_obj.sort_order != item["sort_order"]:
                    gender_obj.sort_order = item["sort_order"]
                    updated = True
                if hasattr(gender_obj, "is_active") and not gender_obj.is_active:
                    gender_obj.is_active = True
                    updated = True
                if updated:
                    gender_obj.save()

    def _build_gender_value(self, facility, gender_code):
        gender_field = Patient._meta.get_field("gender")

        # CharField version
        if not getattr(gender_field, "is_relation", False):
            return gender_code

        # FK version
        if PatientGender is None:
            raise RuntimeError("Patient.gender is relational but PatientGender model was not found.")

        gender_obj = PatientGender.objects.filter(
            facility=facility,
            code=gender_code,
            is_active=True,
        ).first()

        if not gender_obj:
            raise RuntimeError(f"PatientGender with code '{gender_code}' not found for facility '{facility.name}'.")

        return gender_obj

    def _seed_patients(self, facility):
        patients_by_chart = {}

        for item in DEMO_PATIENTS:
            patient_defaults = {
                "gender": self._build_gender_value(facility, item["gender_code"]),
                "chart_number": item["chart_number"],
                "is_active": True,
            }

            patient, created = Patient.objects.get_or_create(
                facility=facility,
                first_name=item["first_name"],
                last_name=item["last_name"],
                date_of_birth=item["date_of_birth"],
                defaults=patient_defaults,
            )

            updated = False

            if not created:
                if patient.chart_number != item["chart_number"]:
                    patient.chart_number = item["chart_number"]
                    updated = True

                desired_gender = self._build_gender_value(facility, item["gender_code"])
                if patient.gender != desired_gender:
                    patient.gender = desired_gender
                    updated = True

                if hasattr(patient, "is_active") and not patient.is_active:
                    patient.is_active = True
                    updated = True

                if updated:
                    patient.save()

            patients_by_chart[item["chart_number"]] = patient

        self.stdout.write(f"Seeded {len(patients_by_chart)} demo patients.")
        return patients_by_chart

    def _seed_appointments(self, facility, patients, reset_appointments=False):
        if reset_appointments:
            Appointment.objects.filter(facility=facility).delete()

        physicians = list(
            Staff.objects.filter(
                facility=facility,
                role__code="physician",
                role__is_active=True,
                is_active=True,
            )
            .select_related("user")
            .order_by("user__last_name", "user__first_name")
        )

        if not physicians:
            raise RuntimeError("No physicians found for demo appointments.")

        doctor_names = [p.user.get_full_name() or p.user.username for p in physicians]

        status_lookup = {
            obj.code: obj
            for obj in AppointmentStatus.objects.filter(facility=facility, is_active=True)
        }
        type_lookup = {
            obj.code: obj
            for obj in AppointmentType.objects.filter(facility=facility, is_active=True)
        }

        fallback_status = next(iter(status_lookup.values()), None)
        fallback_type = next(iter(type_lookup.values()), None)

        if not fallback_status or not fallback_type:
            raise RuntimeError("Facility is missing appointment statuses or types.")

        today = timezone.localdate()
        morning = timezone.make_aware(
            timezone.datetime.combine(today, timezone.datetime.min.time())
        )

        appointment_specs = [
            {
                "chart": "P1001",
                "day_offset": 0,
                "hour": 9,
                "minute": 0,
                "doctor_index": 0,
                "reason": "Annual physical",
                "status_code": "pending",
                "type_code": "annual",
            },
            {
                "chart": "P1002",
                "day_offset": 0,
                "hour": 9,
                "minute": 30,
                "doctor_index": 1,
                "reason": "Follow-up blood pressure",
                "status_code": "check_in",
                "type_code": "follow_up",
            },
            {
                "chart": "P1003",
                "day_offset": 0,
                "hour": 10,
                "minute": 0,
                "doctor_index": 0,
                "reason": "New patient consult",
                "status_code": "pending",
                "type_code": "new_patient",
            },
            {
                "chart": "P1004",
                "day_offset": 0,
                "hour": 11,
                "minute": 0,
                "doctor_index": 1,
                "reason": "Lab review",
                "status_code": "check_out",
                "type_code": "follow_up",
            },
            {
                "chart": "P1005",
                "day_offset": 1,
                "hour": 9,
                "minute": 15,
                "doctor_index": 0,
                "reason": "Diabetes management",
                "status_code": "pending",
                "type_code": "follow_up",
            },
            {
                "chart": "P1006",
                "day_offset": 1,
                "hour": 10,
                "minute": 15,
                "doctor_index": 1,
                "reason": "Preventive screening",
                "status_code": "pending",
                "type_code": "annual",
            },
            {
                "chart": "P1007",
                "day_offset": 1,
                "hour": 11,
                "minute": 30,
                "doctor_index": 0,
                "reason": "Migraine evaluation",
                "status_code": "pending",
                "type_code": "consult",
            },
            {
                "chart": "P1008",
                "day_offset": 2,
                "hour": 9,
                "minute": 0,
                "doctor_index": 1,
                "reason": "Asthma follow-up",
                "status_code": "check_in",
                "type_code": "follow_up",
            },
            {
                "chart": "P1009",
                "day_offset": 2,
                "hour": 10,
                "minute": 0,
                "doctor_index": 0,
                "reason": "Chest discomfort consult",
                "status_code": "pending",
                "type_code": "consult",
            },
            {
                "chart": "P1010",
                "day_offset": 2,
                "hour": 10,
                "minute": 45,
                "doctor_index": 1,
                "reason": "School physical",
                "status_code": "pending",
                "type_code": "annual",
            },
            {
                "chart": "P1011",
                "day_offset": 3,
                "hour": 9,
                "minute": 30,
                "doctor_index": 0,
                "reason": "Medication refill review",
                "status_code": "check_out",
                "type_code": "follow_up",
            },
            {
                "chart": "P1012",
                "day_offset": 3,
                "hour": 11,
                "minute": 15,
                "doctor_index": 1,
                "reason": "New patient intake",
                "status_code": "pending",
                "type_code": "new_patient",
            },
        ]

        created_count = 0

        for spec in appointment_specs:
            patient = patients.get(spec["chart"])
            if not patient:
                continue

            appointment_dt = morning + timedelta(
                days=spec["day_offset"],
                hours=spec["hour"],
                minutes=spec["minute"],
            )

            status_obj = status_lookup.get(spec["status_code"], fallback_status)
            type_obj = type_lookup.get(spec["type_code"], fallback_type)
            doctor_name = doctor_names[spec["doctor_index"] % len(doctor_names)]

            _, created = Appointment.objects.get_or_create(
                facility=facility,
                patient=patient,
                appointment_time=appointment_dt,
                defaults={
                    "doctor_name": doctor_name,
                    "reason": spec["reason"],
                    "status": status_obj,
                    "appointment_type": type_obj,
                },
            )

            if created:
                created_count += 1

        self.stdout.write(f"Seeded {created_count} demo appointments.")