import uuid
from django.db import models
from common.choices import sex_choices
from common.models import TimeStampedModel
from accounts.models import RpmUser

class Patient(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(RpmUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=10)  # Remove choices temporarily
    contact_number = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    raw_fhir_json = models.JSONField(blank=True, null=True)


class PatientIdentifier(TimeStampedModel):
    id = models.UUIDField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    system = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    type_code = models.CharField(max_length=255)


class CareTeamMembership(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    clinician = models.ForeignKey(RpmUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    assigned_at = models.DateTimeField()

