import uuid
from django.db import models
from common.models import TimeStampedModel
from accounts.models import RpmUser

class Patient(TimeStampedModel):
    class GenderChoices(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"
        UNKNOWN = "unknown", "Unknown"

    record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(RpmUser, related_name='patient', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)
    contact_number = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "patient"


class PatientIdentifier(TimeStampedModel):
    id = models.UUIDField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    system = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    type_code = models.CharField(max_length=255, help_text="Type of the identifier")

    class Meta:
        unique_together = ('system', 'value')
        db_table = "patient_identifier"
