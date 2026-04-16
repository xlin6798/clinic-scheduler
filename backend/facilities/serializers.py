from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    AppointmentStatus,
    AppointmentType,
    Facility,
    Staff,
    StaffRole,
    StaffTitle,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class StaffSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)
    title_name = serializers.CharField(
        source="title.name", read_only=True, allow_null=True
    )

    class Meta:
        model = Staff
        fields = ["id", "user", "role_name", "title_name", "is_active"]


class FacilitySerializer(serializers.ModelSerializer):
    timezone = serializers.SerializerMethodField()

    class Meta:
        model = Facility
        fields = ["id", "name"]

    def get_timezone(self, obj):
        return str(obj.timezone)


class AppointmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentStatus
        fields = "__all__"


class AppointmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentType
        fields = "__all__"


class StaffRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffRole
        fields = "__all__"


class StaffTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffTitle
        fields = "__all__"
