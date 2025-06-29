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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(RpmUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)
    contact_number = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    raw_fhir_json = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "patient"


class PatientIdentifier(TimeStampedModel):
    id = models.UUIDField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    system = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    type_code = models.CharField(max_length=255)

    class Meta:
        unique_together = ('system', 'value')
        db_table = "patient_identifier"


class CareTeamMembership(TimeStampedModel):
    """
    This model corresponds to the CareTeam FHIR resource
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    clinician = models.ForeignKey(RpmUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=255, help_text="The role of the member in the care team, corresponds to CareTeam.participant.role")
    status = models.CharField(max_length=255)
    assigned_at = models.DateTimeField()

    class Meta:
        db_table = "care_team_membership"

