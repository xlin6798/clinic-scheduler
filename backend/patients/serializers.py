from rest_framework import serializers

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    gender_name = serializers.CharField(source="gender.name", read_only=True)
    gender_code = serializers.CharField(source="gender.code", read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id",
            "facility",
            "last_name",
            "first_name",
            "date_of_birth",
            "gender",
            "gender_name",
            "gender_code",
            "chart_number",
            "is_active",
        ]
        read_only_fields = ["facility", "chart_number"]
