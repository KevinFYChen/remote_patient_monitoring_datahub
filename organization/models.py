import uuid
from django.db import models
from common.models import TimeStampedModel
from accounts.models import RpmUser

ORGANIZATION_MEMBERSHIP_ROLE_CHOICES = [
    ("admin", "Organization Admin"),
    ("member", "Member")
]

ORGANIZATION_MEMBERSHIP_STATUS_CHOICES = [
    ("active", "Active"),
    ("inactive", "Inactive"),
    ('pending', 'Pending'),
    ('suspended', 'Suspended')
]

CLINICIAN_INVITATION = [
    ('pending', 'Pending'),
    ('expired', 'Expired'),
    ('accepted', 'Accepted'),
    ('revoked', 'Revoked')
]

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


class OrganizationMembership(TimeStampedModel):
    """
    Specifies the membership of an organization
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        RpmUser, 
        on_delete=models.CASCADE,
        related_name='organization_memberships',
        related_query_name='organization_membership'
    ) # A user can have multiple memberships.
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=255, choices=ORGANIZATION_MEMBERSHIP_ROLE_CHOICES)
    status = models.CharField(max_length=255, choices=ORGANIZATION_MEMBERSHIP_STATUS_CHOICES)
    approved_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey(
        RpmUser, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='approved_organization_memberships',
        related_query_name='approved_organization_membership'
    )

    class Meta:
        db_table = "organization_membership"
        unique_together = ('user', 'organization')
        permissions = [
            ('is_organization_admin', 'Can invite clinicians to the organization')
        ]


class ClinicianInvitation(TimeStampedModel):
    """
    A resource that represents an invitation to create an account for a clinician in an organization
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expires_at = models.DateTimeField()
    clinician_email = models.EmailField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    invited_by = models.ForeignKey(RpmUser, on_delete=models.CASCADE) # A user can receive multiple invitations.
    invitation_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=255, choices=CLINICIAN_INVITATION)

    class Meta:
        db_table = "clinician_organization_account_invitation"



