import uuid
from django.db import models
from patients.models import Patient
from accounts.models import RpmUser
from common.models import TimeStampedModel
from organizations.models import Organization


class CareTeamMembershipStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    SUSPENDED = 'suspended', 'Suspended'


class CareTeamMembership(TimeStampedModel):
    """
    This model corresponds to the CareTeam FHIR resource
    """
    record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, related_name='care_team_memberships', on_delete=models.CASCADE)
    clinician = models.ForeignKey(RpmUser, related_name='care_team_memberships', on_delete=models.CASCADE)
    role = models.CharField(max_length=255, help_text="The role of the member in the care team, corresponds to CareTeam.participant.role")
    status = models.CharField(max_length=255, choices=CareTeamMembershipStatus.choices)
    managing_organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField()
    reason_for_assignment = models.TextField(blank=True, null=True, help_text="Why the care team exists for this patient")

    class Meta:
        db_table = "care_team_membership"
