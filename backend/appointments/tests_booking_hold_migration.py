"""Prove the interval table is additive and reversible on an isolated test DB."""

from datetime import timedelta
from uuid import uuid4

from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils import timezone

from . import tests as appointment_test_fixtures
from .models import Appointment, AppointmentSlotHold


class BookingHoldMigrationTests(TransactionTestCase):
    migrate_from = [
        (
            "appointments",
            "0016_appointmentslothold_uniq_slot_hold_facility_null_resource_start",
        )
    ]
    migrate_to = [("appointments", "0017_appointmentbookinghold")]

    def test_apply_reverse_reapply_preserves_legacy_rows_and_constraints(self):
        self.assertEqual(connection.vendor, "postgresql")
        appointment_test_fixtures.AppointmentViewSetTests.setUp(self)
        start = timezone.now()
        appointment = Appointment.objects.create(
            facility=self.facility,
            patient=self.patient,
            appointment_time=start,
            end_time=None,
            status=self.status,
            appointment_type=self.appointment_type,
        )
        # Current save() fills a missing end; preserve an actual legacy null.
        Appointment.objects.filter(pk=appointment.pk).update(end_time=None)
        legacy = AppointmentSlotHold.objects.create(
            facility=self.facility,
            resource=self.resource,
            start_time=start,
            user=self.user,
        )
        null_legacy = AppointmentSlotHold.objects.create(
            facility=self.facility, resource=None, start_time=start, user=self.user
        )
        expected = (appointment.pk, legacy.pk, null_legacy.pk)
        try:
            for target in (
                self.migrate_from,
                self.migrate_to,
                self.migrate_from,
                self.migrate_to,
            ):
                executor = MigrationExecutor(connection)
                executor.migrate(target)
                apps = executor.loader.project_state(target).apps
                OldAppointment = apps.get_model("appointments", "Appointment")
                OldSlotHold = apps.get_model("appointments", "AppointmentSlotHold")
                self.assertIsNone(OldAppointment.objects.get(pk=expected[0]).end_time)
                self.assertEqual(
                    set(OldSlotHold.objects.values_list("pk", flat=True)),
                    set(expected[1:]),
                )
                for resource_id in (self.resource.pk, None):
                    with self.assertRaises(IntegrityError), transaction.atomic():
                        OldSlotHold.objects.create(
                            facility_id=self.facility.pk,
                            resource_id=resource_id,
                            start_time=start,
                        )
                if target == self.migrate_to:
                    Hold = apps.get_model("appointments", "AppointmentBookingHold")
                    Hold.objects.create(
                        session_id=uuid4(),
                        facility_id=self.facility.pk,
                        revision=1,
                        state="released",
                    )
                    for start_time, end_time in (
                        (None, None),
                        (start, start),
                        (start, start - timedelta(minutes=1)),
                    ):
                        with self.assertRaises(IntegrityError), transaction.atomic():
                            Hold.objects.create(
                                session_id=uuid4(),
                                facility_id=self.facility.pk,
                                revision=1,
                                state="active",
                                start_time=start_time,
                                end_time=end_time,
                            )
                    Hold.objects.create(
                        session_id=uuid4(),
                        facility_id=self.facility.pk,
                        revision=1,
                        state="active",
                        start_time=start,
                        end_time=start + timedelta(minutes=1),
                    )
        finally:
            MigrationExecutor(connection).migrate(self.migrate_to)
