"""Facility-serialized advisory interval sessions, independent of saved visits."""

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from facilities.security import user_has_facility_permission

from .booking_hold_serializers import (
    BookingHoldAcquireSerializer,
    BookingHoldIdentitySerializer,
    BookingHoldResponseSerializer,
    ScheduleCheckSerializer,
)
from .models import APPOINTMENT_SLOT_HOLD_TIMEOUT, AppointmentBookingHold
from .schedule_conflicts import facility_schedule_lock, find_schedule_conflicts
from .services import get_user_display_name


class BookingHoldSchema(AutoSchema):
    def _get_request_body(self, direction="request"):
        body = super()._get_request_body(direction)
        # Heartbeat is a complete identity command, not a partial model update.
        if self.method == "PATCH" and body:
            body["required"] = True
        return body


def _candidate(data):
    return {
        field: data[field]
        for field in ("start_time", "end_time", "resource", "rendering_provider")
    }


def _stored_candidate(hold):
    if not hold.start_time or not hold.end_time:
        return None
    return {
        "start_time": hold.start_time,
        "end_time": hold.end_time,
        "resource": hold.resource_id,
        "rendering_provider": hold.rendering_provider_id,
    }


def _overlapping_holds(facility, candidate, session_id=None):
    assignments = Q(pk__in=[])
    if candidate["resource"] is not None:
        assignments |= Q(resource_id=candidate["resource"])
    if candidate["rendering_provider"] is not None:
        assignments |= Q(rendering_provider_id=candidate["rendering_provider"])
    holds = AppointmentBookingHold.objects.filter(
        assignments,
        facility=facility,
        state="active",
        last_seen_at__gte=timezone.now() - APPOINTMENT_SLOT_HOLD_TIMEOUT,
        start_time__lt=candidate["end_time"],
        end_time__gt=candidate["start_time"],
    )
    if session_id:
        holds = holds.exclude(session_id=session_id)
    return holds.order_by("start_time", "pk")


def _response(
    facility, candidate, *, hold=None, status=None, exclude_appointment_id=None
):
    holders = (
        list(_overlapping_holds(facility, candidate, hold.session_id if hold else None))
        if candidate
        else []
    )
    conflicts = (
        find_schedule_conflicts(
            facility,
            candidate["start_time"],
            candidate["end_time"],
            resource_id=candidate["resource"],
            rendering_provider_id=candidate["rendering_provider"],
            exclude_appointment_id=exclude_appointment_id,
        )
        if candidate
        else []
    )
    result = {
        "status": status or ("occupied" if holders else "available"),
        "candidate": candidate,
        "conflicts": conflicts,
        "holders": [
            {
                "user_name": item.user_display_name or "Unknown user",
                "start_time": item.start_time,
                "end_time": item.end_time,
            }
            for item in holders
        ],
    }
    if hold:
        result.update(session_id=hold.session_id, revision=hold.revision)
    return Response(result)


