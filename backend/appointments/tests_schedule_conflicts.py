"""Interval and authoritative-save policy using synthetic appointment fixtures."""

from datetime import date, datetime, timedelta, timezone as dt_timezone
from zoneinfo import ZoneInfo

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from appointments import tests as legacy_tests
from appointments.models import Appointment
from appointments.schedule_conflicts import (
    find_schedule_conflicts,
    parse_facility_datetime,
)
from facilities.models import AppointmentStatus
from patients.models import Patient


class SchedulingFixtures:
    def setUp(self):
        legacy_tests.AppointmentViewSetTests.setUp(self)
        self.second_patient = Patient.objects.create(
            facility=self.facility,
            first_name="Second",
            last_name="Synthetic",
            date_of_birth=date(1991, 1, 1),
            gender=self.gender,
        )
        self.start = datetime(
            2027, 4, 22, 10, tzinfo=ZoneInfo(str(self.facility.timezone))
        )

    def appointment(self, **changes):
        fields = dict(
            patient=self.patient,
            facility=self.facility,
            appointment_time=self.start,
            end_time=self.start + timedelta(minutes=30),
            resource=self.resource,
            rendering_provider=self.rendering_provider,
            status=self.status,
            appointment_type=self.appointment_type,
            is_billable=False,
        )
        fields.update(changes)
        return Appointment.objects.create(**fields)

    def payload(self, **changes):
        fields = dict(
            patient=self.second_patient.pk,
            appointment_time=self.start.isoformat(),
            end_time=(self.start + timedelta(minutes=30)).isoformat(),
            resource=self.resource.pk,
            rendering_provider=self.rendering_provider.pk,
            status=self.status.pk,
            appointment_type=self.appointment_type.pk,
            is_billable=False,
        )
        fields.update(changes)
        return fields

    def conflicts(self, start=None, end=None, **changes):
        args = dict(
            resource_id=self.resource.pk,
            rendering_provider_id=self.rendering_provider.pk,
        )
        args.update(changes)
        return find_schedule_conflicts(
            self.facility,
            start or self.start,
            end or self.start + timedelta(minutes=30),
            **args,
        )

    def post(self, payload):
        return self.client.post("/v1/appointments/", payload, format="json")


class ScheduleConflictTests(SchedulingFixtures, TestCase):
    def test_half_open_and_containment(self):
        self.appointment()
        for start, end, expected in [
            (30, 60, 0),
            (15, 45, 1),
            (-15, 45, 1),
            (5, 10, 1),
            (-30, 0, 0),
        ]:
            with self.subTest(start=start, end=end):
                result = self.conflicts(
                    self.start + timedelta(minutes=start),
                    self.start + timedelta(minutes=end),
                )
                self.assertEqual(len(result), expected)

    def test_provider_resource_or_null_self_and_facility(self):
        appointment = self.appointment()
        self.assertEqual(len(self.conflicts(resource_id=None)), 1)
        self.assertEqual(len(self.conflicts(rendering_provider_id=None)), 1)
        self.assertEqual(
            self.conflicts(resource_id=None, rendering_provider_id=None), []
        )
        self.assertEqual(self.conflicts(resource_id=-1, rendering_provider_id=-1), [])
        self.assertEqual(self.conflicts(exclude_appointment_id=appointment.pk), [])
        self.assertEqual(
            find_schedule_conflicts(
                self.other_facility,
                self.start,
                self.start + timedelta(minutes=30),
                resource_id=self.resource.pk,
            ),
            [],
        )

    def test_cancelled_only_does_not_occupy(self):
        for code in ("cancelled", "no_show", "completed", "custom"):
            with self.subTest(code=code):
                status, _ = AppointmentStatus.objects.get_or_create(
                    facility=self.facility, code=code, defaults={"name": code}
                )
                appointment = self.appointment(status=status)
                self.assertEqual(len(self.conflicts()), 0 if code == "cancelled" else 1)
                appointment.delete()

    def test_legacy_null_end_and_invalid_end(self):
        appointment = self.appointment()
        Appointment.objects.filter(pk=appointment.pk).update(end_time=None)
        self.assertEqual(len(self.conflicts()), 1)
        Appointment.objects.filter(pk=appointment.pk).update(end_time=self.start)
        with self.assertRaisesMessage(
            ValidationError, "existing schedule interval is invalid"
        ):
            self.conflicts()

    def test_gap_fold_offset_and_midnight(self):
        with self.assertRaises(ValidationError):
            parse_facility_datetime("2027-03-14T02:30", self.facility)
        first = parse_facility_datetime("2027-11-07T01:30", self.facility)
        second = parse_facility_datetime("2027-11-07T01:30-08:00", self.facility)
        self.assertEqual(second - first, timedelta(hours=1))
        self.assertEqual(first.tzinfo, dt_timezone.utc)
        midnight = self.start.replace(hour=0)
        self.appointment(
            appointment_time=midnight - timedelta(minutes=15),
            end_time=midnight + timedelta(minutes=15),
        )
        self.assertEqual(
            len(self.conflicts(midnight, midnight + timedelta(minutes=30))), 1
        )
