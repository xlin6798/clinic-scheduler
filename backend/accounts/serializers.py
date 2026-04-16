from rest_framework import serializers

from facilities.models import Staff

from .models import User


class UserSerializer(serializers.ModelSerializer):
    facility = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "last_name",
            "first_name",
            "phone_number",
            "facility",
            "role",
        ]

    def get_facility(self, obj):
        staff_profile = Staff.objects.filter(user=obj, is_active=True).first()
        if staff_profile and staff_profile.facility:
            return {
                "id": staff_profile.facility.id,
                "name": staff_profile.facility.name,
            }
        return None

    def get_role(self, obj):
        staff_profile = Staff.objects.filter(user=obj, is_active=True).first()
        if staff_profile and staff_profile.role:
            return {
                "id": staff_profile.role.id,
                "name": staff_profile.role.name,
                "code": staff_profile.role.code,
            }
        return None


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "last_name",
            "first_name",
            "phone_number",
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone_number=validated_data.get("phone_number", ""),
        )
        return user
