from django.db import models

from facilities.models import Facility


class PatientPhone(models.Model):
    PHONE_TYPES = [
        ("cell", "Cell"),
        ("home", "Home"),
        ("work", "Work"),
    ]

    patient = models.ForeignKey(
        "Patient", on_delete=models.CASCADE, related_name="phones"
    )
    number = models.CharField(max_length=20)
    label = models.CharField(max_length=10, choices=PHONE_TYPES, default="cell")
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_label_display()}: {self.number}"


class Patient(models.Model):
    facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, related_name="patients"
    )
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.ForeignKey(
        "facilities.PatientGender", on_delete=models.PROTECT, related_name="patients"
    )

    chart_number = models.CharField(max_length=50, blank=True, null=True)

    address = models.OneToOneField(
        "shared.Address", on_delete=models.SET_NULL, null=True, related_name="patient"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("facility", "first_name", "last_name", "date_of_birth")
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"
