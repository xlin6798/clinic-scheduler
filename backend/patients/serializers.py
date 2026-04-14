from rest_framework import serializers

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    gender_name = serializers.CharField(source="gender.name", read_only=True)
    gender_code = serializers.CharField(source="gender.code", read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id",
            "facility",
            "first_name",
            "last_name",
            "full_name",
            "display_name",
            "date_of_birth",
            "gender",
            "gender_name",
            "gender_code",
            "chart_number",
            "is_active",
        ]
        read_only_fields = ["facility", "chart_number"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_display_name(self, obj):
        return f"{obj.last_name}, {obj.first_name}".strip()
