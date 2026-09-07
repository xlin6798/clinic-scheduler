"""Facility-local interval policy shared by appointment and presence endpoints."""

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone as dt_timezone

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.exceptions import APIException, ValidationError

from facilities.models import Facility

from .models import Appointment
from .services import get_facility_timezone


@contextmanager
def facility_schedule_lock(facility):
    """Serialize schedule writes before acquiring patient/appointment/slot locks.

    NO KEY UPDATE allows foreign-key checks by concurrent encounter creation;
    ordinary FOR UPDATE can deadlock against its existing appointment lock.
    """
    with transaction.atomic():
        Facility.objects.select_for_update(of=("self",), no_key=True).get(
            pk=facility.pk
        )
        yield


def parse_facility_datetime(value, facility, field_name="start_time"):
    parsed = value if isinstance(value, datetime) else None
    if isinstance(value, str):
        try:
            parsed = parse_datetime(value)
        except ValueError:
            pass
    if parsed is None:
        raise ValidationError({field_name: "Use an ISO datetime."})
    facility_tz = get_facility_timezone(facility)
    if timezone.is_naive(parsed):
        # Preserve the existing first-occurrence interpretation during a fold.
        local = parsed.replace(tzinfo=facility_tz, fold=0)
        if (
            local.astimezone(dt_timezone.utc)
            .astimezone(facility_tz)
            .replace(tzinfo=None)
            != parsed
        ):
            raise ValidationError(
                {field_name: "This local time does not exist in the facility timezone."}
            )
        parsed = local
    return parsed.astimezone(dt_timezone.utc)


def normalize_interval(start_time, end_time, appointment_type=None):
    if start_time is None or timezone.is_naive(start_time):
        raise ValidationError({"start_time": "An aware start time is required."})
    if end_time is None:
        duration = getattr(appointment_type, "duration_minutes", None)
        if not duration or duration <= 0:
            raise ValidationError(
                {"end_time": "A valid appointment duration is required."}
            )
        end_time = start_time + timedelta(minutes=duration)
    if timezone.is_naive(end_time) or end_time <= start_time:
        raise ValidationError({"end_time": "End time must be after start time."})
    return start_time.astimezone(dt_timezone.utc), end_time.astimezone(dt_timezone.utc)


def occupies_schedule(status):
    return getattr(status, "code", None) != "cancelled"


def find_schedule_conflicts(
    facility,
    start_time,
    end_time,
    resource_id=None,
    rendering_provider_id=None,
    exclude_appointment_id=None,
):
    start_time, end_time = normalize_interval(start_time, end_time)
    assignments = Q(pk__in=[])
    if resource_id is not None:
        assignments |= Q(resource_id=resource_id)
    if rendering_provider_id is not None:
        assignments |= Q(rendering_provider_id=rendering_provider_id)
    if resource_id is None and rendering_provider_id is None:
        return []
    # Do not filter on stored end_time: legacy null ends must participate.
    appointments = (
        Appointment.objects.filter(assignments, facility=facility)
        .exclude(status__code="cancelled")
        .select_related("appointment_type")
        .order_by("appointment_time", "pk")
    )
    if exclude_appointment_id is not None:
        appointments = appointments.exclude(pk=exclude_appointment_id)
    conflicts = []
    for appointment in appointments.iterator():
        try:
            existing_start, existing_end = normalize_interval(
                appointment.appointment_time,
                appointment.end_time,
                appointment.appointment_type,
            )
        except ValidationError:
            raise ValidationError(
                {
                    "detail": "An existing schedule interval is invalid. Contact the office to correct it."
                }
            ) from None
        if existing_start < end_time and existing_end > start_time:
            if len(conflicts) < 20:
                conflicts.append(
                    {
                        "start_time": existing_start.isoformat(),
                        "end_time": existing_end.isoformat(),
                        "resource": (
                            resource_id
                            if resource_id == appointment.resource_id
                            else None
                        ),
                        "rendering_provider": (
                            rendering_provider_id
                            if rendering_provider_id
                            == appointment.rendering_provider_id
                            else None
                        ),
                    }
                )
    return conflicts


class ScheduleOverlap(APIException):
    status_code = 409
    default_code = "schedule_overlap"

    def __init__(self, conflicts):
        # Keep numeric assignment IDs numeric rather than coercing every leaf to
        # ErrorDetail, as APIException's generic initializer would do.
        self.detail = {
            "code": "schedule_overlap",
            "detail": "This time overlaps another appointment.",
            "conflicts": conflicts,
        }


def validate_schedule_save(validated_data, instance=None, allow_overlap=False):
    def value(field):
        return validated_data.get(field, getattr(instance, field, None))

    status = value("status")
    if not occupies_schedule(status):
        return
    start, end = normalize_interval(
        value("appointment_time"), value("end_time"), value("appointment_type")
    )
    resource = value("resource")
    provider = value("rendering_provider")
    resource_id = resource.pk if resource else None
    provider_id = provider.pk if provider else None
    if instance is not None and occupies_schedule(instance.status):
        old_start, old_end = normalize_interval(
            instance.appointment_time, instance.end_time, instance.appointment_type
        )
        if (start, end, resource_id, provider_id) == (
            old_start,
            old_end,
            instance.resource_id,
            instance.rendering_provider_id,
        ):
            return
    conflicts = find_schedule_conflicts(
        value("facility"),
        start,
        end,
        resource_id=resource_id,
        rendering_provider_id=provider_id,
        exclude_appointment_id=instance.pk if instance else None,
    )
    if conflicts and not allow_overlap:
        raise ScheduleOverlap(conflicts)
