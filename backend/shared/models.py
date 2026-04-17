from django.db import models


class Address(models.Model):
    line_1 = models.CharField(max_length=255)
    line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, default="Queens")
    state = models.CharField(max_length=2, default="NY")
    zip_code = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        unit = f" {self.line_2}" if self.line_2 else ""
        return f"{self.line_1}{unit}, {self.city}, {self.state} {self.zip_code}"