class BookingHoldMixin:
    def _require_booking_permission(self, facility, permission="schedule.create"):
        if not user_has_facility_permission(self.request.user, facility.id, permission):
            raise PermissionDenied("You do not have access to schedule appointments.")

    def _owned_booking_hold(self, facility, session_id):
        # Check globally because session UUID uniqueness spans facilities. Never
        # disclose the owner, facility, or candidate of an inaccessible session.
        hold = AppointmentBookingHold.objects.filter(session_id=session_id).first()
        if hold and (
            hold.facility_id != facility.id or hold.user_id != self.request.user.id
        ):
            raise PermissionDenied("Booking session is not accessible.")
        return hold

    @extend_schema(
        request=ScheduleCheckSerializer, responses={200: BookingHoldResponseSerializer}
    )
    @action(detail=False, methods=["post"], url_path="schedule-check")
    def schedule_check(self, request):
        facility = self.get_facility()
        serializer = ScheduleCheckSerializer(
            data=request.data, context={"facility": facility}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        appointment_id = data.get("appointment_id")
        self._require_booking_permission(
            facility, "schedule.update" if appointment_id else "schedule.create"
        )
        if (
            appointment_id
            and not self.get_queryset().filter(pk=appointment_id).exists()
        ):
            raise PermissionDenied("Appointment is not accessible.")
        hold = (
            self._owned_booking_hold(facility, data["session_id"])
            if data.get("session_id")
            else None
        )
        response = _response(
            facility, _candidate(data), hold=hold, exclude_appointment_id=appointment_id
        )
        response.data.pop("session_id", None)
        response.data.pop("revision", None)
        return response

    @extend_schema(
        methods=["POST"],
        request=BookingHoldAcquireSerializer,
        responses={200: BookingHoldResponseSerializer},
    )
    @extend_schema(
        methods=["PATCH"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "format": "uuid"},
                    "revision": {"type": "integer", "minimum": 1},
                },
                "required": ["session_id", "revision"],
            },
        },
        responses={200: BookingHoldResponseSerializer},
    )
    @extend_schema(
        methods=["DELETE"],
        request=None,
        parameters=[
            OpenApiParameter(
                "session_id", type={"type": "string", "format": "uuid"}, required=True
            ),
            OpenApiParameter("revision", type=int, required=True),
        ],
        responses={200: BookingHoldResponseSerializer},
    )
    @action(
        detail=False,
        methods=["post", "patch", "delete"],
        url_path="booking-hold",
        schema=BookingHoldSchema(),
    )
    def booking_hold(self, request):
        facility = self.get_facility()
        self._require_booking_permission(facility)
        serializer_class = (
            BookingHoldAcquireSerializer
            if request.method == "POST"
            else BookingHoldIdentitySerializer
        )
        payload = (
            request.data
            if request.method != "DELETE"
            else {
                key: request.query_params[key]
                for key in ("session_id", "revision")
                if key in request.query_params
            }
        )
        serializer = serializer_class(data=payload, context={"facility": facility})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        with facility_schedule_lock(facility):
            hold = self._owned_booking_hold(facility, data["session_id"])
            if hold and hold.state == "active" and not hold.is_active():
                hold.state = "revoked"
                hold.save(update_fields=["state"])
            if request.method == "PATCH":
                return self._heartbeat_booking_hold(facility, hold, data)
            if hold and (
                hold.state in ("released", "revoked")
                or data["revision"] <= hold.revision
            ):
                return self._booking_state(facility, hold)
            if not hold:
                # A malicious UUID collision across facilities uses different
                # facility mutexes, so the unique insert still needs a savepoint.
                try:
                    with transaction.atomic():
                        hold = AppointmentBookingHold.objects.create(
                            facility=facility,
                            user=request.user,
                            session_id=data["session_id"],
                            revision=data["revision"],
                            user_display_name=get_user_display_name(request.user),
                        )
                except IntegrityError:
                    hold = self._owned_booking_hold(facility, data["session_id"])
                    if hold is None:
                        raise
                    return self._booking_state(facility, hold)
            hold.revision = data["revision"]
            if request.method == "DELETE":
                hold.state = "released"
                hold.save(update_fields=["state", "revision"])
                return self._booking_state(facility, hold)
            return self._acquire_booking_hold(facility, hold, data)

    def _booking_state(self, facility, hold):
        state = hold.state
        if state == "active" and not hold.is_active():
            state = "revoked"
        if state in ("released", "revoked"):
            return Response(
                {
                    "status": state,
                    "session_id": hold.session_id,
                    "revision": hold.revision,
                    "candidate": _stored_candidate(hold),
                    "conflicts": [],
                    "holders": [],
                }
            )
        return _response(
            facility,
            _stored_candidate(hold),
            hold=hold,
            status=state if state != "inactive" else None,
        )

    def _heartbeat_booking_hold(self, facility, hold, data):
        if not hold:
            return Response(
                {
                    "status": "revoked",
                    "session_id": data["session_id"],
                    "revision": data["revision"],
                    "candidate": None,
                    "conflicts": [],
                    "holders": [],
                }
            )
        if hold.is_active() and hold.revision == data["revision"]:
            hold.last_seen_at = timezone.now()
            hold.save(update_fields=["last_seen_at"])
        elif hold.state == "active" and not hold.is_active():
            hold.state = "revoked"
            hold.save(update_fields=["state"])
        return self._booking_state(facility, hold)

    def _acquire_booking_hold(self, facility, hold, data):
        candidate = _candidate(data)
        others = _overlapping_holds(facility, candidate, hold.session_id)
        occupied = others.exists()
        if occupied and data["take_over"]:
            others.update(state="revoked")
            occupied = False
        hold.start_time = candidate["start_time"]
        hold.end_time = candidate["end_time"]
        hold.resource_id = candidate["resource"]
        hold.rendering_provider_id = candidate["rendering_provider"]
        hold.state = "inactive" if occupied else "active"
        hold.last_seen_at = timezone.now()
        hold.save()
        return _response(
            facility, candidate, hold=hold, status="occupied" if occupied else "active"
        )
