"""Explicit input and public DTOs for interval checks and advisory sessions."""

from rest_framework import serializers

from facilities.models import FacilityResource, Staff
from shared.serializers import StrictPayloadMixin


class StrictBooleanField(serializers.BooleanField):
    def to_internal_value(self, data):
        if not isinstance(data, bool):
            self.fail("invalid", input=data)
        return data


class BookingCandidateSerializer(StrictPayloadMixin, serializers.Serializer):
    start_time = serializers.CharField()
    end_time = serializers.CharField()
    resource = serializers.IntegerField(min_value=1, allow_null=True, default=None)
    rendering_provider = serializers.IntegerField(
        min_value=1, allow_null=True, default=None
    )

    def validate(self, attrs):
        from .schedule_conflicts import parse_facility_datetime

        facility = self.context["facility"]
        for field in ("start_time", "end_time"):
            attrs[field] = parse_facility_datetime(attrs[field], facility, field)
        if attrs["end_time"] <= attrs["start_time"]:
            raise serializers.ValidationError({"end_time": "End must be after start."})
        for field, model in (
            ("resource", FacilityResource),
            ("rendering_provider", Staff),
        ):
            if (
                attrs[field] is not None
                and not model.objects.filter(
                    pk=attrs[field], facility=facility
                ).exists()
            ):
                raise serializers.ValidationError(
                    {field: "Assignment not found for this facility."}
                )
        return attrs


class ScheduleCheckSerializer(BookingCandidateSerializer):
    appointment_id = serializers.IntegerField(min_value=1, required=False)
    session_id = serializers.UUIDField(required=False)


class BookingHoldAcquireSerializer(BookingCandidateSerializer):
    session_id = serializers.UUIDField()
    revision = serializers.IntegerField(min_value=1)
    take_over = StrictBooleanField(default=False)


class BookingHoldIdentitySerializer(StrictPayloadMixin, serializers.Serializer):
    session_id = serializers.UUIDField()
    revision = serializers.IntegerField(min_value=1)


class BookingCandidateResponseSerializer(serializers.Serializer):
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    resource = serializers.IntegerField(allow_null=True)
    rendering_provider = serializers.IntegerField(allow_null=True)


class BookingHolderSerializer(serializers.Serializer):
    user_name = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()


class BookingConflictSerializer(BookingCandidateResponseSerializer):
    pass


class BookingHoldResponseSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=["available", "active", "occupied", "released", "revoked"]
    )
    session_id = serializers.UUIDField(required=False)
    revision = serializers.IntegerField(required=False)
    candidate = BookingCandidateResponseSerializer(allow_null=True)
    conflicts = BookingConflictSerializer(many=True)
    holders = BookingHolderSerializer(many=True)
