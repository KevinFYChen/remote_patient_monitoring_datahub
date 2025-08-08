from django.db import models
from patients.models import Patient
from accounts.models import RpmUser
from common.models import TimeStampedModel
import uuid


class Organization(TimeStampedModel):
    """
    This model corresponds to the Organization FHIR resource
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=255, blank=True, null=True)
    raw_fhir_json = models.JSONField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    organization_type = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "organization"


class CareTeamMembership(TimeStampedModel):
    """
    This model corresponds to the CareTeam FHIR resource
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    clinician = models.ForeignKey(RpmUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=255, help_text="The role of the member in the care team, corresponds to CareTeam.participant.role")
    status = models.CharField(max_length=255)
    managing_organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField()
    reason_for_assignment = models.TextField(blank=True, null=True, help_text="Why the care team exists for this patient")

    class Meta:
        db_table = "care_team_membership"
